# Development

This section is intended primarily for those who wish to build themes 
or plugins. This section is still a work in progress but will stabalize
after the plugin architecture is completed and as we approach the 1.0 
release.


## Building a Theme

Themes are composed of the HTML templates and assets required for a 
site's display. Themes can be as simple or as complicated as you'd like.

Theme HTML is rendered using the [Jinja](http://jinja.pocoo.org/docs/dev/)
templating engine. All functionality available in Jinja is available to
you in MDWeb theme files. 

To build a basic them you will need to 
1. Create a directory whose name is the name of your theme
2. Create a subdirectory named 'templates'
2. Create a subdirectory named 'assets'
3. Create a template named layout.html in the templates directory
4. Create a template named page.html in the templates directory
5. Create a template named navigation.html in the templates directory
6. Add any CSS, Javascript or images into the assets directory.


#### Example:

```
themes/
    |- mytheme/
        |- templates/
            |- layout.html
            |- page.html
            |- navigation.html
        |- assets/
            |- site.js
            |- site.css
            |- logo.png
```


#### Assets

Assets can be placed in the `<<mytheme>>/assets` directory using any 
structure. The asset path is referenced in the templates by using the 
`url_for` helper.

For example, this line in the layout.html file will load the minified 
bootstrap CSS from the css directory in assets.
```
<link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
```


#### Using your theme
To use your theme make sure the theme directory is located within 
`themes` inside the MDWeb project and then set the `THEME` configuration
value to the the name of your theme directory.


## Building a Plugin

The plugin architecture is not yet completed this section will be added
once plugins are supported.


## Adding Meta Fields

Currently new meta fields must be registered or they will throw a 
`PageMetaInfFieldException` exception. Unfortunately meta fields must
be registered in the core of MDWeb. I hope to change this once the
plugin architecture is completed.

Meta field names are capital-cased and space separated in the markdown 
metainf block, for example `Nav Name`. These capital-cased, space
separated meta field names are converted to camel-cased, underscore
separated dictionary keys within the code.

To register a meta field in MDWeb core:
1. Decide on a capital-cased and space separated name to be used in the
metainf block, for example `Co Author`. This is the field name that
will be used in markdown files metainf block. For example
~~~
```metainf
Title: Breaking News
Author: Jean Luc Picard
Co Author: Will Riker
```
~~~
2 Add an entry to the META_FIELDS dictionary in mdweb/metafields.py.
This dictionary has the following structure
```
META_FIELDS = {
    'camel_cased_field_name': ('python_type', default_value)
}
```

the camel-cased version of the name to 


## Testing

MDWeb uses nose as the test runner. Running tests are as simple as
```
$ nosetests
```
