# Team workbook

`Leadership_Website_Content.xlsx` is the initial workbook extracted from the website. Once enabled, the shared OneDrive or SharePoint copy is the master. The copy here is a starting template, not an automatically synchronized backup.

The workbook contains 71 programs and opportunities (11 also appear in the course catalog), 52 resources, 69 featured placements, existing page wording and existing page links. Existing provider review dates are preserved. This export is not a new verification of provider availability.

Team members edit the master in Excel and save. The website checks it hourly, at 17 minutes past the hour; GitHub may delay scheduled runs. Both editions and their CSV downloads are rebuilt from the same data. Invalid changes stop the deployment and leave the last successful website online. GitHub Actions displays the validation error, including the affected row or record where available. An expired or revoked link stops publishing rather than restoring old catalog content.

## One-time connection

The folder link alone is not the file download connection. Upload the workbook, then use its existing OneDrive/SharePoint file-sharing link. Do not commit a private sharing link, access token or credential to this public repository.

For a workbook link that already allows automated download, store the file link in the repository Actions secret `LEADERSHIP_WORKBOOK_URL`. The downloader requests the Excel file and rejects login pages. Test the exact link before enabling publishing. Do not change the library or file permissions merely to satisfy this option.

For a workbook that requires organizational sign-in, the Microsoft 365 administrator can authorize an Entra application to read only the selected site or file and supply these repository Actions secrets:

| Secret | Value |
| --- | --- |
| `MS_TENANT_ID` | Microsoft tenant identifier |
| `MS_CLIENT_ID` | Authorized application identifier |
| `MS_CLIENT_SECRET` | Application secret, stored only in GitHub Secrets |
| `MS_DRIVE_ID` | Drive containing the shared master |
| `MS_ITEM_ID` | File item identifier for the workbook |

The app requires Microsoft Graph application permission and a resource-specific read grant. Microsoft documents selected permissions for sites, libraries and files; use the narrowest approved scope rather than granting tenant-wide access. The code never writes to Microsoft 365. If organizational policy requires certificate or federated identity authentication, adapt the token acquisition to that approved method before enabling the workflow.

After the connection is configured, set the repository Actions variable `CONTENT_SYNC_ENABLED` to `true` and run **Deploy GitHub Pages** manually once. Confirm the deployment and both website versions. The hourly schedule then continues automatically. To pause updates, set the variable to `false`; avoid a new main-branch deployment while paused because the existing source-version build remains the fallback for that explicit deployment. Scheduled checks skip while disabled.

## Editing

- Keep worksheet names, the row-6 column headings and stable IDs.
- Add catalog rows with unique IDs. Copy a similar row as a starting point and set `Publish` to `No` until the public fields are ready. Set `Publish` to `No` to withdraw an item.
- Programs and courses share one row per item. `Show on course page`, `Course area` and `Sort hours` control the course view.
- Use semicolons between audience or journey labels. `Journey stages` controls the live discovery mapping; `Source stages` and `Source audience` preserve the original research labels.
- The eight existing resource topics correspond to the eight Aggie UX topic pages. Creating a new topic or a new page is a website change.
- Featured Content chooses items by ID for each version and journey page. Blank overrides follow the main record. Existing intentional abbreviated titles or editorial descriptions are preserved in override columns.
- Page Text and Page Links update existing main-body wording, page titles/descriptions and links, including calendars. Keep their IDs and context columns and edit only the value column. Navigation, layout and imagery remain in the website files.
- Content fields are literal text, not Excel formulas or HTML. The publisher escapes text and rejects executable links.

## Maintainer validation

```sh
python3 -m pip install -r scripts/requirements-content.txt
python3 scripts/test_content.py
python3 scripts/build-pages.py --workbook content/Leadership_Website_Content.xlsx
python3 -m http.server 8000 --directory _site
```

The build changes generated `_site/` files only. Source editions remain unchanged. `bindings.json` records the source layouts and stable text/link targets. If source HTML changes, update the workbook mappings deliberately; the source hash check prevents quietly applying old IDs to the wrong page element. `prepare-content-data.py` extracts a fresh baseline for that maintenance operation; it does not merge existing shared workbook edits, so do not rerun it as a routine content refresh.

References: [Microsoft Graph file download](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0), [selected Microsoft Graph permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview), [GitHub scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
