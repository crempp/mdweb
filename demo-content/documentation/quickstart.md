```metainf
Title: MDWeb Quick Start
Nav Name: Quick Start
Description: How to quickly get MDWeb running
Order: 1
Teaser: Learn how to setup MDWeb in 5 minutes or less. Step-by-step
    instructions are given.
Sitemap Priority: 0.5
Sitemap Changefreq: monthly
```

# Quickstart

## Requirements
* Python 2.7 or 3.x
* Pip
* Virtualenv (optional, highly recommended)


## General usage guidlines

* Fork the repository.

* Clone your forked repository on your local machine.

* Copy `sites/MySite.py.example` to `sites/MySite.py` or what ever name you 
  choose for your site class. Inside the copied file rename the class to match
  the file name - for example if you call the file `JoesSite.py` the Class
  should be named `JoesSite`.
  
* Update the config attributes in the site class, specifically `THEME` and 
  `CONTENT_PATH` (I suggest using the provided, empty, `content` directory).
  The `demo-content` directory is provided with example content to get you 
  started. 
  
* Add your content to the content directory defined.

* (optional) Create a new theme for your site in the `themes` directory. If 
  you add a new theme remember to update the THEME config value.

* Run the application (assuming you have a virtual environment setup). The
  dev_server script has one required parameter which is the site class name,
  in the example about the class name was `JoesSite`.


## Quick setup
* Setup a virtual environment and activate
```
$ virtualenv mymdwebenv
$ source ./mymdwebenv/bin/activate
```
* Clone the project
```
$ git clone git@github.com:crempp/mdweb.git
```
* Go into the directory
```
$ cd mdweb
```
* Install requirements
```
$ pip install -r requirements.txt
```
* Setup site class
```
$ cp sites/MySite.py.example sites/JoesSite.py
$ nano sites/JoesSite.py
# Edit the class name and config as described above
```
* Run the server
```
$ ./bin/dev_server JoesSite
```

Now visit [http://127.0.0.1:5000](http://127.0.0.1:5000)
