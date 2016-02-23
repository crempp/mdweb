/*
Title: The Navigation Object
Nav Name: Navigation
*/

#Navigation Object
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
