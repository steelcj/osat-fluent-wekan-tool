# ROADMAP

Known gaps and their planned resolution. Not a backlog.

## Windows: pinned to an older release under `latest` mode

Upstream stopped publishing a `win64.zip` somewhere between v10.24 and
v10.44 (releases in between were not individually inspected). Under
`--mode latest` (the default), `windows-amd64` resolves to v10.24 while
Linux/macOS resolve to v10.44 -- this is now an explicit, documented
consequence of the mode rather than a silent gap, but the underlying fact
still needs attention: Windows users on `latest` mode run an older,
potentially less-patched Wekan than everyone else, against upstream's own
stated security posture ("only newest WeKan is supported"). Needs periodic
re-checking against
`https://api.github.com/repos/wekan/wekan/releases/tags/<tag>` for each
release between v10.25 and current, to find whether/when a Windows asset
reappears, and `releases`/`policy.latest` in the config updated accordingly.
Not yet tested on real Windows hardware -- the `.cmd` wrapper calls
upstream's `start-wekan.bat` but that path is unverified end to end.

## `team` mode: security delta between v10.24 and v10.44 not verified

`policy.team.security_note` in the config says plainly that nobody has yet
checked whether security-relevant fixes landed in v10.25 through v10.44.
Before recommending `--mode team` for an actual multi-user deployment,
someone should read that range of release notes at
https://github.com/wekan/wekan/releases and record the answer -- either
"clear" or a specific list of what's being knowingly deferred -- directly
in the security_note field, replacing the current "not verified" language.

No `.ps1` wrapper is provided alongside `wekan-tool.cmd`, unlike the
two-file (`.cmd` + `.ps1`) pattern shown in `osat-fluent--archetype-5`
section 5.2/5.3. Upstream ships `start-wekan.bat`, not a PowerShell
equivalent, so there is nothing for a `.ps1` wrapper to add here. Recorded
as a deliberate deviation with rationale, per the fleet's explicit-rationale
convention, rather than an oversight.

## macOS: Apple Silicon only

Only `wekan-<version>-mac-arm64.zip` exists. No Intel Mac (`darwin-amd64`)
asset is published. `detect_platform()` fails explicitly rather than
silently degrading. Revisit if upstream adds one.

## FerretDB/SQLite data path -- unverified

`write_wrapper()` sets `WRITABLE_PATH` to the tool's XDG data directory,
which is confirmed correct for attachments/avatars based on older
MongoDB-backed bundle documentation. It is NOT yet confirmed that the same
variable, or that variable alone, controls where the bundled FerretDB v1
writes its SQLite file in the newest Node.js+FerretDB+SQLite bundle. This
must be verified by inspecting `bundle/start-wekan.sh` (or `.bat`) after
extraction, before this installer is trusted with real data. Flagged
in-line in `install-wekan.py` as well.

## Wrapper does not persist across reboots

`start-wekan.sh` is a foreground launcher; `wekan-tool`'s wrapper execs it
directly. There is no `systemd --user` unit (or launchd equivalent) yet to
keep Wekan running across logins. Worth adding as a genuinely new pattern --
a user-scoped service archetype -- rather than improvising it here, since
other future Fluent tools may need the same thing.

## No rollback automation

Rollback is currently manual (point the wrapper at an older version
directory). A `--version` flag to `install-wekan.py` that regenerates the
wrapper against an already-downloaded version, without re-fetching, would
match the Rollback section other Archetype 5 tools document.

## Checksum-verification-only trust model

The zip itself is checksum-verified against the GitHub Releases API
`digest` field. Nothing inside the zip (the bundled Node.js binary, FerretDB
binary, or their dependencies) is independently verified beyond that single
outer checksum. This matches the trust model description discussed during
design (the zip is the unit of trust), but is worth a line item in case that
assumption is revisited.
