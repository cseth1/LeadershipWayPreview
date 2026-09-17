# Leadership at Texas A&M | Design concept

Employee-first website with four main pages: The Aggie Way home page (index.html), Programs & Opportunities (programs.html), a resource library (toolkit.html), and courses/calendar (professional-development.html).

Open dist/index.html locally or serve dist with a static web server. Fonts and core imagery are local; provider links require internet access.

The public opportunity catalog lives in dist/data.js. The 52 published resource records live in dist/toolkit-data.js. Two additional historical document links remain in the research workbook for access confirmation. Both public catalogs are available as CSV files. Historical TrainTraq metadata stays in the research workbook. No enrollment or completion tracking is implemented.

Visual references: jobs.tamu.edu, www.tamu.edu and its facts page, and A&M's published Aggie UX / font / web-color guidance. The mockup matches published defaults but is not the university's production Aggie UX installation. Use current approved components with the campus web team for official implementation.

Typography: locally hosted Open Sans, Oswald and Work Sans from Google Fonts. OFL licenses are in dist/assets. University wordmarks are unchanged files from tamu.edu. The campus photograph is credited to https://news.tamus.edu/stories/regents-unanimously-approve-academic-building-restoration/. Confirm official asset and content review before public university launch.

The resource library preserves HROE's curation and labels external publishers. Direct-link availability and playback have not all been individually verified. Dates and registration remain with the official calendar and providers. Journey stages, topic groups and practice examples are proposals. Research checked September 16, 2026.

## The Aggie Way page

Added September 17, 2026. The dedicated narrative page follows the supplied Brand-Guide.pdf: messaging themes and voice (pages 18–22, 39–42), typography (52–58), primary/secondary colors (59–61), emphasis boxes and supporting linework (67–68). It retains the shared site header, navigation and footer. Existing opportunity, toolkit and course data are unchanged. The prior index.html#aggie-way anchor now opens the narrative hero on the home page.

The purpose statement is excerpted from https://www.tamu.edu/about/purpose-values.html. Core Value descriptions and 12 principles are concise paraphrases; workplace examples are proposed editorial content. The president’s source is https://president.tamu.edu/presidential-priorities/index.html.

Hero photograph: Texas A&M Engineering, https://engineering.tamu.edu/news/2025/06/department-head-nationally-recognized-for-mentorship-impact.html. It shows Sarah Lam presenting her team’s RAD Exploration Vehicle to Guillermo Aguilar. Source image: https://engineering.tamu.edu/news/2025/06/_news-images/News-MEEN-RADLab-24June2025.jpg. All-rights-reserved university source; reused in this private design concept with credit. Obtain institutional asset/content clearance before an official public launch. The user-supplied brand guide itself is not uploaded or bundled.

## Hub polish and audience behavior

The final September 17, 2026 treatment carries the Aggie Way narrative, brand type, maroon/white palette, emphasis boxes and supporting linework across all four pages. Discovery controls are placed before supporting stories.

A shared discovery engine combines filters using AND logic. Search is case-insensitive and matches every entered word across titles, descriptions, provider, topic and audience labels. Employees includes the 36 employee offerings; staff and faculty are explicit relevance tags. Faculty includes both academic and shared employee learning; Faculty-focused learning selects 20 academic offerings, 2 academic courses or the faculty mentoring toolkit. Supervisor relevance is explicitly curated by offering instead of inferred at runtime from the provider. Student, System/agency and external programs remain separate. All 71 opportunities, 52 published resources and 11 course rows are retained. Source eligibility, costs and dates are unchanged. Resource descriptions receive only the grammar correction “A article” to “An article.”

Audience follows internal navigation without cookies or browser storage. Relevant filters are encoded in the URL. Development-goal and topic buttons preserve the other selected filters; Clear filters restores the default employee view. Result chips can remove a single filter. Explicit role tags describe discovery relevance and do not establish eligibility. Course results show the provider’s eligibility text, including faculty and academic-staff restrictions.

Primary sources rechecked for audience interpretation: HROE Leadership Development (article 1587), The Leadership Collective (1709), Recommended Resources for Supervisors (1625), Faculty Affairs faculty/leadership development, Successful Conflict Conversations, Third-Party Conflict Resolution for Leaders, and CTE faculty/graduate mentoring.

Validation: 1,425 filter combinations checked against the catalog, with all original records retained and source fields preserved apart from the documented grammar correction. Local browser checks covered combined filters, faculty/staff separation, focused academic results, cross-page audience carryover, empty states, resets, individual filter removal, pagination, course details, compact navigation, student separation and filter restoration after refresh. This is functional validation, not a comprehensive accessibility or visual audit.

## Home page and program navigation

The Aggie Way is the default index.html landing page. The former home page, including its catalog, search, audience filters and learning pathways, now lives at programs.html. Shared navigation has one home destination, labeled The Aggie Way, and a distinct Programs & Opportunities destination. Older aggie-way.html links forward to the new home while retaining query strings and section anchors. Older index.html#opportunities, #journey and #resources links, and catalog-specific query parameters, forward to programs.html. Audience-only parameters stay on the narrative home and carry into the program catalog. All catalog and toolkit data and filtering behavior are preserved.
