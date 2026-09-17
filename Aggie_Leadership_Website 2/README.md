# Aggie Leadership | Employee Development Hub

This export contains the published **version 7**, released September 17, 2026.

Live site: https://aggie-leadership-hub-concept.vert-mid.chatgpt.site
Published website commit: `d511c89849dda6e118018cd24a47dde8d1e049b0`

## What is included

- **Leadership Hub** (`dist/index.html`): restored resource-hub layout, six leadership stages, search and opportunity discovery. Each homepage “Explore this stage” link opens courses, programs and communities for that stage.
- **The Aggie Leadership Way** (`dist/aggie-way.html`): the retained values, principles and everyday-behavior content.
- **Your Leadership Journey** (`dist/journey.html`): stage selection, “What does your work ask of you now?”, a resource-focused learning cycle and links to development support.
- **Six stage guides**: Start at A&M, Lead Yourself, Lead People, Lead Teams, Lead Across A&M and Develop Others. Each emphasizes “Learn with a purpose” and “Tools to support your development.”
- **Learning & Experiences** (`dist/programs.html`) and **Courses & calendar** (`dist/professional-development.html`): searchable learning options and provider registration links.
- **Tools & Resources** (`dist/toolkit.html`): the searchable resource library, with audience, stage, topic, format and source filters.

The Academy and practice-plan interfaces are removed. The small `academy.html` and `practice.html` files redirect old links to the Journey and resource library. They are not Academy or assignment pages. There is no enrollment, assignment or completion tracking.

## View or edit locally

The editable website is in `dist/`. HTML, CSS, JavaScript, fonts, images and downloadable CSV catalogs are included. No build step is required.

For full navigation and filters, serve `dist/` with a local static web server. For example, from this folder:

```sh
python3 -m http.server 4173 --directory dist
```

Then open http://localhost:4173. Stop the server with Control+C. Provider websites and registration links require internet access.

Site hosting settings are in `.openai/hosting.json`. The existing site's sharing settings are managed in Sites and are not changed by unzipping these files.

## Catalog and source information

The 71 opportunity records (including 36 employee offerings) and 11 course rows are in `dist/data.js`. The 52 published resource records are in `dist/toolkit-data.js`. Downloadable catalogs are `leadership-opportunities.csv` and `leadership-resources.csv`.

The research catalogs, provider eligibility, fees, dates and source links are preserved. Six-stage connections in `journey-map.js` are editorial discovery guidance; they do not establish program eligibility. Audience and other filters combine, and selected audience context follows internal navigation. Providers retain responsibility for registration and availability.

The separate research workbook is not included in this website ZIP and has not been changed by the version 7 website revision. Historical TrainTraq metadata and two historical document links requiring access confirmation remain in that workbook.

## Branding and attribution

The site retains its Texas A&M maroon/white palette, local Open Sans, Oswald and Work Sans fonts, and existing university wordmarks. Font licenses are in `dist/assets/`. This is a private design concept, not the university's production Aggie UX installation.

The mentorship image shows Sarah Lam presenting the RAD Exploration Vehicle to Guillermo Aguilar. Its source is Texas A&M Engineering: https://engineering.tamu.edu/news/2025/06/department-head-nationally-recognized-for-mentorship-impact.html. The source image is https://engineering.tamu.edu/news/2025/06/_news-images/News-MEEN-RADLab-24June2025.jpg.

The retained campus image is attributed to https://news.tamus.edu/stories/regents-unanimously-approve-academic-building-restoration/. University images are retained for this private design concept; institutional asset and content review remains part of any official university launch.

Purpose and values source: https://www.tamu.edu/about/purpose-values.html. Guiding-principle source: https://president.tamu.edu/presidential-priorities/index.html. Workplace behavior examples and stage connections are proposed editorial content. The source brand guide is not bundled.

## Validation for version 7

All 14 HTML files, local assets and internal section links were checked. JavaScript syntax checks passed. The original research catalogs and shared brand files were preserved, and the Aggie Leadership Way main content is unchanged.

Local browser checks covered homepage stage filtering, the stage guide, offering details, stage-filtered resources, a Journey resource-format link, mobile navigation and horizontal overflow on the checked pages. The deployment reported success for version 7. External provider links and video playback have not all been individually rechecked; confirm current information with each provider.
