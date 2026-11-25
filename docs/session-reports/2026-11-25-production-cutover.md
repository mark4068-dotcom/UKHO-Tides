# Production cutover — 25 November 2026

## Result

Production Home Assistant Core 2026.11.2 now uses HLM UKHO Tides 1.2.1 from
`mark4068-dotcom/UKHO-Tides`. The release source commit is
`5e8a50a61408b4f4b759028b1ef9cc0e96656ac1`. The original repository was removed
from Marketplace; future releases are tracked through `update.hlm_ukho_tides`.

## Recovery and migration

The user explicitly accepted the Marketplace warning, then approved the
configuration backup and remove/recreate migration required by Marketplace.
Backup `e2b74afd`, **Before HLM UKHO Tides cutover 2026-11-25**, completed with
Home Assistant configuration and SSL included, without recorder database or apps.
It uses the instance's default backup password.

A separate exact copy of the previous integration and private account settings
is retained on the HA host under
`/config/hlm-backups/ukho-fork-cutover-20261125T153001Z/`. The account snapshot is
mode 0600 and has not been committed or exported. Roll back code using the saved
original directory and a Core restart; changing the managed repository back also
requires the entry/source migration. Any full configuration restore requires
separate approval because it reverts unrelated configuration changes too.

Marketplace correctly refused to uninstall the original while its config entry
existed. Following approval, the entry was removed through the API, its original
repository uninstalled, and our fork installed. After restart, the normal config
flow recreated Cowes using the same API account, Discovery tier, station `0060`,
name `COWES`, and zero high/low time offsets. No HA storage files were edited.

The config entry changed from `01M0AA7Y4TEK07SP59EFV4EEXA` to
`01M89PBZ0SK8G043C3PCTDD05C`. The public identity remains `sensor.cowes_tide`,
unique ID `0060`, platform `ukho_tides`, display name `COWES Tide`. Its registry
name, area, labels, aliases, enabled state and voice exposure match the baseline.

## Validation

- Seven regression checks pass locally against Core 2026.11.2 / Python 3.14.
  Both GitHub compatibility and release workflows pass on the same versions.
- The clean environment exposed an undeclared `async_timeout` dependency.
  Version 1.2.1 uses Python's built-in `asyncio.timeout` instead.
- All 39 prediction timestamp/height pairs match the pre-cutover snapshot.
  Next high and low timestamps and heights also match. State is available.
- The options form opens with no errors; the test flow was cancelled without
  saving. Account key, API tier and station settings were compared privately and
  are unchanged.
- Browser checks show the HLM tide summary and seven-day curve, Topgallant
  overview and tide detail, Home Kiosk overview and tide detail, and Topgallant
  kiosk welcome and weather pages rendering the same data.
- The seven beach displays retain the existing 1.9 m threshold and 15-minute
  margin at each end. On this date their displayed window is 15:34–18:47,
  duration 3 h 13 min. No interpolation changes were made.
- The initial post-cutover log check contains no UKHO errors or deprecated
  connection-class warning. The unplugged voice device warning is expected.
- Version 1.2.1 was published after live validation, then installed by tag so
  Marketplace follows releases rather than the main branch. Marketplace required
  a final restart after this tag install, despite identical integration files.
- After that final restart, Cowes remains available with 39 predictions,
  `update.hlm_ukho_tides` reports installed/latest `v1.2.1`, the restart repair
  is gone, and the log contains only the expected unplugged voice warning.
  All 20 dashboard-reference matches retain their original configuration hashes.

Separate observation: Home Kiosk's overview contains two missing EV/car entity
tiles unrelated to tides; those were left unchanged. Longer-term observations
over subsequent hourly API refreshes are outside the immediate deployment check.

## Upstream

Continue watching upstream issue #43 and releases. An upstream fix can be
evaluated against this fork's compatibility tests and returned to through the
same managed source-switch process. Ordinary updates to our fork do not need to
remove/recreate the config entry.
