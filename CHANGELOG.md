# Changelog

## 1.2.0 — maintained fork

- Identify the fork as HLM UKHO Tides, with its own source and issue tracker;
  retain `ukho_tides` internally for migration compatibility.
- Add automated tests and a manual workflow to prepare tested draft releases.
- Remove deprecated config-flow connection class; declare cloud polling in the manifest.
- Use the current HA-managed options-flow config entry instead of assigning its read-only property.
- Keep options edits separate from running configuration and return a form on station-download failure.
- Handle empty/expired event lists without indexing errors, mark expired predictions unavailable, clear expired next-event attributes and retain full countdown hours beyond 24 hours.
- Preserve the integration domain, station unique IDs, UKHO client version, API/account data and existing sensor attribute format.
- No change to UKHO subscriptions, high/low prediction source, station offsets or dashboard interpolation.
