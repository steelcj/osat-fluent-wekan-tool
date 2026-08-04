---
dc:title: "Wekan: Web Interface Setup Tutorial"
dcterms:version: "0.2.0"
dc:creator: "Christopher Steel"
dc:description: "Walks through first-run account creation, user profile, and board setup in Wekan's own web interface, with a worked example modeling the OSAT Fluent fleet as a board."
dcterms:created: "2026-07-28"
dcterms:modified: "2026-07-28"
dc:format: "text/markdown"
dc:language: "en"
sat:language_bcp47: "en"
dc:identifier: "wekan--web-interface-setup-tutorial"
dcterms:rightsHolder: "Christopher Steel"
dc:rights: >
  Copyright 2026 Christopher Steel.
  SPDX-License-Identifier: GPL-3.0-or-later
sat:uuid: ""
sat:version_at_creation: "0.1.0"
sat:migration_status: pre-sat
sat:changelog:
  - version: "0.2.0"
    date: "2026-07-28"
    author: "Christopher Steel"
    notes: >
      Added an Accessibility subsection under board creation: a pinned-card
      convention (Wekan has no native "accessibility page enabled" toggle),
      example markdown content for keyboard navigation and visual
      accessibility, and the rationale for a pinned card over a separate
      document.
  - version: "0.1.0"
    date: "2026-07-28"
    author: "Christopher Steel"
    notes: "Initial draft, companion to wekan-tool--setup-tutorial."
---

# Wekan: Web Interface Setup Tutorial

Version: 0.2.0
Status: Draft
Style Guide: style-guide--technical-documentation-for-technologists

## Abstract

This tutorial covers setting up Wekan itself once it is running, first-run account creation, the distinction between site admin and board admin, user profile settings, and board creation and configuration. It closes with a worked example that models the whole OSAT Fluent fleet, every tool repository and `sat` itself, as a single board, including the rationale for how swimlanes, lists, and labels were assigned. It assumes Wekan is already installed and running; see `wekan-tool--setup-tutorial` for that step.

## First-run account creation

Navigate to `<ROOT_URL>/sign-up`, for example `http://localhost:2000/sign-up` with the wrapper's default settings, and register a username, email address, and password. Working email is not required. Wekan is fully usable without configuring an SMTP server, and if registration reports an internal error with no mail server configured, that error can be ignored; the account is created regardless.

The first account ever registered on a given Wekan instance automatically becomes the site admin, the Wekan-wide administrator role, not to be confused with a board admin, which is scoped to a single board and covered below. Every account registered after the first is an ordinary user until a site admin promotes them.

## The Admin Panel

The Admin Panel is reached from the username menu in the top right corner once logged in. It covers instance-wide settings: user accounts and their site-wide permissions, registration policy (open self-registration versus invite-only), and the mail server configuration, if one is wanted. This tutorial does not reproduce the Admin Panel's full reference; upstream's own documentation is the authoritative source for the complete set of settings, and it changes release to release. Point of orientation only: if something instance-wide needs changing, look there first.

## User profile

Profile settings, display name, avatar, and personal preferences such as the default board view, are reached from the same username menu as the Admin Panel. This is per-account and does not require site admin privileges; any registered user can set their own profile.

## Creating a board

A board is created using the "+ Add Board" Button

Every board has a name, a colour, and a visibility setting: private, visible only to invited members, or public, visible to anyone with the link.

The account that creates a board becomes that board's admin automatically, a role distinct from the site-wide admin role covered above. Board admin status can be granted to other members later from the board's own settings.

### Board settings

Board settings are reached by pressing `W`(???) or opening the side menu (the `≡` icon at the top of the board), then the gear icon. From there:

- **Swimlanes** and **lists** can be added, renamed, and removed. Lists are the vertical columns cards move through; swimlanes are horizontal bands that group cards without implying progress, useful for separating unrelated categories of work on the same board.
- **Labels** can be created and coloured, then attached to cards for filtering.
- **Members** can be invited by username or email, and each member's role set: admin (full board control), normal (create and edit cards, but not board settings), comment-only (can comment but not edit or move cards), or no-comments (view only). Only a board admin can change another member's role.
- **Card settings** control which fields appear on a card by default, useful for keeping cards simple when a board does not need every available field.

### Accessibility

- [ ] Accessibility card created and pinned

Wekan has no single setting called "accessibility page enabled"; there is no admin toggle to flip. What exists instead, and what this checklist item actually refers to, is a convention worth adopting deliberately: create a card named `Accessibility`, put it in a list every board member will see (the leftmost list on the default swimlane is a reasonable choice), and pin it so it stays at the top regardless of sort order. The card's description field supports GitHub-flavoured markdown, the same dialect this document is written in, which is what makes this practical: the content below can be pasted directly into that field and will render.

This was chosen over maintaining a separate accessibility document outside Wekan, the alternative most similar tools default to. A separate document requires a second place to look and a second place to keep current. A pinned card lives inside the tool it describes, is editable by any board admin without touching a repository, and is exactly as discoverable as anything else on the board. The tradeoff is that it is per-board rather than instance-wide; a multi-board instance needs the card pinned on each board, or a decision to point every board's accessibility card at one canonical board instead of duplicating the text. That decision is left to whoever sets up the second board; duplication is the safer default until it becomes a maintenance problem.

Example content for the card description:

```markdown
# Accessibility

This board supports keyboard navigation and is built with accessibility in mind. If something here is not accessible to you, say so, this list improves by being corrected.

## Keyboard navigation

Wekan has a built-in keyboard shortcuts panel, opened from the board sidebar (the `≡` icon, top left). It lists every shortcut for the version currently running, which is the authoritative source since shortcuts have changed across Wekan releases; this card does not duplicate that list; and it will drift out of date if it tries. See also the upstream reference: https://github.com/wekan/wekan/tree/main/docs/Features/Keyboard-Shortcuts

## Visual accessibility

- Labels on this board are always named, not colour-only. Wekan does not currently offer a colourblind-friendly label texture mode (unlike some similar tools), so a label distinguishable only by colour is not accessible; if you add a label, give it a name.
- A dark theme is available from the user profile menu, for anyone who needs reduced screen brightness or finds it easier to read.
- If a colour contrast issue makes something hard to read, report it as a card on this board rather than working around it silently.

## Screen readers and other assistive technology

Wekan is a actively developed web application; screen reader compatibility varies by release and has open issues upstream. If you use a screen reader and hit a wall, report the specific interaction that failed (which page, which control, what you expected) as a card here. A precise report is far more useful than a general one.

## Where this card's claims come from

This card should be corrected the moment it is wrong. It is a living document, not a policy statement, and its accuracy is only as good as the last person who checked it against the running instance.
```

The register above is plainer than the rest of this document deliberately: the audience for a pinned Accessibility card is every board member, not only the technologist setting the board up, so it follows the same plain, direct address this repository's own *Style Guide: Plain Language for General Audiences* calls for, rather than the technical register governing this tutorial itself. Adapt the specific claims (theme names, shortcut panel location) to the version of Wekan actually running before pinning; they are accurate as of the version this tutorial was written against and are exactly the kind of detail most likely to drift.

## Worked example: modeling the OSAT Fluent fleet as a board

This section applies the mechanics above to a concrete case: a single Wekan board that tracks work across every repository in the OSAT Fluent collection, `osat-fluent` itself, `sat`, and every `osat-fluent-<tool>-tool` repository, in one place.

### Deciding what swimlanes and lists represent

The board needs two independent axes: which repository a piece of work belongs to, and how far along that work is. Lists and swimlanes are both available for this, but they are not interchangeable, because only lists imply left-to-right progress. Repository membership is not a stage of progress; a task does not become more done by belonging to a different repository. Workflow stage is. This is why lists were assigned to workflow stage and swimlanes to repository, not the reverse. A board with lists per repository would lose the at-a-glance read of what stage each repository's work is at, which is the whole value of a fleet-wide view.

**Lists** (left to right): `Backlog`, `In Progress`, `Blocked`, `Done`.

**Swimlanes** (top to bottom), one per repository currently in the fleet: `osat-fluent`, `sat`, `sat-doc-automa`, `osat-fluent-sat-tool`, `osat-fluent-rclone-tool`, `osat-fluent-hugo`, `osat-fluent-myrepos-tool`, `osat-fluent-python-tool`, `osat-fluent-wekan-tool`.

A new repository joining the fleet gets a new swimlane. A repository that graduates out of active development does not need to be deleted; an inactive swimlane with no cards in it is harmless and preserves history if it is later reopened.

### Deciding what labels represent

Wekan labels are attached to individual cards and are independent of a card's list or swimlane, which makes them the right tool for a property that cuts across both axes. The five OSAT Fluent design principles:

* Sovereign
* Fluent
* Accessible
* Secured
* Transparent

are exactly that kind of property: a piece of work in any repository, at any stage, can be primarily about one of them.

Five labels, one per principle, let a card be filtered by which principle it most directly serves, independent of which repository or stage it belongs to.

This was chosen over the alternative of a sixth swimlane axis or a custom field, because labels are the one mechanism in Wekan meant to be attached and filtered without affecting a card's position on the board, which is exactly the behaviour wanted here: a principle label should not compete with repository or stage for where the card physically sits.

### Populating the board

Cards below reflect the fleet's actual state, so this is not a hypothetical board but the real starting point for one.

`osat-fluent` swimlane, `In Progress` list:

- Cut and push the `v0.1.0` tag on `steelcj/osat-fluent`, then fetch the tarball, compute its checksum, and pin it into the Cookiecutter demo installer. Label: Transparent, since this exists to give the Cookiecutter template a verifiable, checksummed artifact to install.
- Build the `fluent-tool-cookiecutter` template at `osat-fluent/templates/fluent-tool-cookiecutter/`, whose generated demo installer will itself fetch and install a tagged snapshot of `osat-fluent`, exercising the full Archetype 5 chain end to end. Label: Fluent.

`sat` swimlane, `Backlog` list:

- Resolve the `LICENSE`/`pyproject.toml` mismatch, AGPL text against a declared GPL-3.0-only classifier. Label: Transparent.
- Remove the stale `VERSION.md` reference. Label: Transparent.
- Close the Windows dispatcher gap. Label: Fluent.

`osat-fluent-python-tool` swimlane, `Backlog` list:

- Validate `install.ps1` on real Windows hardware; it is syntax-validated but has not run on actual Windows to date. Label: Accessible.
- Validate on real macOS hardware; platform detection and paths are written but untested. Label: Accessible.

`osat-fluent-wekan-tool` swimlane, `Backlog` list:

- Confirm whether `WRITABLE_PATH` alone controls the FerretDB/SQLite data file location in the bundled release, by reading the actual `start-wekan.sh` after extraction. Label: Secured, since an unverified data path is a data-loss risk on upgrade until confirmed.
- Read the upstream release notes between the `team` mode's pinned version and the current latest, and record a definite answer in the `security_note` field rather than leaving it open. Label: Secured.

`sat-doc-automa` swimlane, `Done` list:

- Establish automa categories, including `en/docs/automa/ai-collaboration/defaults/`. Label: Transparent.

This is a starting point, not a complete backlog. The pattern, one swimlane per repository, one list per stage, principle labels layered on top, extends to every future card without needing a board redesign; only new repositories require a new swimlane, and that is a single board-settings action.

## Backing up board content

Board content backup is a property of the Wekan instance's data directory, not of anything configured through the web interface itself. See the Data and backup section of `wekan-tool--setup-tutorial` for what that means in practice and what has and has not been verified about it.

## Resources

- [wekan-tool--setup-tutorial](wekan-tool--setup-tutorial-v0-1-0.md), installing and running the Wekan instance this tutorial assumes
- Upstream Wekan documentation: <https://github.com/wekan/wekan-doc/wiki>
- Upstream board administration reference: <https://wekan.github.io/wekan-doc/user/Board-Administration.html>

## License

This document, *Wekan: Web Interface Setup Tutorial*, by **Christopher Steel**, with AI assistance from **Claude Sonnet 5 (Anthropic)**, is licensed under the [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html).

## Changelog

| Version | Status | Notes |
|---------|--------|-------|
| 0.2.0 | Draft | Added an Accessibility subsection under board creation: pinned-card convention, example markdown content, and rationale |
| 0.1.0 | Draft | Initial draft, companion to wekan-tool--setup-tutorial |
