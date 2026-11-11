"""Static checks for hyde-shell rofi.movie; a live Rofi/mpv session is still required."""
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Configs/.local/lib/hyde/rofi.movie.sh"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def run_bash(source, stdin=""):
    process = subprocess.run(
        ["bash", "-c", source],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    return process.returncode, process.stdout, process.stderr


class ScriptContractTest(unittest.TestCase):
    def test_syntax_and_shellcheck(self):
        status, _, err = run_bash(f"bash -n {SCRIPT}")
        self.assertEqual(status, 0, err)
        if shutil.which("shellcheck"):
            status, out, err = run_bash(f"shellcheck -x {SCRIPT}")
            self.assertEqual(status, 0, out + err)

    def test_metadata_header(self):
        header = "\n".join(SCRIPT.read_text().splitlines()[:50])
        self.assertIn("# @name: rofi.movie", header)
        self.assertIn("# @ver:", header)
        # hyde-shell completions only discover scripts that declare @name early.
        for line in SCRIPT.read_text().splitlines()[:50]:
            if line.startswith("# @name:"):
                self.assertEqual(line.split(":", 1)[1].strip(), "rofi.movie")
                break

    def test_help_documents_every_subcommand(self):
        _, out, _ = run_bash(f"bash {SCRIPT} -h")
        for command in ("search", "browse", "recent", "history", "play", "link", "open", "settings", "diagnose"):
            self.assertRegex(out, rf"\b{command}\b")

    def test_configuration_is_namespaced(self):
        text = SCRIPT.read_text()
        for key in ("PLAYER", "STYLE", "SCALE", "FONT", "SERVER_PREF", "POSTER", "LIMIT", "DETAIL_TTL"):
            self.assertIn(f"ROFI_MOVIE_{key}", text)
        # Only the XDG/HyDE path plumbing may be exported; settings stay local so
        # they never leak into other hyde-shell wrappers.
        exported = re.findall(r"(?m)^export ([A-Za-z_][A-Za-z0-9_]*)=", text)
        for name in exported:
            self.assertTrue(
                name.startswith(("XDG_", "HYDE_")),
                f"unexpected export {name}",
            )

    def test_no_unsafe_home_paths(self):
        text = SCRIPT.read_text()
        self.assertNotIn("/home/", text)
        self.assertNotIn("rm -rf /", text)


class FixtureParsingTest(unittest.TestCase):
    """jq fixtures copied from the live PhimAPI responses (v1 and legacy shape)."""

    def test_fixtures_are_valid_json(self):
        for path in FIXTURES.glob("*.json"):
            with path.open(encoding="utf-8") as handle:
                json.load(handle)

    def test_rows_are_pipe_safe(self):
        # Row fields are read back with awk -F'|', so names must never add pipes.
        status, out, err = run_bash(
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); movie_rows < {FIXTURES / 'legacy.json'}"
        )
        self.assertEqual(status, 0, err)
        rows = [line for line in out.splitlines() if line]
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0].split("|")), 5, rows[0])
        self.assertEqual(rows[0].split("|")[2], "phim-cu")

    def test_pagination_matches_both_api_shapes(self):
        source = (
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
            f"for f in {FIXTURES / 'category.json'} {FIXTURES / 'legacy.json'}; do "
            'jq -r "$MOVIE_JQ_TOTAL" <"$f" | tr "\\n" " "; '
            'jq -r "$MOVIE_JQ_PAGE" <"$f"; done'
        )
        status, out, err = run_bash(source)
        self.assertEqual(status, 0, err)
        self.assertEqual(out.split(), ["387", "1", "2", "1"])

    def test_empty_category_is_not_an_error(self):
        status, out, _ = run_bash(
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); movie_rows < {FIXTURES / 'empty.json'}"
        )
        self.assertEqual(status, 0)
        self.assertEqual(out.strip(), "")

    def test_servers_and_episodes(self):
        source = (
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
            f"json=$(cat {FIXTURES / 'detail.json'}); "
            'movie_servers <<<"$json"; echo ---; movie_episodes "$json" 0'
        )
        status, out, err = run_bash(source)
        self.assertEqual(status, 0, err)
        servers, episodes = out.split("---")
        self.assertIn("0|Vietsub|3", servers)
        self.assertEqual(len([line for line in episodes.splitlines() if line]), 3)
        for line in episodes.splitlines():
            if line:
                self.assertEqual(len(line.split("|")), 3, line)

    def test_server_preference_matching(self):
        source = (
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
            f"json=$(cat {FIXTURES / 'detail.json'}); "
            'for pref in auto vietsub thuyet-minh long-tieng; do '
            'printf "%s=" "$pref"; MOVIE_SERVER_PREF=$pref movie_pref_server "$json"; echo; done'
        )
        _, out, err = run_bash(source)
        chosen = dict(line.split("=", 1) for line in out.splitlines() if "=" in line)
        self.assertEqual(chosen["auto"], "0")
        self.assertEqual(chosen["vietsub"], "0")
        self.assertEqual(chosen["thuyet-minh"], "1")
        # No matching server falls back to the first one.
        self.assertEqual(chosen["long-tieng"], "0")

    def test_stream_url_prefers_m3u8(self):
        row = "Tập 1|https://cdn/index.m3u8|https://player/?url=x"
        source = (
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
            f"movie_stream_url {shlex.quote(row)}"
        )
        status, out, err = run_bash(source)
        self.assertEqual(status, 0, err)
        self.assertEqual(out.strip(), "https://cdn/index.m3u8")

    def test_stream_url_decodes_embed_parameter(self):
        # Some servers only expose the player wrapper; the m3u8 hides in ?url=.
        target = "https://s4.example.tv/x/index.m3u8?token=abc"
        row = f"Tập 1||https://player.example/?url={quote(target, safe='')}"
        source = (
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
            f"movie_stream_url {shlex.quote(row)}"
        )
        status, out, err = run_bash(source)
        self.assertEqual(status, 0, err)
        self.assertEqual(out.strip(), target)

    def test_stream_url_rejects_empty_row(self):
        source = f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); movie_stream_url 'Tập 1||'"
        status, _, _ = run_bash(source)
        self.assertEqual(status, 1)


class ConfigWiringTest(unittest.TestCase):
    def test_schema_and_keybind_are_wired(self):
        schema = (ROOT / "Configs/.local/share/hyde/schema/schema.toml").read_text()
        self.assertIn("[properties.rofi.properties.movie]", schema)
        for key in ("player", "style", "scale", "font", "server_pref", "poster", "site_url"):
            self.assertIn(f"[properties.rofi.properties.movie.properties.{key}]", schema)

        generated = (ROOT / "Configs/.local/share/hyde/schema/config.toml").read_text()
        self.assertIn("[rofi.movie]", generated)

        dispatcher = (ROOT / "Configs/.local/share/hypr/lua/hyde/dispatcher.lua").read_text()
        self.assertIn('"rofi.movie"', dispatcher)

        binds = (ROOT / "Configs/.local/share/hypr/lua/key_binds.lua").read_text()
        self.assertIn('MOD .. " + SHIFT + M"', binds)
        # MOD + CONTROL + M stays reserved for window mute.
        self.assertIn('MOD .. "+ CONTROL + M"', binds)

    def test_generated_config_hydrates_the_script(self):
        """[rofi.movie] keys must reach the script as ROFI_MOVIE_* (config.lua)."""
        import tomllib

        schema = tomllib.loads(
            (ROOT / "Configs/.local/share/hyde/schema/config.toml").read_text()
        )
        movie = schema["rofi"]["movie"]
        expected = {
            "player": "ROFI_MOVIE_PLAYER",
            "style": "ROFI_MOVIE_STYLE",
            "scale": "ROFI_MOVIE_SCALE",
            "font": "ROFI_MOVIE_FONT",
            "width": "ROFI_MOVIE_WIDTH",
            "server_pref": "ROFI_MOVIE_SERVER_PREF",
            "poster": "ROFI_MOVIE_POSTER",
            "limit": "ROFI_MOVIE_LIMIT",
            "detail_ttl": "ROFI_MOVIE_DETAIL_TTL",
            "site_url": "ROFI_MOVIE_SITE_URL",
            "api_url": "ROFI_MOVIE_API_URL",
            "cdn_url": "ROFI_MOVIE_CDN_URL",
        }
        self.assertEqual(set(movie), set(expected))
        for key, env in expected.items():
            self.assertEqual(f"ROFI_MOVIE_{key.upper()}", env)

    def test_settings_menu_persists_and_sanitises(self):
        """movie_set_config writes TOML literals; movie_setup_rofi sanitises input."""
        workdir = pathlib.Path(tempfile.mkdtemp())
        try:
            config = workdir / "hyde" / "config.toml"
            config.parent.mkdir()
            config.write_text('[rofi.movie]\nplayer = "vlc"\n\n[rofi.launch]\nstyle = "s1"\n')
            env = {**os.environ, "XDG_CONFIG_HOME": str(workdir)}
            source = (
                f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
                'movie_set_config limit 30; movie_set_config font "JetBrainsMono NF"'
            )
            process = subprocess.run(
                ["bash", "-c", source], capture_output=True, text=True, env=env, cwd=ROOT
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            written = tomllib.loads(config.read_text())["rofi"]["movie"]
            self.assertEqual(written["limit"], 30)
            self.assertEqual(written["font"], "JetBrainsMono NF")
            # The untouched key and the following table survive the rewrite.
            self.assertEqual(written["player"], "vlc")
            self.assertEqual(tomllib.loads(config.read_text())["rofi"]["launch"]["style"], "s1")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def test_invalid_settings_fall_back_to_defaults(self):
        env = {
            **os.environ,
            "ROFI_MOVIE_LIMIT": "999",
            "ROFI_MOVIE_DETAIL_TTL": "abc",
            "ROFI_MOVIE_SERVER_PREF": "bad|value",
            "ROFI_MOVIE_WIDTH": "",
        }
        source = (
            f"source <(sed '/^main \"\\$@\"$/d' {SCRIPT}); "
            'printf "%s %s %s %s" "$MOVIE_LIMIT" "$MOVIE_DETAIL_TTL" '
            '"$MOVIE_SERVER_PREF" "$MOVIE_WIDTH"'
        )
        process = subprocess.run(
            ["bash", "-c", source], capture_output=True, text=True, env=env, cwd=ROOT
        )
        self.assertEqual(process.stdout.split(), ["24", "600", "auto", "46em"])


if __name__ == "__main__":
    unittest.main()
