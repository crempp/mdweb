/*
Title: The Page Object
Nav Name: Page
*/

#Page Object
The page object contains all the data related to a page. The rendered page
is also cached in this object.

* *path:* The filesystem path to the page (relative to the content directory).

* *url_path:* The URL path to the page.

* *meta_inf:* The page meta-information.

* *markdown_str:* The raw markdown for the page.

* *page_html:* The page content after rendering the markdown.

* *page_cache:* Then entire rendered page including the dependant layout.
