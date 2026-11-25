# Maintained fork and upstream return plan

This fork starts from Ian Byrne's MIT-licensed integration, upstream commit
`4a62c25` (version 1.1.2). The original license and history are retained.
The `upstream` Git remote tracks the original repository. No UKHO service or
prediction algorithm is replaced.

The owner has reported the compatibility problem in
[upstream issue #43](https://github.com/ianByrne/HASS-ukho_tides/issues/43).
Keep that issue as the place to track an upstream response.
The existing upstream compatibility monitor should remain active. An upstream
patch is a candidate for review, not a trigger for automatic installation.

Our maintained source is [mark4068-dotcom/UKHO-Tides](https://github.com/mark4068-dotcom/UKHO-Tides),
with `main` as the default branch and **HLM UKHO Tides** as the display name.
The local checkout is `/Users/mark/Documents/GitHub/UKHO-Tides`.
Its `origin` remote points to our repository and `upstream` to Ian Byrne's.
Push compatibility checks run on GitHub Actions; the manual **Prepare release**
workflow builds an installation ZIP and creates a draft release after tests.
Publish that draft only after target-version and live checks pass.

## Compatibility contract

- Keep domain `ukho_tides`, config-entry version 1, station-based unique IDs,
  existing account details, station names and configured offsets.
- Keep `predictions` as timestamp/height pairs and existing next-tide attribute
  names and units. Keep the pinned `ukhotides==1.1.2` client for this patch.
- Empty or exhausted forecasts become unavailable instead of raising an index
  error or retaining old next-tide attributes.
- No change to beach interpolation, the 1.9 m threshold, or the 15-minute margins.
- High/low predictions remain predictions; this fork adds no measured-height or
  interval-height data.

## Staged deployment

1. Run the regression suite on the target Home Assistant Python/Core version.
   The initial local test environment is Core 2026.2.3; production is 2026.11,
   so local success alone does not establish production compatibility.
2. Back up `/config/custom_components/ukho_tides` and a Home Assistant backup.
   Capture the Cowes entity ID, availability, prediction pairs, next-tide
   attributes and all dependent beach displays before deployment.
3. Settle the update source before installing: an update from the original HACS
   repository can overwrite a manually installed fork. Use one repository for
   this domain, and retain the upstream remote for comparison.
4. Replace only integration files. Keep the existing integration entry and
   station configuration; do not remove/recreate the integration or edit its
   storage records. Restart Core in a maintenance window.
5. Verify startup without the deprecated connection-class warning, open the
   options flow without saving, and confirm Cowes identity and predictions.
   Check all seven beach cards across HLM, Topgallant, Home Kiosk and the welcome
   page. Confirm displayed times agree and settings remain 1.9 m / 15 minutes.
6. Observe at least one API refresh and the next tide transition. If validation
   fails, restore the saved integration directory and restart Core.

## Returning to upstream

Fetch `upstream`, inspect its patch and compare it against this branch. Confirm
that the removed `CONN_CLASS_CLOUD_POLL` constant and read-only options-flow
property are both addressed. Review any entity ID, schema, attribute or client
dependency changes. Run these regression tests against the candidate upstream
code before accepting it.

If its identity/schema contract remains compatible, return by replacing the
integration files and switching HACS to the upstream repository; retain the
same config entry. Repeat the deployment checks above. Keep the fork available
until the upstream version has passed live observation. There is no need to
maintain a separate API key or recreate dashboard entities solely to switch
between compatible versions.

## Development

Use Python 3.13 in an isolated environment:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use synthetic events and a mocked API; they need no credentials or UKHO
requests. Do not store API keys,
Home Assistant backups or live config-entry exports in this repository.
