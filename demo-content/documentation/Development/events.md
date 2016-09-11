/*
Title: Event Hooks
Nav Name: Event Hooks
Description: MDWeb Event Hooks
Order: 4
Teaser: MDWeb system event hook reference. Useful reference for writing
    plugins.
Sitemap Priority: 0.5
Sitemap Changefreq: monthly
*/

#System Event Hooks

The following is an overview of the site start-up process including the
subscribable events. The following process occurs in the order it's presented
in.

1. *pre-boot:* Triggered at the beginning of the Site instantiation. The only
thing that has happened at this point is signal creation.

2. \[ Internal pre-boot logic occurs \]

3. *pre-app-start:* Triggered before the Flask application is created.

4. \[ Flask application is created, routes are registered, error handlers
are registered and logging is started \]

5. *post-app-start:* Triggered after the application has been created.

6. *pre-config:* Triggered before the configuration is loaded.

7. \[ Config loaded and added to Flask application, theme folder is setup,
meta-inf regex is compiled \]

8. *post-config:* Triggered after the configuration is loaded.

9. *pre-content-scan:* Triggered before the content directory is scanned.

10. \[ The content directory is scanned and pages are created for each content
file, the navigation object is created and the navigation context processor is
created \]

11. *post-content-scan:* Triggered before the content directory is scanned.

12. \[ Internal post-boot logic occurs \]

13. *post-boot:* Triggered after all site setup is complete and the application
is ready to start handling requests.
