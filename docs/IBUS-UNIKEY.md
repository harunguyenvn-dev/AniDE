# Gõ tiếng Việt với IBus Unikey

AniDE cài `ibus` và `ibus-unikey` trong nhóm phụ thuộc Arch; `ibus-unikey`
được yêu cầu qua yay/paru trong manifest deez (helper có thể lấy từ repo hoặc
AUR tùy hệ thống). Phiên Hyprland đặt các biến GTK/Qt/XIM và khởi chạy IBus,
không dùng `--replace` để tránh thay thế daemon đang chạy. Với UWSM, các biến
cũng được thiết lập trước khi compositor khởi động. Khởi động lại phiên sau khi
cập nhật để mọi ứng dụng nhận môi trường mới.

**Lần đầu**, mở **AniDE Settings → System → Vietnamese input** hoặc chạy
`ibus-setup`, vào **Input Method → Add → Vietnamese → Unikey**. Chọn Telex/VNI
trong tùy chọn Unikey và cấu hình phím chuyển trong IBus Preferences. AniDE
không tự thay đổi danh sách engine hoặc phím tắt có sẵn của bạn. Kiểm tra bằng
`ibus list-engine | grep -i unikey`; nếu thiếu, kiểm tra gói đã cài rồi đăng
xuất/đăng nhập. IBus-Unikey upstream hiện không còn được hỗ trợ; xem
[upstream](https://github.com/vn-input/ibus-unikey) để biết các lựa chọn khác.

Nếu đã dùng Fcitx hoặc framework khác, các biến `GTK_IM_MODULE`, `QT_IM_MODULE`
và `XMODIFIERS` hiện có được tôn trọng như một nhóm; daemon không tự chạy khi
phát hiện Fcitx. Nếu Fcitx khởi chạy mà không khai báo các biến toolkit,
hãy tắt mặc định IBus để tránh trỏ ứng dụng tới IBus trong khi daemon không chạy.
Để chủ động tắt tích hợp AniDE, đặt
`ANIDE_INPUT_METHOD=none` **trước khi đăng nhập** (ví dụ trong cấu hình môi
trường UWSM cá nhân, chẳng hạn `~/.config/uwsm/env`, trước snippet
`10-anide-input.sh`), rồi đăng xuất/đăng nhập; dùng cấu hình framework khác của
bạn như bình thường. Với phiên không dùng UWSM, đặt biến trước khi chạy
Hyprland. Không đổi cấu hình `.conf` của Hyprland.

IBus hoạt động qua IM module GTK/Qt và XIM cho XWayland; hành vi có thể khác
nhau theo ứng dụng, đặc biệt ứng dụng Electron/Wayland native. Kiểm tra trong
GTK, Qt và XWayland trên hệ thống của bạn. Tích hợp này chưa được kiểm thử trên
một phiên Hyprland thực tế trong môi trường phát triển.
