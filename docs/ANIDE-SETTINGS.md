# AniDE Settings

AniDE Settings is an optional Qt 6 desktop control hub inspired by the settings
experience of SekaiPop and end-4. It keeps Waybar, Rofi and the existing HyDE
commands; it does not install or require Quickshell.

After deploying the updated dotfiles, launch **AniDE Settings** in your
application launcher, click the settings icon in the optional AniDE Glass bar,
or run:

```sh
hyde-shell anide-settings
```

It requires **PyQt6 for the system Python**. On Arch Linux, install it with
`sudo pacman -S python-pyqt6`. The launcher reports the missing dependency if
it is absent. Other optional tools are checked individually; unavailable
buttons are disabled and show the missing executables. Actions execute existing
programs directly without passing user text through a shell. They may change
settings when you make a selection in those programs; the hub itself does not
write Hyprland configuration or replace your themes.

The first version groups theme/wallpaper, Waybar layout and style, workflows,
shaders, lockscreen, GTK/Qt appearance, night light, audio, network and
Bluetooth. Search filters the current section. It uses simple hex colors from
Waybar's `theme.css` when present, otherwise the Qt platform palette; reopen it
to load a changed theme. Real compositor blur is not assumed.

This is not yet a complete direct-edit Settings app: it does not offer display
position editing, idle timers, blur/rounding sliders or plugin management.
Animation selection is deliberately not exposed yet: the existing animation
selector also writes a legacy `animations.conf`, so its Lua migration must be
resolved before it is safely surfaced here. External utilities manage their own
configuration and errors; starting one does not mean it successfully applied a
change. Existing tools and user configuration remain intact.
