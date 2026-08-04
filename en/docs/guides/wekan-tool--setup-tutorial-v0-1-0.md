---
dc:title: "Wekan Tool: Setup Tutorial"
dcterms:version: "0.1.0"
dc:creator: "Christopher Steel"
dc:description: "Walks through installing, configuring, and running Wekan via osat-fluent-wekan-tool, including the latest and team version-selection modes and the decisions behind the data directory layout."
dcterms:created: "2026-07-28"
dcterms:modified: "2026-07-28"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "wekan-tool--setup-tutorial"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: GPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: "0.1.0"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.1.0"
    date: "2026-07-28"
    author: "Christopher Steel"
    notes: "Initial draft, written against osat-fluent-wekan-tool as it stands after the executable-bit extraction fix."
---

# Wekan Tool: Setup Tutorial

Version: 0.1.0
Status: Draft
Style Guide: style-guide--technical-documentation-for-technologists

## Abstract

This tutorial walks through installing and running Wekan using `osat-fluent-wekan-tool`, an OSAT Fluent tool manager built to the Archetype 5 pattern. It covers prerequisites, the two version-selection modes and when to choose each, installation and verification, running and configuring the instance, data location and backup, upgrading, and the known limitations recorded in the tool's `ROADMAP.md`. It assumes the reader is comfortable with a shell but has not necessarily used an OSAT Fluent tool before.

## Prerequisites

Python 3.8 or later, standard library only. No other software is required to run the installer itself. The installer refuses to run as root, since OSAT Fluent tools install to user space only.

Supported platforms, as of the version this tutorial was written against: Linux (amd64, arm64, ppc64le, riscv64, s390x) and macOS on Apple Silicon. Intel Mac has no upstream release asset in any recent version and is not supported. Windows is supported with a caveat covered in the mode-selection section below.

## Choosing a version-selection mode

`wekan-tool` resolves which Wekan version to install through `config/wekan-assets.json`, using one of two modes. This choice matters enough to make deliberately, not by accepting the default without thinking about it.

**`latest`**, the default, has each platform independently track its own newest upstream release. This is the right choice for one person running Wekan on their own machine. Because upstream does not publish every platform's asset on every release, this can produce version skew between platforms: at the time of writing, Linux and macOS resolve to v10.44 while Windows resolves to v10.24, the newest release that still shipped a `win64.zip`.

**`team`** pins every platform to the same version, so that everyone on a team who runs the installer converges on identical Wekan behaviour regardless of operating system. This was added because version skew is a worse problem for a team than for an individual: two team members on different Wekan versions can see different behaviour on the same board. The tradeoff, stated plainly in the tool's own security note and printed to the console every time `--mode team` runs, is that the pinned version may be missing security fixes present in newer releases. Whether any such fixes exist between the pinned version and the current latest has not been independently verified for this configuration. Treat that as an open question to answer, not a reassurance to rely on, before using `team` mode for anything reachable beyond `localhost`.

The loopback-only assumption matters here specifically because a team deployment is the scenario most likely to break it. Wekan's bundled database, FerretDB v1 over SQLite, carries no authentication by default; the only thing standing between an unauthenticated database and the network is that it binds to `127.0.0.1`. A single person running Wekan locally keeps that assumption true by construction. A team that wants to share one Wekan instance over a LAN does not, and needs to revisit database authentication before doing so, not just the version pin.

```sh
python3 install-wekan.py               # latest, per-platform
python3 install-wekan.py --mode team   # uniform version across the team
```

## Installing

Clone `osat-fluent-wekan-tool`, then run the installer from the repository root.

```sh
git clone https://github.com/steelcj/osat-fluent-wekan-tool.git
cd osat-fluent-wekan-tool
python3 install-wekan.py
```

The installer detects the platform, downloads the matching release asset, verifies it against the SHA-256 checksum recorded in `config/wekan-assets.json`, and extracts it into a versioned directory. The zip itself is the unit of trust: the outer checksum is verified, but nothing inside the zip, the bundled Node.js binary or the FerretDB binary, is independently checked beyond that. This matches the trust model used throughout OSAT Fluent, where a single verified download stands in for the whole artifact, but it is worth naming explicitly rather than leaving implicit.

The installer is safe to re-run. If the version resolved for the current mode is already installed, it reports that there is nothing to do and exits.

### What gets installed, and where

Linux and macOS:

```
~/.local/share/wekan-tool/<version>/bundle/    versioned, replaceable on upgrade
~/.local/share/wekan-tool/data/                persistent, never touched by upgrades
~/.local/share/wekan-tool/cache/               downloaded zips
~/.local/bin/wekan-tool                        wrapper script
```

Windows:

```
%LOCALAPPDATA%\wekan-tool\<version>\bundle\    versioned, replaceable on upgrade
%LOCALAPPDATA%\wekan-tool\data\                persistent, never touched by upgrades
%LOCALAPPDATA%\wekan-tool\cache\               downloaded zips
%LOCALAPPDATA%\Programs\wekan-tool.cmd         wrapper script
```

Everything under `wekan-tool` on Linux and macOS is owner-only, `700` on directories and the wrapper, `600` implied for regular files that do not need to be executable. This matches every other tool in the OSAT Fluent collection.

The separation between the versioned bundle directory and the data directory is deliberate and is the one place this tool deviates from a plain Archetype 5 layout. Wekan is stateful: it accumulates a SQLite-backed database and user-uploaded attachments, unlike a tool such as `rclone-tool` or `hugo-tool` that simply runs and exits. If that state lived inside the versioned bundle directory, an upgrade, which replaces the bundle directory wholesale, would risk destroying it. Keeping data in a stable, XDG-scoped directory outside any versioned path means upgrading Wekan never touches a board.

## Verifying the installation

Confirm the wrapper exists and points at the version you expect.

```sh
# Linux/macOS
cat ~/.local/bin/wekan-tool

# Windows
type %LOCALAPPDATA%\Programs\wekan-tool.cmd
```

The wrapper sets `WRITABLE_PATH` to the data directory, sets `ROOT_URL` and `PORT` from `WEKAN_ROOT_URL`/`WEKAN_PORT` if set or sensible defaults otherwise, changes into the versioned bundle directory, and execs upstream's own `start-wekan.sh` (or `start-wekan.bat` on Windows). It does not reimplement Wekan's own startup logic; it only supplies the environment that logic expects.

If `start-wekan.sh` reports `Permission denied` when the wrapper runs it, the extraction did not preserve the script's executable bit. `zipfile.extractall()` does not restore Unix permission bits by default, which is a real gap the installer had to account for explicitly: it now re-applies each archive member's original Unix mode from the zip's `external_attr` field after extraction, with a direct `chmod` on `start-wekan.sh` as a fallback. If you hit this on a version installed before that fix, delete the affected version directory and re-run `install-wekan.py` rather than trying to repair the extracted directory in place.

## Running Wekan

Run the wrapper directly.

```sh
# Linux/macOS
wekan-tool

# Windows
wekan-tool.cmd
```

By default this serves on `http://localhost:2000`. Override either value by setting `WEKAN_ROOT_URL` or `WEKAN_PORT` in the environment before invoking the wrapper.

```sh
WEKAN_PORT=3000 wekan-tool
```

`start-wekan.sh` is a foreground launcher, not a daemon. It does not background itself or survive the terminal closing, and the wrapper does not add that behaviour on top of it. Keeping Wekan running across logins is not yet solved by this tool; see Known limitations below.

## Data and backup

Everything that needs backing up lives under the data directory (`~/.local/share/wekan-tool/data` or `%LOCALAPPDATA%\wekan-tool\data`): the FerretDB/SQLite database file and any uploaded attachments and avatars. The versioned bundle directory does not need to be backed up, since it can always be reproduced from the checksummed zip.

Whether `WRITABLE_PATH` alone controls the location of every piece of Wekan's data, specifically the FerretDB SQLite file, has not been independently confirmed against this bundle's actual `start-wekan.sh`. Older, MongoDB-backed Wekan bundles used `WRITABLE_PATH` for attachments and avatars only, with the database living wherever the separately-run MongoDB server put it. The newer bundle folds the database into the same zip, but the variable that governs where its SQLite file lands has not been verified to be the same one. Confirm this by reading `bundle/start-wekan.sh` in your installed version before relying on the data directory as a complete backup source.

## Upgrading

Add a new version's data to the `releases` object in `config/wekan-assets.json`, following the shape of the existing entries, then point the relevant `policy` entry (`latest` for the platform in question, or `team.version`) at the new version. Re-run the installer.

```sh
python3 install-wekan.py
```

The new version installs alongside the old one; the wrapper is regenerated to point at it. Data is untouched throughout, since it never lived inside a versioned directory in the first place.

## Known limitations

These are tracked in the tool's own `ROADMAP.md` and repeated here for visibility.

Windows, under `latest` mode, resolves to an older release than Linux and macOS, because upstream stopped publishing a Windows zip somewhere after v10.24. This is a real gap against upstream's own stated position that only the newest Wekan release is supported, and needs periodic re-checking to see whether Windows asset publication resumes.

`team` mode's security note has not been resolved into a definite answer. Someone needs to read the upstream release notes between the pinned version and the current latest and record either a clean bill of health or a specific list of what is being knowingly deferred, directly in the `security_note` field.

There is no persistence mechanism across logins yet. A `systemd --user` unit, or the launchd equivalent on macOS, would close this gap without requiring elevation, but does not exist in this tool as of this version.

## Resources

- [osat-fluent--archetype-5--self-contained-binary](../osat-fluent--archetype-5--self-contained-binary-v0-1-1.md), the pattern this tool follows
- [osat--user-space-installation-specification](../osat--user-space-installation-specification-v0-3-0.md), path and permission conventions referenced throughout this tutorial
- Upstream Wekan releases: <https://github.com/wekan/wekan/releases>

## License

This document, *Wekan Tool: Setup Tutorial*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 5 (Anthropic)**, is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html).

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.1.0 | Draft | Initial draft, written against osat-fluent-wekan-tool as it stands after the executable-bit extraction fix |
