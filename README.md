#Markdown based web site framework

MDWeb is painstakingly designed to be as minimalistic as possible while taking less than 5 minutes to setup and less than one minute to add content.

This project was borne out of my frustration with maintaining websites and adding content. I'm a firm believer in the ethos that CMS is an evil that should be rid from this world. I spent years fighting horrific battles with enemies such as Drupal, Wordpress and Joomla. The things I saw during those dark days can not be unseen.

After years of battle, this weary web development soldier built himself a a tiny oasis. This is MDWeb, I hope you find respite in it.

## Requirements
* Python 2.7+, 3.x
* Pip
* Virtualenv (optional)

## How to use

* Fork the repository.

* Clone your forked repository on your local machine.

* Copy `SiteConfig.py.example` to `SiteConfig.py`. Edit the config according
  to your needs.
  
* Copy `Site.py.example` to `Site.py`. Edit the config according to your
  needs.
  
* Add your content to the content directory.

* Edit (or add) your theme. If you add a new theme update the THEME config
  option.
  
* Run the application (assuming you have a virtual environment setup)
```
$ source ./venv/bin/activate
$ python Site.py
```

## Quick setup
* Setup a virtual environment and activate
```
$ virtualenv venv
$ source ./venv/bin/activate
```
* Clone the project
```
$ git clone https://bitbucket.org/crempp/mdweb.git
```
* Go into the directory
```
$ cd mdweb
```
* Install requirements
```
$ pip install -r requirements.txt
```
* Run the server
```
$ python Site.py
```

Now visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Documentation

###Content

Site content is simply markdown formatted files. Each page on the site has it's
own file and the directory structure defines the navigation.

The content files currently support standard markdown with the addition of a
meta-information section at the beginning of each file which is parsed during
the content scan.

###Navigation Structure

Each directory under /content defines a section in the navigation structure.
If a file named index.md exists in the directory it is used as the landing page
for that section in the navigation. The index.md file in the root of the
content directory is the "home" page. Note that the navigation template
currently only supports one level of nesting, support for deeper navigation
levels could easily be added by updating (overriding) the navigation template.

```
For example:
    content/
        |- index.md               Home page
        |- articles/
               |- index.md        Articles section landing page
               |- foo_article.md  Page located in Articles->Foo Article
        |- examples/
               |- index.md        Examples section landing page
        |- help/
               |- index.md        Help section landing page
               |- how_to.md       Page located in Help->HowTo
```

###Content Meta Fields
* *Title:* The page title. In the provided templates this will be used in the
`<title>` tag and in the page header.

* *Nav Name:* The name that will appear in the navigation

* *Description:* The page description. In the provided templates this will be
used in meta description tag.

* *Author:* The page author. This is useful for blog posts and articles.

* *Date:* The page creation date. This is useful for blog posts and articles.

* *Order:* The order the page will appear in navigation.

* *Template:* The template to use for page rendering. Defaults to page.html

###Navigation Object
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

###Page Object
The page object contains all the data related to a page. The rendered page
is also cached in this object.

* *path:* The filesystem path to the page (relative to the content directory).

* *url_path:* The URL path to the page.

* *meta_inf:* The page meta-information.

* *markdown_str:* The raw markdown for the page.

* *page_html:* The page content after rendering the markdown.

* *page_cache:* Then entire rendered page including the dependant layout.

###System Events
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

## Credits
* Alpha theme modified from the [Alpha site template](http://html5up.net/alpha) on [html5up.net](http://html5up.net).
This site template was licenced under [CCA 3.0](html5up.net/license)
