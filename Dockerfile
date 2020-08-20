FROM python:alpine
MAINTAINER Chad Rempp <crempp@gmail.com>
LABEL description="MDWeb production demo site"

COPY . /opt/mdweb

WORKDIR /opt/mdweb

RUN apk add --no-cache --update --virtual .build-deps \
        g++ \
        gcc \
    && pip install -r /opt/mdweb/requirements/production.txt \
    && apk del .build-deps \
    && rm -rf /var/cache/apk/*

EXPOSE 5000

CMD ["gunicorn", "--workers=4", "-b 0.0.0.0:5000","wsgi:app"]
