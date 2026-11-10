"""Static contract checks; a real GTK/Waybar session is still required."""
import ast
import glob
import json
import os
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
STYLE = ROOT / "Configs/.local/share/waybar/styles/anide-glass.css"


class GlassStyleTest(unittest.TestCase):
    def test_inherits_existing_styles_and_theme(self):
        css = STYLE.read_text()
        self.assertIn('@import "defaults.css";', css)
        for token in ("@main-bg", "@main-fg", "@wb-act-bg", "@wb-act-fg", "@wb-hvr-bg", "@wb-hvr-fg"):
            self.assertIn(token, css)
        self.assertNotIn('/home/', css)

    def test_style_is_in_existing_sync_tree(self):
        manifest = (ROOT / "Scripts/dots/waybar.toml").read_text()
        self.assertIn('source_root = "Configs/.local/share/waybar"', manifest)
        self.assertIn('"styles"', manifest)

    def test_layout_structure_and_no_unknown_groups(self):
        path = ROOT / "Configs/.local/share/waybar/layouts/anide-glass.jsonc"
        layout = json.loads(path.read_text())
        groups = set(layout["modules-left"] + layout["modules-center"] + layout["modules-right"])
        self.assertEqual(groups, {"group/pill#navigation", "group/pill#center", "group/pill#system"})
        for group in groups:
            self.assertTrue(layout[group]["modules"])
        self.assertEqual(layout["include"], ["$XDG_CONFIG_HOME/waybar/includes/includes.json"])
        self.assertEqual(layout["position"], "top")
        self.assertNotIn("/home/", path.read_text())

    def test_layout_resolves_matching_style_and_user_override(self):
        # Exercise the production resolver without importing Waybar's desktop dependencies.
        source = (ROOT / "Configs/.local/lib/hyde/waybar.py").read_text()
        tree = ast.parse(source)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "resolve_style_path")
        module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
        class Logger:
            def debug(self, *args): pass
            def warning(self, *args): pass
        with tempfile.TemporaryDirectory() as tmp:
            user = pathlib.Path(tmp) / "user"
            user.mkdir()
            shared = STYLE.parent
            scope = {"os": os, "glob": glob, "STYLE_DIRS": [str(user), str(shared)], "logger": Logger()}
            exec(compile(module, "waybar.py", "exec"), scope)
            resolve = scope["resolve_style_path"]
            layout = str(ROOT / "Configs/.local/share/waybar/layouts/anide-glass.jsonc")
            self.assertEqual(resolve(layout), str(STYLE))
            override = user / "anide-glass.css"
            override.touch()
            self.assertEqual(resolve(layout), str(override))


if __name__ == "__main__":
    unittest.main()
