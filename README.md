# Markdown based web site framework [![Code Health](https://landscape.io/github/crempp/mdweb/feature/PylintCleanup/landscape.svg?style=flat)](https://landscape.io/github/crempp/mdweb/feature/PylintCleanup) [![CircleCI](https://circleci.com/gh/crempp/mdweb/tree/develop.svg?style=svg)](https://circleci.com/gh/crempp/mdweb/tree/develop)

![Demo](docs/images/MDWeb_logo_275x190.png?raw=true)

MDWeb is painstakingly designed to be as minimalistic as possible while taking 
less than 5 minutes to setup and less than a minute to add content.

This project was borne out of my frustration with maintaining websites and 
adding content. I'm a firm believer in the ethos that CMS is an evil that 
should be rid from this world. I spent years fighting horrific battles with 
enemies such as Drupal, Wordpress and Joomla. The things I saw during those
dark days can not be unseen.

After years of battle, this weary web developmer built himself a tiny oasis.
This is MDWeb, I hope you find respite in it.

You can see a live demo of MDWeb here: [http://mdweb.lapinlabs.com/](http://mdweb.lapinlabs.com/ )

## Requirements


* Python 2.7 or 3.x
* Pip
* Virtualenv (optional, highly recommended)

## Forking for your own site


The suggested method for using MDWeb and also tracking any udpates you make for
your own site is to fork the MDWeb repository. Any changes you make will be
commited to your personally forked repository and you'll be able to pull down
upstream changes by following the procedure outlined here 
[How to update a GitHub forked repository?](http://stackoverflow.com/a/7244456/1436323)

## Quickstart


For more ways to run MDWeb see [Setup](docs/setup.md) and [Basic Usage](docs/basic_usage.md).

1. Fork the Github repository.
2. Clone your forked repository on your local machine.
3. Go into the directory
```
$ cd mdweb
```
4. Setup a virtual environment and activate
```
$ virtualenv env
$ source ./env/bin/activate
```
5. Install requirements
```
$ pip install -r requirements/development.txt
```
6. (Optional) Copy `sites/MySite.py` to `sites/<<NameOfYourSite>>.py`. Inside the copied file rename the class to match the file name - for example if you call the file `JoesSite.py` the class should be named `JoesSite`. If you choose not to copy to a new file continue to the next step using `sites/MySite.py`.
```
$ cp sites/MySite.py sites/JoesSite.py
$ nano sites/JoesSite.py
# Edit the class name and config as described above
```
7. (Optional) Create a new theme for your site in the `themes` directory. If you add a new theme remember to update the THEME config value in the next step.
8. Update the config attributes in the site class, specifically `THEME` and `CONTENT_PATH` (I suggest using the provided, empty, `content` directory). The `demo-content` directory is provided with example content to get you started. Add your content to the content directory defined.
9. Run the application. The dev_server script has one required parameter which is the site class name. If you copied the site file in step 6 the site name will be the name you used in that step (`JoesSite`) otherwise it will be the default site name `MySite`.
```
$ ./bin/dev_server JoesSite
```

Now visit [http://127.0.0.1:5000](http://127.0.0.1:5000) and you should see your site.

## Documentation

* [Setup](docs/setup.md) - How to get MDWeb running locally or in Docker either in development or production environments
* [Basic Usage](docs/basic_usage.md) - How to use MDWeb to host your site
* [Development](docs/development.md) - How to build themes and plugins for MDWeb
* [Reference](docs/reference.md) - API and core framework reference
* [Contributing](docs/contributing.md) - How to report bugs and contribute to the development of MDWeb

## License

MIT © [Chad Rempp](https://github.com/crempp/mdweb/blob/master/LICENSE.txt)

## Credits

Some portions of MDWeb uses other F/OSS content. Below is a sourced list of content used in MDWeb.
* Alpha theme modified from the [Alpha site template](http://html5up.net/alpha) on [html5up.net](http://html5up.net).
This site template was licensed under [CCA 3.0](html5up.net/license)
* Bootstrap theme modified from [Bootstrap examples](http://getbootstrap.com/getting-started/#examples).
The Bootstrap examples are licensed under the [MIT License](https://github.com/twbs/bootstrap/blob/master/LICENSE).
