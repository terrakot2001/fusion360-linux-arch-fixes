import unittest

import fusion360_bootstrap as b


class BootstrapTests(unittest.TestCase):
    def test_arch_family_direct_ids(self):
        for distro in ("arch", "cachyos", "manjaro", "endeavouros", "garuda", "artix"):
            self.assertTrue(b.is_arch_family({"ID": distro}))

    def test_arch_family_id_like(self):
        self.assertTrue(b.is_arch_family({"ID": "custom", "ID_LIKE": "arch linux"}))

    def test_non_arch_is_rejected(self):
        self.assertFalse(b.is_arch_family({"ID": "ubuntu", "ID_LIKE": "debian"}))

    def test_default_upstream_is_pinned_commit(self):
        self.assertEqual(len(b.PINNED_UPSTREAM_REF), 40)
        self.assertNotEqual(b.PINNED_UPSTREAM_REF, b.UPSTREAM_DEFAULT_BRANCH)


if __name__ == "__main__":
    unittest.main()
