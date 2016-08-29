# Setup

## Development
----

### Prerequisites

* Fork the project and clone it locally.
* To run the project in Docker follow the instructions [here](https://docs.docker.com/engine/installation/) to setup Docker.

### Local Flask Server

1. Go into the project directory
```
$ cd mdweb
```
2. Setup a virtual environment and activate
```
$ virtualenv env
$ source ./env/bin/activate
```
3. Install requirements
```
$ pip install -r requirements/development.txt
```
4. (Optional) Copy `sites/MySite.py` to `sites/<<NameOfYourSite>>.py`. Inside the copied file rename the class to match the file name - for example if you call the file `JoesSite.py` the class should be named `JoesSite`. If you choose not to copy to a new file continue to the next step using `sites/MySite.py`.
```
$ cp sites/MySite.py sites/JoesSite.py
$ nano sites/JoesSite.py
# Edit the class name and config as described above
```
5. (Optional) Create a new theme for your site in the `themes` directory. If you add a new theme remember to update the THEME config value in the next step.
8. Update the config attributes in the site class, specifically `THEME` and `CONTENT_PATH` (I suggest using the provided, empty, `content` directory). The `demo-content` directory is provided with example content to get you started. Add your content to the content directory defined.
6. Run the application. The dev_server script has one required parameter which is the site class name. If you copied the site file in step 6 the site name will be the name you used in that step (`JoesSite`) otherwise it will be the default site name `MySite`.
```
$ ./bin/dev_server JoesSite
```

Now visit [http://127.0.0.1:5000](http://127.0.0.1:5000) and you should see your site.

### Docker Container

It is possible to run MDWeb in Docker while developing.

Build the image from the Dockerfile in this project:
```
docker build -t mdweb .
```

Start a container based on the image just built but share your
development directory. Replace `<</host/directory>>` with the directory where you cloned the
MDWeb project.
```
docker run -d -p 80:5000 -v <</host/directory>>:/opt/mdweb --name mdweb-dev mdweb
```

This will run MDWeb using the default `MySite`. To run a Docker
container with a custom site it is possible to pass the site
configuration to MDWeb using environment variables. You must pass *all
five* environment variables or MDWeb will fall back to the default
site.

```
docker run -d -p 80:5000 \
           -v ./:/opt/mdweb \
           -e "SITE_NAME=JoesSite" \
           -e "DEBUG=True" \
           -e "SECRET_KEY="create_a_secret_key_for_use_in_production" \
           -e "CONTENT_PATH=demo-content/" \
           -e "THEME=bootstrap" \
           --name mdweb-dev mdweb
```

## Production
----

### Gunicorn Server

* Setup a site class as outlined above.
* Point your webserver to the wsgi.py file. For example, for Gunicorn a command similar to the following would run the site 
```
gunicorn -b 0.0.0.0:5000 -b [::1]:5000 --pythonpath /srv/mdweb wsgi:app
```

### Docker Container

To run the project in production mode in a Docker container.

First, follow the instructions
[here](https://docs.docker.com/engine/installation/) to setup Docker.

Build the image from the Dockerfile in this project:
```
docker build -t mdweb .
```

Start a container based on the image just built:
```
docker run -d -p 80:5000 --name mdweb-dev mdweb
```

This will run MDWeb using the default `MySite`. To run a Docker
container with a custom site it is possible to pass the site
configuration to MDWeb using environment variables. You must pass *all
five* environment variables or MDWeb will fall back to the default
site.

```
docker run -d -p 80:5000 \
           -e "SITE_NAME=JoesSite" \
           -e "DEBUG=True" \
           -e "SECRET_KEY=\x85\xa2\x1c\xfd\x07MF\xcb_ ]\x1e\x9e\xab\xa2qn\xd1\x82\xcb^\x11x\xc5" \
           -e "CONTENT_PATH=demo-content/" \
           -e "THEME=bootstrap" \
           --name mdweb-dev mdweb
```

Any further setup is outside the scope of this README. I'll try to add example cases as time allows.
