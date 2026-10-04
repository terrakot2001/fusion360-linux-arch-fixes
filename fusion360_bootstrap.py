#!/usr/bin/env python3
"""Full Arch/CachyOS bootstrap for Autodesk Fusion 360 on Linux.

The bootstrap downloads the upstream stonegray/fusion360-linux source, applies
this project's Arch compatibility patches *before* upstream installation, runs
the upstream installer, then applies/verifies the installed-runtime patches.

It does not redistribute Autodesk software. The Autodesk installer is downloaded
by the upstream installer from Autodesk's CDN.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, Optional, Tuple

import fusion360_arch_fix as fixes

UPSTREAM_URL = "https://github.com/stonegray/fusion360-linux.git"
# Pinned to a known source layout so the source-level patches are reproducible.
PINNED_UPSTREAM_REF = "c437488e1e73a19413295cb6ea74e357313bc359"
UPSTREAM_DEFAULT_BRANCH = "dev"


def info(message: str) -> None:
    print(f"[INFO] {message}")


def good(message: str) -> None:
    print(f"[OK] {message}")


def caution(message: str) -> None:
    print(f"[WARN] {message}")


def die(message: str, code: int = 2) -> int:
    print(f"[FAIL] {message}", file=sys.stderr)
    return code


def parse_os_release(path: Path = Path("/etc/os-release")) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(errors="replace").splitlines():
        if "=" not in raw or raw.lstrip().startswith("#"):
            continue
        key, value = raw.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def is_arch_family(values: Dict[str, str]) -> bool:
    distro_id = values.get("ID", "").lower()
    id_like = values.get("ID_LIKE", "").lower().split()
    explicit = {"arch", "cachyos", "manjaro", "endeavouros", "garuda", "artix"}
    return distro_id in explicit or "arch" in id_like


def run(
    args: list[str],
    *,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    pretty = " ".join(args)
    info(f"$ {pretty}")
    return subprocess.run(args, cwd=cwd, env=env, check=check)


def output(args: list[str], *, cwd: Optional[Path] = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def ensure_host() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("Do not run the installer as root. Run it as your normal desktop user.")

    os_release = parse_os_release()
    if not is_arch_family(os_release):
        label = os_release.get("PRETTY_NAME") or os_release.get("ID") or "unknown Linux"
        raise RuntimeError(
            f"This full installer targets Arch-family systems. Detected: {label}. "
            "Use the upstream installer directly on other distributions."
        )

    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        raise RuntimeError("No graphical desktop session detected (DISPLAY/WAYLAND_DISPLAY is empty).")

    if shutil.which("sudo") is None:
        raise RuntimeError("sudo is required because upstream installs Arch packages.")

    good(f"Arch-family host: {os_release.get('PRETTY_NAME', os_release.get('ID', 'Arch'))}")


def ensure_bootstrap_dependencies() -> None:
    missing = [name for name in ("git", "bash") if shutil.which(name) is None]
    if missing:
        if shutil.which("pacman") is None:
            raise RuntimeError(
                "Missing bootstrap dependencies: "
                + ", ".join(missing)
                + ". Automatic dependency installation is only supported on Arch-family hosts."
            )
        info("Installing bootstrap dependencies: " + " ".join(missing))
        run(["sudo", "pacman", "-S", "--needed", "--noconfirm", *missing])

    if shutil.which("git") is None:
        raise RuntimeError("git is still unavailable after dependency installation.")


def existing_install() -> bool:
    home = Path.home()
    return (
        (home / ".local/share/fusion360-linux/launch-fusion.sh").exists()
        and (home / ".config/fusion360-linux/config").exists()
    )


def existing_artifacts() -> list[Path]:
    home = Path.home()
    candidates = [
        home / ".local/share/fusion360-linux",
        home / ".config/fusion360-linux",
        home / ".fusion360-proton2",
    ]
    return [path for path in candidates if path.exists()]


def choose_browser() -> Optional[str]:
    for name in (
        "chromium",
        "google-chrome-stable",
        "google-chrome",
        "brave",
        "brave-browser",
        "firefox",
    ):
        path = shutil.which(name)
        if path:
            return path
    return None


def clone_upstream(base_dir: Path, ref: str) -> Tuple[Path, str]:
    base_dir.mkdir(parents=True, exist_ok=True)
    source = Path(tempfile.mkdtemp(prefix="stonegray-fusion360-linux-", dir=base_dir))
    try:
        run(["git", "clone", "--no-tags", UPSTREAM_URL, str(source)])
        run(["git", "checkout", "--detach", ref], cwd=source)
        sha = output(["git", "rev-parse", "HEAD"], cwd=source)
        good(f"Upstream checkout: {sha}")
        return source, sha
    except Exception:
        caution(f"Keeping failed checkout for inspection: {source}")
        raise


def patch_file(path: Path, patcher, label: str) -> None:
    if not path.exists():
        raise RuntimeError(f"Upstream layout changed; missing {path}")
    old = path.read_text()
    new, changed = patcher(old)
    if changed:
        path.write_text(new)
        good(f"patched upstream: {label}")
    else:
        good(f"already compatible upstream: {label}")


def patch_upstream_tree(source: Path) -> None:
    """Apply all source-level fixes before upstream's install steps run."""
    patch_file(source / "src/install/distro/arch.txt", fixes.patch_arch_deps_text, "Arch dependencies")
    patch_file(source / "src/runtime/launcher-functions.sh", fixes.patch_launcher_text, "WINEDLLOVERRIDES")
    patch_file(source / "share/cleanup.fn", fixes.patch_cleanup_text, "cleanup")
    patch_file(source / "share/process.fn", fixes.patch_process_text, "process isolation")
    patch_file(source / "share/daemon.fn", fixes.patch_daemon_text, "Toolwindow Fixer")
    patch_file(
        source / "src/runtime/fusion-browser-listener.sh",
        fixes.patch_listener_privacy_text,
        "browser/callback log privacy",
    )
    patch_file(
        source / "src/runtime/fusion-callback-handler.sh",
        fixes.patch_callback_privacy_text,
        "callback log privacy",
    )
    patch_file(source / "install.sh", fixes.patch_upstream_install_text, "safe --kill")

    shell_files = [
        source / "install.sh",
        source / "share/cleanup.fn",
        source / "share/process.fn",
        source / "share/daemon.fn",
        source / "src/runtime/launcher-functions.sh",
        source / "src/runtime/fusion-browser-listener.sh",
        source / "src/runtime/fusion-callback-handler.sh",
    ]
    if not fixes.syntax_check(shell_files):
        raise RuntimeError("Source patch produced invalid Bash syntax.")
    good("patched upstream shell syntax verified")


def write_source_manifest(source: Path, upstream_sha: str, upstream_ref: str) -> None:
    manifest = {
        "project": fixes.PROJECT_NAME,
        "patch_version": fixes.VERSION,
        "upstream_url": UPSTREAM_URL,
        "upstream_ref_requested": upstream_ref,
        "upstream_commit": upstream_sha,
        "prepared_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    (source / ".fusion360-arch-fixes.json").write_text(json.dumps(manifest, indent=2) + "\n")


def run_upstream_installer(source: Path) -> None:
    env = os.environ.copy()
    browser = choose_browser()
    if browser:
        # Upstream writes this host browser into its generated config.
        env["BROWSER"] = browser
        env["CHROME"] = browser
        good(f"host browser selected: {browser}")
    else:
        caution("No common host browser found; upstream browser fallback will be used.")

    # These are safe defaults while installation is running. The final config is
    # enforced again by fusion360_arch_fix.py after upstream returns.
    env["FUSION_ENABLE_TOOLWINDOW_FIXER"] = "0"
    env["FUSION_USE_INTEL_VK_ICD"] = "0"
    env["FUSION_FIX_BCP47LANGS"] = "1"

    info("Starting upstream Fusion installer. sudo may ask for your password.")
    run(["bash", "install.sh"], cwd=source, env=env)
    good("upstream installer returned successfully")


def verify_fusion_payload() -> Path:
    prefix = Path.home() / ".fusion360-proton2"
    candidates = list(prefix.glob("pfx/drive_c/users/steamuser/AppData/Local/Autodesk/webdeploy/production/*/Fusion360.exe"))
    if not candidates:
        # Fall back to a bounded search in Autodesk data only.
        root = prefix / "pfx/drive_c/users/steamuser/AppData/Local/Autodesk"
        if root.exists():
            candidates = list(root.rglob("Fusion360.exe"))
    if not candidates:
        raise RuntimeError("Fusion360.exe was not found after upstream installation.")
    exe = sorted(candidates)[-1]
    good(f"Fusion payload found: {exe}")
    return exe


def install_maintenance_tools(project_root: Path, upstream_sha: str, upstream_ref: str) -> None:
    home = Path.home()
    data = home / ".local/share/fusion360-linux/arch-fixes"
    bin_dir = home / ".local/bin"
    config_dir = home / ".config/fusion360-linux"
    data.mkdir(parents=True, exist_ok=True)
    (data / "scripts").mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(project_root / "fusion360_arch_fix.py", data / "fusion360_arch_fix.py")
    shutil.copy2(
        project_root / "scripts/collect-diagnostics.sh",
        data / "scripts/collect-diagnostics.sh",
    )

    wrappers = {
        "fusion360-arch-check": f'''#!/usr/bin/env bash
set -euo pipefail
exec python3 "{data / 'fusion360_arch_fix.py'}" check "$@"
''',
        "fusion360-arch-repair": f'''#!/usr/bin/env bash
set -euo pipefail
python3 "{data / 'fusion360_arch_fix.py'}" apply
exec python3 "{data / 'fusion360_arch_fix.py'}" check
''',
        "fusion360-arch-diagnostics": f'''#!/usr/bin/env bash
set -euo pipefail
exec bash "{data / 'scripts/collect-diagnostics.sh'}" "$@"
''',
        "fusion360-safe-stop": f'''#!/usr/bin/env bash
set -euo pipefail
exec "{home / '.local/share/fusion360-linux/runtime-scripts/kill-wine-proton-fusion-nuclear.sh'}"
''',
    }
    for name, content in wrappers.items():
        path = bin_dir / name
        path.write_text(content)
        path.chmod(0o755)

    project_sha = None
    try:
        project_sha = output(["git", "rev-parse", "HEAD"], cwd=project_root)
    except Exception:
        pass

    provenance = {
        "patch_version": fixes.VERSION,
        "project_commit": project_sha,
        "upstream_url": UPSTREAM_URL,
        "upstream_ref_requested": upstream_ref,
        "upstream_commit": upstream_sha,
        "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    (config_dir / "arch-fixes-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    good("maintenance commands installed in ~/.local/bin")


def post_patch_and_verify(project_root: Path, upstream_sha: str, upstream_ref: str) -> None:
    rc = fixes.apply(fixes.default_paths())
    if rc != 0:
        raise RuntimeError(f"Post-install patching failed with exit code {rc}.")

    rc = fixes.check(fixes.default_paths())
    if rc != 0:
        raise RuntimeError(f"Post-install verification failed with exit code {rc}.")

    verify_fusion_payload()
    install_maintenance_tools(project_root, upstream_sha, upstream_ref)

    desktop = Path.home() / ".local/share/applications/fusion360-linux/autodesk-fusion360.desktop"
    if desktop.exists():
        good("desktop launcher installed")
    else:
        caution("desktop launcher was not found; Fusion can still be started with launch-fusion.sh")


def launch_fusion() -> None:
    launcher = Path.home() / ".local/share/fusion360-linux/launch-fusion.sh"
    if not launcher.exists():
        raise RuntimeError("Fusion launcher not found.")
    subprocess.Popen([str(launcher)], start_new_session=True)
    good("Fusion launch requested")


def install(args: argparse.Namespace) -> int:
    if not args.prepare_only:
        ensure_host()
    ensure_bootstrap_dependencies()

    artifacts = existing_artifacts()
    if not args.prepare_only and existing_install():
        return die(
            "An existing Fusion Linux installation was detected. "
            "Use 'bash repair.sh' or the smart 'bash install.sh' instead of a fresh install."
        )
    if not args.prepare_only and artifacts:
        details = ", ".join(str(path) for path in artifacts)
        return die(
            "A partial/previous Fusion Linux installation was detected. "
            "For safety the fresh installer will not overwrite it automatically. "
            f"Existing paths: {details}"
        )

    project_root = Path(__file__).resolve().parent
    work_base = Path(args.work_base).expanduser() if args.work_base else Path.home() / ".cache/fusion360-linux-arch-fixes"
    upstream_ref = UPSTREAM_DEFAULT_BRANCH if args.latest_upstream else args.upstream_ref

    info(f"patch set: {fixes.VERSION}")
    info(f"upstream ref: {upstream_ref}")
    if upstream_ref == PINNED_UPSTREAM_REF:
        info("using reproducible pinned upstream revision")
    else:
        caution("using a non-pinned upstream ref; source layout may have changed")

    source: Optional[Path] = None
    success = False
    try:
        source, upstream_sha = clone_upstream(work_base, upstream_ref)
        patch_upstream_tree(source)
        write_source_manifest(source, upstream_sha, upstream_ref)

        if args.prepare_only:
            print()
            good("Prepared patched upstream source only.")
            print(f"Source: {source}")
            success = True
            return 0

        run_upstream_installer(source)
        post_patch_and_verify(project_root, upstream_sha, upstream_ref)
        success = True

        print()
        print("============================================================")
        print(" Fusion 360 installation complete")
        print("============================================================")
        print("Start from the application menu or:")
        print("  ~/.local/share/fusion360-linux/launch-fusion.sh")
        print()
        print("Maintenance commands:")
        print("  fusion360-arch-check")
        print("  fusion360-arch-repair")
        print("  fusion360-arch-diagnostics")
        print("  fusion360-safe-stop")
        print()
        print("Autodesk sign-in is completed on first Fusion launch.")

        if args.launch:
            launch_fusion()
        return 0
    except subprocess.CalledProcessError as exc:
        return die(f"Command failed with exit code {exc.returncode}. Patched source kept at: {source}")
    except Exception as exc:
        return die(f"{exc} Patched source kept at: {source}")
    finally:
        if success and source is not None and not args.keep_source and not args.prepare_only:
            shutil.rmtree(source, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Full Fusion 360 installer for Arch/CachyOS with compatibility fixes")
    parser.add_argument(
        "--upstream-ref",
        default=PINNED_UPSTREAM_REF,
        help="stonegray/fusion360-linux tag/branch/commit (default: pinned known source layout)",
    )
    parser.add_argument(
        "--latest-upstream",
        action="store_true",
        help=f"use the upstream {UPSTREAM_DEFAULT_BRANCH!r} branch instead of the pinned revision",
    )
    parser.add_argument("--work-base", help="base directory for the temporary upstream checkout")
    parser.add_argument("--keep-source", action="store_true", help="keep patched upstream source after success")
    parser.add_argument("--prepare-only", action="store_true", help="clone and patch upstream source but do not install")
    parser.add_argument("--launch", action="store_true", help="launch Fusion after successful installation")
    return install(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
