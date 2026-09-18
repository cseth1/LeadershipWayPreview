# Aggie Leadership previews

One GitHub Pages website contains both design versions:

- **Version 1: Original** — https://cseth1.github.io/LeadershipWayPreview/
- **Version 2: Aggie UX** — https://cseth1.github.io/LeadershipWayPreview/aggie-ux/

Use the **Website versions** bar at the top of either version to switch. The current version is highlighted. When both versions have the same page, switching keeps you on that page; otherwise it opens the other version's homepage. Existing Version 1 URLs continue to work.

## Source versions

- `Aggie_Leadership_Website 2/dist/` is the original Version 1 source, preserved unchanged from commit `af89d805ee4350fbf6b04ddd4b5649aaaa7761b3`.
- `aggie-ux/` contains the exported Aggie UX website supplied on September 18, 2026. Its source publication was [the Aggie Leadership Hub concept](https://aggie-leadership-hub-concept.vert-mid.chatgpt.site/), publication 11. Its release record is in `versions/aggie-ux-release.json`.
- The GitHub labels Version 1 and Version 2 identify the two designs. They are separate from the source site's publication numbers.

`scripts/build-pages.py` copies both editions into `_site/` and adds the shared version links and `versions/version-switcher.css` to the generated pages. It does not modify either edition's source. Historical redirect pages retain their original behavior. Each version keeps its own styles, scripts, assets, downloads, and navigation. Aggie UX continues to use the official externally hosted Aggie UX 2.1.0 stylesheet and script.

## Preview locally

```sh
python3 scripts/build-pages.py
python3 -m http.server 8000 --directory _site
```

Open http://localhost:8000/ for the original and http://localhost:8000/aggie-ux/ for Aggie UX. Building requires only Python's standard library.

The existing GitHub Pages workflow builds and deploys `_site/` whenever `main` changes. To update the Aggie UX design, replace the website files inside `aggie-ux/` and update its release record; leave the Version 1 folder intact. The separate ChatGPT-hosted site is not changed by this repository.
