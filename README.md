# wekan-tool

## Description

An OSAT Fluent tool manager for [Wekan](https://github.com/wekan/wekan), the
open-source kanban board. Installs the self-contained Wekan bundle -- Node.js,
FerretDB v1, and SQLite all included in the upstream release zip, no external
runtime or database required -- into a versioned, user-space directory, and
manages the full lifecycle: acquisition, checksum verification, version
tracking, and updates.

Built to the Archetype 5 (User XDG / Manual User Install) pattern defined in
`osat-fluent--archetype-5--self-contained-binary`, with one deliberate
addition: Wekan's mutable data (attachments, avatars, the FerretDB/SQLite
database file) is kept in a stable directory outside the versioned bundle,
so upgrades never touch it.

## Requirements

Python 3.8 or later, standard library only, to run the installer.
No other prerequisite. No dependency on other OSAT Fluent tools.

## Install

```sh
python3 install-wekan.py
```

Detects your platform, downloads the matching release asset from
`wekan/wekan` on GitHub, verifies it against the published SHA-256 checksum,
and extracts it to a versioned directory. Safe to re-run: if the resolved
version for your platform is already installed, it does nothing.

Two modes, chosen with `--mode`:

- **`latest`** (default) -- this platform tracks its own newest release.
  Right choice for one person on their own machine. Because upstream
  doesn't publish every asset on every release, different platforms can
  end up on different Wekan versions this way (currently: Linux/macOS on
  v10.44, Windows on v10.24, the newest release that still shipped a
  `win64.zip`).
- **`team`** -- every platform pins to the same version, so everyone on a
  team converges on identical Wekan behavior regardless of OS. Comes with
  a real tradeoff, printed as a security note at install time: the pinned
  version (currently v10.24) may be missing security fixes present in
  newer releases, and that gap has not been independently verified for
  this config. Worth real attention if the board will be reachable beyond
  `localhost` -- see the `security_note` field in
  `config/wekan-assets.json` and ROADMAP.md.

```sh
python3 install-wekan.py               # latest, per-platform
python3 install-wekan.py --mode team   # uniform version across the team
```

## Upgrade

Update the relevant platform entry in `config/wekan-assets.json` to a newer
release (see the `_comment` field in that file for how to regenerate it),
then re-run:

```sh
python3 install-wekan.py
```

The new version installs side-by-side with the old one. Data is untouched,
since it never lived inside the versioned directory.

## Rollback

Point the wrapper at a previous version directory under
`~/.local/share/wekan-tool/<version>/` and re-run `write_wrapper()` logic
manually, or re-run the installer against an older `wekan-assets.json`.

## Layout

### Linux and macOS (Apple Silicon)

```
~/.local/share/wekan-tool/<version>/bundle/    (versioned, replaceable)
~/.local/share/wekan-tool/data/                (persistent, never touched by upgrades)
~/.local/share/wekan-tool/cache/               (downloaded zips)
~/.local/bin/wekan-tool                        (wrapper script, 700)
```

Everything under `wekan-tool` is owner-only (`700`/`600`), matching every
other Fluent tool.

### Windows

```
%LOCALAPPDATA%\wekan-tool\<version>\bundle\    (versioned, replaceable; pinned to v10.24, see ROADMAP.md)
%LOCALAPPDATA%\wekan-tool\data\                (persistent, never touched by upgrades)
%LOCALAPPDATA%\wekan-tool\cache\               (downloaded zips)
%LOCALAPPDATA%\Programs\wekan-tool.cmd         (wrapper script)
```

The wrapper calls upstream's own `start-wekan.bat`. Not yet tested on real
Windows hardware -- see ROADMAP.md.

## See also

- `osat-fluent--archetype-5--self-contained-binary` -- the pattern this tool follows
- `osat--user-space-installation-specification` -- path and permission conventions
- Upstream: https://github.com/wekan/wekan
