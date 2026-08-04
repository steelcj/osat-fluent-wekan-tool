#!/usr/bin/env python3
"""
install-wekan.py -- OSAT Fluent installer for wekan-tool

Archetype 5 (User XDG / Manual User Install), per osat-fluent--archetype-5-*.
Installs a self-contained Wekan bundle (Node.js + FerretDB v1 + SQLite,
all included in the upstream release zip) into a versioned, side-by-side
directory under the user's XDG data home (or %LOCALAPPDATA% on Windows).
No elevation. No dependency beyond Python 3.8 stdlib and network access to
github.com/codeload.github.com.

Two selection modes, both read from config/wekan-assets.json:

  latest (default) -- each platform independently uses the newest release
  that shipped an asset for it. Right choice for a single person on their
  own machine. Because upstream doesn't publish every asset on every
  release, this can mean different platforms end up on different Wekan
  versions (e.g. Windows on v10.24 while Linux/macOS track v10.44).

  team (--mode team) -- every platform pins to the same version, so every
  team member converges on identical Wekan behavior regardless of OS. Right
  choice when consistency across a team matters more than each platform
  having its own latest. Comes with a real tradeoff: the pinned version may
  be missing security fixes present in newer releases. See the
  "security_note" field under policy.team in the config file, and
  ROADMAP.md, before using this for anything reachable beyond localhost.

Mutable Wekan data (attachments, avatars, the FerretDB/SQLite database file)
is deliberately kept OUTSIDE the versioned bundle directory, in a stable
data directory that survives upgrades.

Usage:
    python3 install-wekan.py [--mode {latest,team}] [--data-dir PATH] [--platform PLATFORM]

Status: Draft. Linux (amd64/arm64/ppc64le/riscv64/s390x), macOS (Apple
Silicon only), and Windows (amd64, pinned to an older release) are
supported. See ROADMAP.md for gaps.
"""

import hashlib
import json
import os
import platform
import stat
import sys
import urllib.request
import zipfile
from pathlib import Path

TOOL_NAME = "wekan-tool"
CONFIG_FILENAME = "wekan-assets.json"


def log(msg):
    print(f"[{TOOL_NAME}] {msg}")


def fail(msg):
    print(f"[{TOOL_NAME}] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def is_windows():
    return platform.system().lower() == "windows"


def detect_platform():
    """Map (system, machine) to the platform keys used in wekan-assets.json."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    machine_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "ppc64le": "ppc64le",
        "riscv64": "riscv64",
        "s390x": "s390x",
    }
    arch = machine_map.get(machine)

    if system == "linux":
        if arch is None:
            fail(f"Unsupported Linux architecture: {machine}")
        return f"linux-{arch}"
    if system == "darwin":
        if arch != "arm64":
            fail(
                "Unsupported macOS architecture: "
                f"{machine}. Upstream currently ships Apple Silicon (arm64) "
                "only -- no Intel Mac zip exists in recent releases. See ROADMAP.md."
            )
        return "darwin-arm64"
    if system == "windows":
        if arch != "amd64":
            fail(f"Unsupported Windows architecture: {machine}")
        return "windows-amd64"
    fail(f"Unsupported platform: {system}")


def xdg_data_home():
    if os.environ.get("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"])
    return Path.home() / ".local" / "share"


def tool_root():
    """Where wekan-tool owns everything: versions, cache, state."""
    if is_windows():
        base = os.environ.get("LOCALAPPDATA")
        if not base:
            fail("LOCALAPPDATA is not set.")
        return Path(base) / TOOL_NAME
    return xdg_data_home() / TOOL_NAME


def wrapper_path():
    if is_windows():
        base = os.environ.get("LOCALAPPDATA")
        if not base:
            fail("LOCALAPPDATA is not set.")
        return Path(base) / "Programs" / f"{TOOL_NAME}.cmd"
    return Path.home() / ".local" / "bin" / TOOL_NAME


def data_dir(override=None):
    """
    Stable, XDG-scoped (or %LOCALAPPDATA%-scoped) location for Wekan's
    mutable state -- attachments, avatars, and the FerretDB/SQLite database
    file (WRITABLE_PATH and the FerretDB data path both get pointed here).
    Never inside a versioned bundle directory, so upgrades never touch it.
    """
    if override:
        return Path(override).expanduser().resolve()
    return tool_root() / "data"


def load_config():
    config_path = Path(__file__).parent / "config" / CONFIG_FILENAME
    if not config_path.exists():
        fail(f"Missing config file: {config_path}")
    with open(config_path) as f:
        return json.load(f)


def resolve_asset(config, plat_key, mode):
    """
    Returns (version, asset_dict) for the given platform under the given
    mode ('latest' or 'team'). Fails with a clear message if the resolved
    version has no asset for this platform -- most likely to happen in
    team mode, since the pinned version may predate a platform gaining
    support, or postdate it losing one.
    """
    policy = config.get("policy", {})

    if mode == "team":
        team_policy = policy.get("team")
        if team_policy is None:
            fail("No 'policy.team' entry in config.")
        version = team_policy["version"]
        note = team_policy.get("security_note")
        if note:
            log("TEAM MODE SECURITY NOTE:")
            log(note)
    elif mode == "latest":
        latest_policy = policy.get("latest", {})
        version = latest_policy.get(plat_key)
        if version is None:
            fail(f"No 'policy.latest' entry for platform '{plat_key}'.")
    else:
        fail(f"Unknown mode: {mode}")

    release = config.get("releases", {}).get(version)
    if release is None:
        fail(f"Config references version '{version}' but 'releases' has no such entry.")

    asset = release.get("platforms", {}).get(plat_key)
    if asset is None:
        fail(
            f"Version {version} (selected by --mode {mode}) has no asset for "
            f"platform '{plat_key}'. Available in that release: "
            f"{', '.join(release.get('platforms', {}))}"
        )
    return version, asset


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    log(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": TOOL_NAME})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as out:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def extract_zip(zip_path, dest_dir):
    """
    zipfile.extractall() does not restore Unix permission bits by default --
    it silently drops the executable bit on everything, including
    start-wekan.sh, which is why the wrapper fails with 'Permission denied'
    if this isn't handled explicitly. Each ZipInfo's external_attr encodes
    the original Unix mode in its high 16 bits when the archive was created
    on a Unix system (which these are); re-apply it after extraction.
    """
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
        if is_windows():
            return  # Windows has no Unix mode bits to restore.
        for info in zf.infolist():
            mode = info.external_attr >> 16
            if mode == 0:
                continue  # Archive member has no Unix mode recorded.
            target = dest_dir / info.filename
            if target.exists():
                os.chmod(target, mode)


def secure_mkdir(path):
    path.mkdir(parents=True, exist_ok=True)
    if not is_windows():
        os.chmod(path, 0o700)


def install(data_dir_override=None, platform_override=None, mode="latest"):
    config = load_config()
    plat_key = platform_override or detect_platform()
    version, asset = resolve_asset(config, plat_key, mode)

    root = tool_root()
    version_dir = root / version
    wrap_path = wrapper_path()
    resolved_data_dir = data_dir(data_dir_override)

    # Idempotency: if this platform's resolved version is already installed
    # and the wrapper points at it, there is nothing to do.
    if version_dir.exists() and wrap_path.exists():
        log(
            f"wekan {version} ({plat_key}, mode={mode}) already installed "
            f"at {version_dir} -- nothing to do."
        )
        return

    secure_mkdir(root)
    secure_mkdir(resolved_data_dir)

    cache_dir = root / "cache"
    secure_mkdir(cache_dir)
    zip_path = cache_dir / asset["filename"]

    if not zip_path.exists() or sha256_of(zip_path) != asset["sha256"]:
        download(asset["url"], zip_path)

    log("Verifying checksum...")
    actual = sha256_of(zip_path)
    if actual != asset["sha256"]:
        fail(
            f"Checksum mismatch for {asset['filename']}: "
            f"expected {asset['sha256']}, got {actual}"
        )
    log("Checksum verified.")

    log(f"Extracting to {version_dir}")
    version_dir.parent.mkdir(parents=True, exist_ok=True)
    extract_zip(zip_path, version_dir)
    if not is_windows():
        os.chmod(version_dir, 0o700)
        # Belt-and-suspenders: ensure the launcher itself is executable
        # even if a future release's zip lacks a Unix mode bit for it
        # (e.g. if it's ever built on a Windows CI runner).
        launcher = version_dir / "bundle" / "start-wekan.sh"
        if launcher.exists():
            os.chmod(launcher, 0o700)

    # TODO(verify): confirm the exact env var names start-wekan uses in
    # this bundle to place the FerretDB/SQLite data file. Older
    # MongoDB-backed bundles used WRITABLE_PATH for attachments/avatars
    # only, with MONGO_URL pointing at an external server. The bundled
    # FerretDB+SQLite release may use a different variable for the SQLite
    # file location -- inspect version_dir/bundle/start-wekan.sh (or .bat)
    # after first extraction and update the wrapper templates accordingly
    # before relying on this with real data. Do not assume -- verify, per
    # the archetype-5 checklist.
    write_wrapper(plat_key, wrap_path, version_dir, resolved_data_dir)

    secure_mkdir(wrap_path.parent)
    log(f"Installed wekan {version} for {plat_key} (mode={mode}).")
    log(f"Data directory: {resolved_data_dir}")
    log(f"Run with: {wrap_path}")


def write_wrapper(plat_key, wrap_path, version_dir, resolved_data_dir):
    bundle_dir = version_dir / "bundle"
    repo_root = Path(__file__).parent

    if plat_key == "windows-amd64":
        template_path = repo_root / "scripts" / "windows" / "wekan-tool.cmd"
    else:
        template_path = repo_root / "scripts" / "nix" / "wekan-tool"

    if not template_path.exists():
        fail(f"Missing wrapper template: {template_path}")

    content = template_path.read_text()
    content = content.replace("__WEKAN_DATA_DIR__", str(resolved_data_dir))
    content = content.replace("__WEKAN_BUNDLE_DIR__", str(bundle_dir))

    wrap_path.parent.mkdir(parents=True, exist_ok=True)
    wrap_path.write_text(content)
    if not is_windows():
        os.chmod(wrap_path, stat.S_IRWXU)  # 700: owner rwx only


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OSAT Fluent installer for Wekan.")
    parser.add_argument("--data-dir", default=None, help="Override the data directory.")
    parser.add_argument("--platform", default=None, help="Override platform detection.")
    parser.add_argument(
        "--mode",
        choices=["latest", "team"],
        default="latest",
        help=(
            "'latest' (default): this platform tracks its own newest release. "
            "'team': pin to the same version as every other team member's machine, "
            "regardless of platform. See the module docstring."
        ),
    )
    args = parser.parse_args()

    if hasattr(os, "geteuid") and os.geteuid() == 0:
        fail("Refusing to run as root. OSAT tools install to user space only.")

    install(data_dir_override=args.data_dir, platform_override=args.platform, mode=args.mode)


if __name__ == "__main__":
    main()
