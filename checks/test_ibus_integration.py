"""IBus integration tests with mocked binaries; no desktop session is required."""
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENV_SCRIPT = ROOT / "Configs/.config/uwsm/env-hyprland.d/10-anide-input.sh"
START_SCRIPT = ROOT / "Configs/.local/lib/hyde/ibus-start.sh"


class IbusIntegrationTest(unittest.TestCase):
    def env_defaults(self, values):
        with tempfile.TemporaryDirectory() as tmp:
            daemon = Path(tmp) / "ibus-daemon"
            daemon.write_text("#!/bin/sh\nexit 0\n")
            daemon.chmod(0o755)
            env = {"PATH": tmp, "HOME": "/tmp"}
            env.update(values)
            code = '. "$1"; printf "%s|%s|%s" "${GTK_IM_MODULE-}" "${QT_IM_MODULE-}" "${XMODIFIERS-}"'
            return subprocess.check_output(["/bin/sh", "-c", code, "sh", str(ENV_SCRIPT)], env=env, text=True)

    def test_default_and_existing_input_method(self):
        self.assertEqual(self.env_defaults({}), "ibus|ibus|@im=ibus")
        self.assertEqual(self.env_defaults({"GTK_IM_MODULE": "fcitx"}), "fcitx||")
        self.assertEqual(self.env_defaults({"QT_IM_MODULE": "fcitx"}), "|fcitx|")
        self.assertEqual(self.env_defaults({"XMODIFIERS": "@im=fcitx"}), "||@im=fcitx")
        self.assertEqual(self.env_defaults({"ANIDE_INPUT_METHOD": "none"}), "||")
        self.assertEqual(self.env_defaults({"PATH": "/nonexistent"}), "||")
        self.assertEqual(self.env_defaults({"GTK_IM_MODULE": "ibus"}), "ibus|ibus|@im=ibus")

    def run_start(self, settings, running_fcitx=False):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            logfile = folder / "log"
            (folder / "ibus-daemon").write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$LOG"\n')
            (folder / "pgrep").write_text(f'#!/bin/sh\nexit {0 if running_fcitx else 1}\n')
            (folder / "ibus-daemon").chmod(0o755)
            (folder / "pgrep").chmod(0o755)
            env = {"PATH": f"{tmp}:/usr/bin:/bin", "HOME": tmp, "LOG": str(logfile), **settings}
            subprocess.run(["bash", str(START_SCRIPT)], env=env, check=True)
            return logfile.read_text() if logfile.exists() else ""

    def test_daemon_no_replace_or_conflicts(self):
        self.assertEqual(self.run_start({}), "--daemonize --xim\n")
        self.assertEqual(self.run_start({"ANIDE_INPUT_METHOD": "none"}), "")
        self.assertEqual(self.run_start({"GTK_IM_MODULE": "fcitx"}), "")
        self.assertEqual(self.run_start({}, running_fcitx=True), "")

    def test_package_and_session_wiring(self):
        deps = tomllib.loads((ROOT / "Scripts/dots/deps.toml").read_text())
        entry = deps["global"]["dependency"][0]
        self.assertIn("ibus", entry["pacman"])
        for helper in ("yay", "paru"):
            self.assertIn("ibus-unikey", entry[helper])
        self.assertIn('hc.start.input_method = "hyde-shell ibus-start"', (ROOT / "Configs/.local/share/hypr/lua/variables.lua").read_text())
        self.assertIn('check_exec(hs.input_method)', (ROOT / "Configs/.local/share/hypr/lua/start_up.lua").read_text())
        subprocess.run(["bash", "-n", str(START_SCRIPT)], check=True)
        subprocess.run(["sh", "-n", str(ENV_SCRIPT)], check=True)


if __name__ == "__main__":
    unittest.main()
