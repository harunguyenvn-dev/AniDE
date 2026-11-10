# AniDE Glass cho Waybar

`anide-glass` là một style **tùy chọn** cho các layout Waybar có nhóm pill/leaf.
Nó kế thừa màu từ theme/Wallbash và styles HyDE, không thay layout hoặc theme
hiện tại. Vùng trong suốt chỉ được blur nếu Hyprland và cấu hình của bạn hỗ trợ;
màu sắc thực tế phụ thuộc theme. Một số layout không dùng nhóm này sẽ không
hiển thị các tấm kính.

Sau khi triển khai dotfiles bằng cách thông thường, chạy:

```sh
hyde-shell waybar --select-style
```

Chọn `anide-glass.css`. Để quay lại, chạy lại lệnh và chọn style trước đó;
file `~/.config/waybar/user-style.css` vẫn có thể ghi đè style. Style được cài
vào `${XDG_DATA_HOME:-$HOME/.local/share}/waybar/styles/` qua manifest Waybar
hiện có. Không cần Quickshell hay dependency mới.

Style chưa được xác minh trên một phiên Wayland trong môi trường phát triển này;
nếu GTK báo lỗi stylesheet, chọn lại style cũ và báo phiên bản Waybar/GTK.

## Layout AniDE Glass

Để dùng bố cục đồng bộ (ứng dụng và workspace bên trái, nhạc và đồng hồ ở
chính giữa, theme/hình nền và trạng thái hệ thống bên phải), chọn layout
`anide-glass` từ:

```sh
hyde-shell waybar --select-layout
```

Tên layout khớp tên style nên bộ chọn Waybar tự ghép `anide-glass.css`, trừ
khi bạn có style cùng tên trong thư mục cấu hình người dùng được ưu tiên hơn.
Layout lấy định nghĩa các module còn lại từ includes do `waybar.py` tạo. Chọn
lại layout trước đó trong cùng menu để quay lại. Phát/dừng và chuyển bài cần
`playerctl`; không có trình phát MPRIS thì vùng nhạc có thể trống. Các biểu tượng
cần font Nerd Font của cấu hình hiện tại. Layout này hiện là thanh phía trên,
không phải triển khai bố cục bốn cạnh.
