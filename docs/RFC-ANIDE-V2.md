# RFC: AniDE v2 — làm đẹp stack hiện tại

**Trạng thái:** định hướng được sửa theo quyết định của người dùng, 2026-11-10.
**Không thêm Quickshell.** AniDE giữ Waybar, Rofi, Dunst/SwayNC, Wlogout và
các công cụ hiện có; SekaiPop và dots-hyprland chỉ là nguồn cảm hứng về bố cục,
tương tác, an toàn cài đặt và tổ chức mã. Không sao chép nguyên giao diện.
Các ý tưởng chưa được triển khai dưới đây không phải tính năng đã có.

## Khảo sát và giới hạn

Khảo sát tĩnh AniDE `fa2fd57afc7203b1b5653d3271f3a57ea3873f97`,
[SekaiPop `19cc45a`](https://github.com/Blapples/SekaiPop/tree/19cc45ae11934e121133a64fa0846b799f018c59),
và [dots-hyprland `cb1c428`](https://github.com/end-4/dots-hyprland/tree/cb1c428bf841dabccff1b126904047c28e89ba8c).
Chưa test trên phiên desktop thực; submodule `tests` và `language-packs` chưa
được khởi tạo. Ba repo có LICENSE GPL-3.0; tài sản/font/theme/phụ thuộc có thể
có giấy phép riêng. Không vendor mã hoặc asset từ hai repo tham khảo.

* `Configs/.local/share/hypr/hyde.lua` là entrypoint managed, load modules,
  `monitors`, user `hyprland`, rồi workflow; `Configs/.config/hypr/hyprland.lua`
  là user entrypoint được preserve. `Scripts/dots/hyprland.toml` sync module
  managed. Không sinh `hyprland.conf`; `.conf` cho hyprlock/hypridle là hợp lệ.
* `lua/variables.lua` và `start_up.lua` chạy Waybar và Dunst; keybinds và
  dispatcher còn gọi `hyde-shell`, Waybar và Rofi. Giữ aliases, không thay
  startup hay cài notification server thứ hai.
* `theme.switch.sh` → `wallpaper.sh` → Wallbash/`color.set.sh`; template
  `Configs/.local/share/wallbash/` tạo palette, bao gồm
  `$XDG_STATE_HOME/hyde/lua_state/colors.lua`. `theme.patch.sh` và
  `Scripts/themepatcher.lst` là một phần hệ sinh thái theme; không thay thế.
* Waybar dùng layouts/modules/styles tại `Configs/.local/share/waybar/` và
  `waybar.py` sinh file style với Wallbash, `theme.css` và `user-style.css`.
  User overrides được giữ; style mới phải tự chọn, không ghi đè layout cũ.
  Layer rule Hyprland đã có blur cho `waybar` và `rofi`; mức blur thực tế vẫn
  phụ thuộc compositor, theme và cấu hình người dùng.
* SekaiPop có bar/dock, media, settings, plugin và installer tách layer trong
  `sekaipop/modules/`, `services/`, `docs/PLUGINS.md`, `install.sh`. end-4
  có launcher, AI, overview, matugen và diagnostics trong
  `dots/.config/quickshell/ii/`, `dots/.config/matugen/`, `diagnose`.
  Đây là tham khảo UX, **không** phải đề xuất đưa runtime của họ vào AniDE.
* `Scripts/install.sh -r` / `--restore` hiện là deploy lại, không phải khôi
  phục backup. `-t` không bảo đảm read-only toàn bộ: `install_pst.sh` có lệnh
  SDDM avatar/xdg-mime không guard; `restore_cfg.sh` có `mkdir` không guard trong
  `hyprland_hook` legacy. Hook này còn tham chiếu nguồn `hyprland.conf` không
  tồn tại; cần xác minh đường gọi trước khi nói nó chạy ở deploy mặc định.
  `install_pre.sh` có nhánh bootloader/pacman; `install_pst.sh` và
  `restore_svc.lst` có thao tác SDDM. Không chạy installer trong khảo sát.
* `flake.nix` hiện đóng gói hydevm, không phải desktop shell; giữ tương thích
  khi bổ sung gói trong tương lai.

## Ma trận thay đổi

| Khu vực | Quyết định | Điều kiện |
|---|---|---|
| Waybar styles/layouts/modules | Thêm style glass tùy chọn; sau đó cải tiến layout và modules | Không ghi đè lựa chọn cũ; dùng màu theme, tương thích bốn cạnh |
| Rofi / Dunst / SwayNC / Wlogout | Cải tiến từng theme, giữ công cụ và cấu hình | Chỉ một notification server, dễ quay lại kiểu cũ |
| Wallbash, themepatcher, theme, Kitty/GTK/Qt/editor | Giữ pipeline | Kiểm thử theme sáng/tối và đồng bộ cross-app, không thay nguồn màu |
| Hyprland Lua / animations / workflows / shaders | Giữ `hyde.lua` và user config; cải thiện an toàn và tương tác | Không đụng custom/monitors của user, không tạo Hyprland `.conf` |
| `hyde-shell` và command wrappers | Giữ tương thích; xem xét alias `anide-shell` | Không đổi hành vi CLI cũ âm thầm |
| Installer/diagnose | Thiết kế plan/apply, backup và kiểm tra read-only | Bảo vệ bootloader/SDDM, kiểm thử trong HOME tạm và VM |
| Quickshell, QML, matugen | Không thêm | Không có dependency mới cho shell |

## Hướng thực hiện

1. **Thẩm mỹ:** style Waybar glass mới là opt-in; dùng `@main-bg`, `@main-fg`,
   `@wb-act-bg` và `@wb-hvr-bg` từ theme hiện có. Bề mặt trong suốt, đường
   viền nhẹ và bo góc giữ cá tính AniDE. Thiết kế phải có fallback không blur,
   không ép độ mờ lên mọi theme và không đưa animation nền nặng vào lite.
2. **Tương tác:** tăng chất lượng launcher, media, thông báo, cheatsheet và các
   selector bằng module/CLI sẵn có trước khi thêm công cụ. Ý tưởng live overview,
   AI, desktop edit và plugins phải được đánh giá riêng về công nghệ, bảo mật,
   hiệu năng; không hứa có tính năng tương đương Quickshell.
3. **Lua và profile:** giữ luồng load hiện tại và tương thích kho theme HyDE;
   chỉ thêm loader `custom/` sau test thứ tự và bảo vệ update. Chế độ lite nếu
   làm sẽ dùng stack cũ với hiệu ứng giảm, không tạo profile Quickshell.
4. **An toàn:** phân biệt `-r` deploy hiện hữu với lệnh restore backup mới;
   dry-run không ghi file, sudo hay đổi service. Bootloader/SDDM phải opt-in
   và xác nhận. Restore cần manifest, preview và kiểm tra path/symlink; không
   hứa hoàn tác package hoặc system tweaks khi chưa có journal tương ứng.
5. **QA:** kiểm thử cấu hình bằng fixtures, syntax, theme sáng/tối, lựa chọn/
   quay lại style, XDG không mặc định và session thật trên nhiều GPU/màn hình.
   Kiểm tra tool sẵn có; ghi rõ test nào chưa thể chạy. `tests/` là submodule,
   dùng vị trí test độc lập thay vì sửa nó khi chưa khởi tạo.

## Việc đầu tiên đã thực hiện

`Configs/.local/share/waybar/styles/anide-glass.css` là style opt-in, kế thừa
styles chung và màu theme. Xem `docs/ANIDE-GLASS.md` để chọn/quay lại. Chưa
được xác nhận trực quan hoặc trên GTK/Waybar runtime tại môi trường khảo sát.
