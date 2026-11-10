#!/usr/bin/env bash
# Start IBus without replacing another daemon or selecting an engine for the user.
set -u
case ${ANIDE_INPUT_METHOD:-auto} in
    auto|ibus) ;;
    *) exit 0 ;;
esac
if [[ -n ${GTK_IM_MODULE:-} && ${GTK_IM_MODULE} != ibus ]] ||
   [[ -n ${QT_IM_MODULE:-} && ${QT_IM_MODULE} != ibus ]] ||
   [[ -n ${XMODIFIERS:-} && ${XMODIFIERS} != '@im=ibus' ]]; then
    exit 0
fi
command -v ibus-daemon >/dev/null 2>&1 || exit 0
# Another framework may have been started without exporting its toolkit variables.
if command -v pgrep >/dev/null 2>&1 && pgrep -u "$(id -u)" -x 'fcitx5|fcitx' >/dev/null 2>&1; then
    exit 0
fi
# IBus itself refuses to replace an existing instance without --replace.
exec ibus-daemon --daemonize --xim
