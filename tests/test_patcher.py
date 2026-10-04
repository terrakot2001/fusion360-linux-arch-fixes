import unittest

import fusion360_arch_fix as f


class PatcherTests(unittest.TestCase):
    def test_config_updates_are_idempotent(self):
        src = "A=1\nFUSION_ENABLE_TOOLWINDOW_FIXER=1\n"
        updates = {
            "FUSION_ENABLE_TOOLWINDOW_FIXER": "0",
            "FUSION_FIX_BCP47LANGS": "1",
        }
        once = f.set_config_values(src, updates)
        twice = f.set_config_values(once, updates)
        self.assertEqual(once, twice)
        self.assertIn("FUSION_ENABLE_TOOLWINDOW_FIXER=0", once)
        self.assertIn("FUSION_FIX_BCP47LANGS=1", once)

    def test_launcher_separator_fix(self):
        src = '''dll_overrides="bcp47langs="\ndll_overrides="${dll_overrides:+$dll_overrides,}winhttp=b"\ndll_overrides="${dll_overrides:+$dll_overrides,}icuuc,icuin,icudt=n,b"\n'''
        out, changed = f.patch_launcher_text(src)
        self.assertTrue(changed)
        self.assertIn("${dll_overrides:+$dll_overrides;}winhttp=b", out)
        self.assertIn("${dll_overrides:+$dll_overrides;}icuuc,icuin,icudt=n,b", out)
        out2, changed2 = f.patch_launcher_text(out)
        self.assertFalse(changed2)
        self.assertEqual(out, out2)

    def test_cleanup_replacement(self):
        src = '''cleanup() {\n    # Kill Fusion/Wine/Proton processes\n    if declare -F kill_fusion_processes &>/dev/null; then\n      kill_fusion_processes || true\n    fi\n\n    # Remove PID file directory\n    true\n}\n'''
        out, changed = f.patch_cleanup_text(src)
        self.assertTrue(changed)
        self.assertIn("# Stop Wine only for the Fusion prefix.", out)
        self.assertNotIn("kill_fusion_processes || true", out)
        out2, changed2 = f.patch_cleanup_text(out)
        self.assertFalse(changed2)
        self.assertEqual(out, out2)

    def test_daemon_patch(self):
        src = '''start_toolwindow_fixer() {\n    nohup "$wine_bin" "$FUSION_TOOLWINDOW_FIXER" &>/dev/null &\n    nohup setsid env WINEPREFIX="$PFX" "$wine_bin" "$FUSION_TOOLWINDOW_FIXER" &>/dev/null &\n}\nif ! daemon_check_running "toolwindow-fixer" && [[ -x "$FUSION_TOOLWINDOW_FIXER" ]]; then\n  start_toolwindow_fixer\nfi\n'''
        out, changed = f.patch_daemon_text(src)
        self.assertTrue(changed)
        self.assertNotIn('    nohup "$wine_bin" "$FUSION_TOOLWINDOW_FIXER" &>/dev/null &\n', out)
        self.assertIn('_is_enabled "$FUSION_ENABLE_TOOLWINDOW_FIXER" && ! daemon_check_running "toolwindow-fixer"', out)
        out2, changed2 = f.patch_daemon_text(out)
        self.assertFalse(changed2)
        self.assertEqual(out, out2)

    def test_cleanup_unknown_layout_fails_closed(self):
        with self.assertRaises(ValueError):
            f.patch_cleanup_text("cleanup() {\n  echo unrelated\n}\n")

    def test_launcher_already_correct_is_unchanged(self):
        src = '''dll_overrides="bcp47langs="\ndll_overrides="${dll_overrides:+$dll_overrides;}winhttp=b"\ndll_overrides="${dll_overrides:+$dll_overrides;}icuuc,icuin,icudt=n,b"\n'''
        out, changed = f.patch_launcher_text(src)
        self.assertFalse(changed)
        self.assertEqual(out, src)

    def test_parse_config_ignores_comments(self):
        parsed = f.parse_config_text("# A=old\nA=1\nB=two=parts\n\n")
        self.assertEqual(parsed, {"A": "1", "B": "two=parts"})

    def test_arch_dependency(self):
        src = "bash\npython3-tk\ntkinter-stuff\n"
        out, changed = f.patch_arch_deps_text(src)
        self.assertTrue(changed)
        self.assertEqual(out, "bash\ntk\ntkinter-stuff\n")
        out2, changed2 = f.patch_arch_deps_text(out)
        self.assertFalse(changed2)
        self.assertEqual(out, out2)


if __name__ == "__main__":
    unittest.main()
