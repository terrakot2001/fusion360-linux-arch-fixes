import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fusion360_bootstrap as b


class BootstrapTests(unittest.TestCase):
    def test_arch_family_direct_ids(self):
        for distro in ("arch", "cachyos", "manjaro", "endeavouros", "garuda", "artix"):
            self.assertTrue(b.is_arch_family({"ID": distro}))

    def test_arch_family_id_like(self):
        self.assertTrue(b.is_arch_family({"ID": "custom", "ID_LIKE": "arch linux"}))

    def test_non_arch_is_rejected(self):
        self.assertFalse(b.is_arch_family({"ID": "ubuntu", "ID_LIKE": "debian"}))

    def test_xdg_cache_home(self):
        with patch.dict(os.environ, {"XDG_CACHE_HOME": "/tmp/custom-cache"}, clear=False):
            self.assertEqual(b.xdg_cache_home(Path("/tmp/home")), Path("/tmp/custom-cache"))

    def test_existing_install_honors_xdg_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "data"
            config = root / "config"
            (data / "fusion360-linux").mkdir(parents=True)
            (data / "fusion360-linux/launch-fusion.sh").write_text("#!/bin/sh\n")
            (config / "fusion360-linux").mkdir(parents=True)
            (config / "fusion360-linux/config").write_text("PROTON=/tmp/proton\n")
            with patch.dict(
                os.environ,
                {"XDG_DATA_HOME": str(data), "XDG_CONFIG_HOME": str(config)},
                clear=False,
            ):
                self.assertTrue(b.existing_install())

    def test_fusion_prefix_prefers_installed_config(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "config"
            cfg = config / "fusion360-linux/config"
            cfg.parent.mkdir(parents=True)
            cfg.write_text("STEAM_COMPAT_DATA_PATH=/tmp/custom-fusion-prefix\n")
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(config)}, clear=False):
                self.assertEqual(
                    b.fusion_prefix_path(),
                    Path("/tmp/custom-fusion-prefix"),
                )

    def test_default_upstream_is_pinned_commit(self):
        self.assertEqual(len(b.PINNED_UPSTREAM_REF), 40)
        self.assertNotEqual(b.PINNED_UPSTREAM_REF, b.UPSTREAM_DEFAULT_BRANCH)


if __name__ == "__main__":
    unittest.main()
