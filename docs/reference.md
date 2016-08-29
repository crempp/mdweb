# Reference

## Navigation Object


The navigation object is available within page templates and provides the
site navigation structure as well as access to the page objects.

The navigation template object is provided by the NavigationLevel class and has
the following attributes available.

* *name:* Section name. This is the lower case name extracted from the 
directory path.

* *page:* The page object for this navigation level.

* *path:* A short-cut to the filesystem path to the page (relative 
to the content directory).

* *order:* A short-cut to the page order for this navigation level.

* *meta:* A short-cut to the page meta-information.

* *children:* A dictionary containing the child NavigationLevel objects.

## Page Object


The page object contains all the data related to a page. The rendered page
is also cached in this object.

* *path:* The filesystem path to the page (relative to the content directory).

* *url_path:* The URL path to the page.

* *meta_inf:* The page meta-information.

* *markdown_str:* The raw markdown for the page.

* *page_html:* The page content after rendering the markdown.

* *page_cache:* Then entire rendered page including the dependant layout.

## System Events


The following is an overview of the site start-up process including the
subscribable events. The following process occurs in the order it's presented
in.

1. *pre-boot:* Triggered at the beginning of the Site instantiation. The only
thing that has happened at this point is signal creation.

2. **\[ Internal pre-boot logic occurs \]**

3. *pre-app-start:* Triggered before the Flask application is created.

4. **\[ Flask application is created, routes are registered, error handlers
are registered and logging is started \]**

5. *post-app-start:* Triggered after the application has been created.

6. *pre-config:* Triggered before the configuration is loaded.

7. **\[ Config loaded and added to Flask application, theme folder is setup,
meta-inf regex is compiled \]**

8. *post-config:* Triggered after the configuration is loaded.

9. *pre-content-scan:* Triggered before the content directory is scanned.

10. **\[ The content directory is scanned and pages are created for each content
file, the navigation object is created and the navigation context processor is
created \]**

11. *post-content-scan:* Triggered before the content directory is scanned.

12. **\[ Internal post-boot logic occurs \]**

13. *post-boot:* Triggered after all site setup is complete and the application
is ready to start handling requests.
