# Brainstorm: animation mới cho profile README

Ngày: 2026-10-13 · Trạng thái: **đã duyệt thiết kế**, chưa implement

## Vấn đề / yêu cầu
- Profile README pixel-art (PICO-8, lưới 4px, font bitmap 5x7) đã có header động (sao, mây, sao băng, đuôi mèo, bubble icon), heading tĩnh, footer nhấp nháy.
- Muốn thêm animation "xịn thật sự" mà không biến profile thành cây thông Noel.
- Phần lệch tông/generic nhất hiện tại: snake (Platane/snk, profile nào cũng có), stats card bên thứ 3.

## Ràng buộc kỹ thuật (GitHub README)
- SVG render qua `<img>` + camo proxy: không JS, không hover/click trong SVG, không font/ảnh ngoài. Chỉ CSS keyframes + SMIL.
- Tương tác duy nhất = link bọc ảnh (vd mở issue).
- SVG không biết giờ người xem → mọi thứ "live" phải do Action regenerate.
- Animate SVG filter (feTurbulence, blur) trên ảnh 1200px → tốn CPU, trang giật. Giữ pixel + `crispEdges` + `steps()`.
- GitHub mobile có thể chỉ hiện frame đầu → frame mặc định phải đầy đủ nội dung.

## Các phương án đã cân nhắc
| # | Ý tưởng | Wow | Effort | Kết luận |
|---|---|---|---|---|
| 1 | Contribution Platformer thay snake | ★★★★★ | L | **Chọn làm hero** |
| 2 | Header sống theo giờ VN + thời tiết (Open-Meteo) | ★★★★★ | M | Bỏ: cần cron mỗi giờ, chuyển header sang branch output |
| 3 | RPG Character Sheet thay stats cards | ★★★★ | M | Để giai đoạn 2 |
| 4 | "Insert coin" thật qua issue + Hall of Fame | ★★★★ | M | Để sau (rủi ro spam/rác issue) |
| 5 | About dialogue box typewriter | ★★★ | S–M | Chọn (polish) |
| 6 | Micro-polish heading/header/footer | ★★★ | S | Chọn (polish) |

Level design cho platformer:
- **A. Địa hình theo tuần (chọn)**: cột cao = số ngày có commit trong tuần (0–7), tuần trống = hố, chuỗi tuần trống dài = cầu gỗ. Đúng chất platformer.
- B. Lưới 7×53 khối "?": quen mắt nhưng chỉ hàng dưới tương tác được, gameplay rời rạc.
- C. Thư viện có sẵn (Pac-Man graph): rẻ nhưng generic, sai palette.

## Giải pháp đã chốt

### 1. Contribution Platformer (`dist/platformer.svg`, thay snake)
- Data: GraphQL `user.contributionsCollection.contributionCalendar` (weeks → days: count, level, date; totalContributions). Token `README_STATS_TOKEN || GITHUB_TOKEN` (snk dùng đúng cách này). Chỉ `urllib`, không dependency.
- Màn chơi: 53 cột tuần, mỗi cột ~5 cell rộng → ~300×70 cell (1200×280px), cảnh đêm cùng palette header.
- Coin lơ lửng trên mỗi cột, màu theo contributionLevel cao nhất tuần đó.
- Dev + mèo (sprite nhìn ngang mới: frame chạy 2–3 + frame nhảy) chạy trái→phải. Mèo theo sau dev.
  - Lên dốc → nhảy, xuống dốc → rơi/nhảy.
  - Apex nhảy = max(h_from, h_to) + 2.
- Cuối màn: cột cờ + "COURSE CLEAR" + "52 WEEKS · N CONTRIBUTIONS" (bù việc mất hình lưới quen thuộc).
- Bộ đếm "COINS 0000" góc trên tăng theo từng cột (mỗi chữ số 1 bộ keyframe).
- Chuyển động:
  - Lấy mẫu vị trí theo frame (~12fps), snap lưới 4px → keyframes `translate` (~200 keyframe, ~7KB). Vòng lặp ~16–18s: chạy ~13s + màn clear.
  - Sprite chạy/nhảy đổi bằng opacity `steps(1)` (giống pattern `frame-a/frame-b` hiện có).
  - Coin: keyframes riêng mỗi cột (53 bộ). Không dùng 1 keyframe chung + delay được, vì coin phải hiện lại khi vòng mới bắt đầu.
- 1 SVG duy nhất (cảnh đêm), bỏ `<picture>` dark/light.

### 2. Polish (asset tĩnh trong `assets/`)
- **Heading icons**: tim đập, rương mở + coin nảy, scroll mở, cúp loé sáng. Động ~0.8s rồi nghỉ ~4s.
- **Header**: đom đóm trên dải cỏ trống, tai mèo thỉnh thoảng giật, laptop của dev loé sáng, mưa sao băng 3 viên ~30s/lần. Tối đa 4 phần tử động mới.
- **Footer**: "CONTINUE? 9…0" đếm ngược → "GAME OVER" → lặp; coin xoay 4 frame.
- **About dialogue** (`assets/about-dialogue.svg`): portrait dev nhìn thẳng (sprite mới), câu chào gõ dần (animate clip width `steps(n)`, font cố định nên dễ), ▼ nhấp nháy. Chỉ câu chào; đoạn HTML giữ nguyên cho select/search/a11y. Có thể cần thêm glyph (vd `—`).

### Nguyên tắc chung
- Style mặc định = trạng thái cuối, đầy đủ nội dung (chữ hiện hết, coin còn). Animation chạy *từ* 0 (`fill-mode: backwards`) → reduced-motion / mobile / renderer tĩnh vẫn đủ thông tin.
- Giữ `@media (prefers-reduced-motion: reduce)` sẵn có trong `document()`.

### 3. Code + workflow
- Tách `Canvas`, `PAL`, `FONT`, `document()`, `layer()` → `scripts/pixel.py` (dùng chung).
- `scripts/build_assets.py`: asset tĩnh, build local, commit vào `assets/`.
- `scripts/build_platformer.py`: chạy trong CI, ghi `dist/platformer.svg`. Cờ `--sample <json>` để preview offline. Thêm fixture mẫu.
- Workflow `profile-assets.yml`:
  - Thay bước `Platane/snk@v3` bằng `actions/setup-python` (hoặc python3 có sẵn trên runner) + `python3 scripts/build_platformer.py`.
  - Bỏ snk → hết vấn đề dist/ do root tạo, có thể bỏ comment về thứ tự bước.
  - Vẫn cron daily.
- README: thay khối `<picture>` snake bằng `<img src=".../output/platformer.svg">`, thêm `about-dialogue.svg` trên đoạn About.

## Rủi ro
- Quỹ đạo nhảy 0→7 cao; nhiều tuần trống liên tiếp → cần cầu, nếu không thì hố quá dài.
- Mất hình lưới snake quen thuộc → bù bằng chú thích tổng số.
- Năm có 53/54 cột hoặc tuần cuối thiếu ngày → layout phải chịu được.
- Total contributions ≥ 5 chữ số → bộ đếm cần đủ chỗ.
- Dung lượng/hiệu năng: ~60 group animate là ổn (snk còn nhiều hơn), nhưng không dùng filter.
- GITHUB_TOKEN chỉ thấy đóng góp public; private cần PAT (đã có secret tùy chọn).

## Tiêu chí thành công
- `platformer.svg` < ~150KB, vòng lặp 16–18s, mượt trên Chrome/Firefox/Safari.
- Bật reduced-motion: tĩnh nhưng đọc được (màn chơi + tổng số + chữ dialogue đầy đủ).
- Build deterministic (cùng data → cùng SVG). `build_assets.py` chạy lại không đổi asset ngoài phần sửa có chủ đích.
- Workflow xanh, branch `output` có `platformer.svg`.
- Frame đầu nhìn vẫn đẹp.

## Bước tiếp theo
1. Phase 1: tách `scripts/pixel.py` (refactor thuần, output byte-identical).
2. Phase 2: platformer: fetch data + fixture, level gen, sprite ngang, timeline/keyframes, coin, counter, course clear.
3. Phase 3: workflow + README swap.
4. Phase 4: polish (heading → footer → header → dialogue).
5. Giai đoạn 2 (sau): RPG Character Sheet; "Insert coin" qua issue.
