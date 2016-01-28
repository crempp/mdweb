# Download MDWeb

MDWeb is ready for you to use.

<a href="https://github.com/crempp/mdweb" target="_blank">MDWeb on Github <img src='/static/images/github.png'></img></a>

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