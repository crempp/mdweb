import datetime
import logging
import numbers
import os
import pytz
import time

from flask import (
    current_app as app,
    make_response,
    render_template_string,
    url_for,
)
from flask.views import View

#: Template string to use for the sitemap generation
# (is there a better place to put this?, not in the theme)
SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    {% for page in pages -%}
    <url>
        <loc>{{page.loc|safe}}</loc>
        <lastmod>{{page.lastmod|safe}}</lastmod>
        {%- if page.changefreq %}
        <changefreq>{{page.changefreq|safe}}</changefreq>
        {%- endif %}
        {%- if page.priority %}
        <priority>{{page.priority|safe}}</priority>
        {%- endif %}
    </url>
    {%- endfor %}
</urlset>
"""


class SiteMapView(View):
    sitemap_cache = None

    def dispatch_request(self):
        if self.sitemap_cache is None:
            self.sitemap_cache = self.generate_sitemap()

        response = make_response(self.sitemap_cache)
        response.headers["Content-Type"] = "application/xml"
        return response

    @classmethod
    def generate_sitemap(cls):
        """Generate sitemap.xml. Makes a list of urls and date modified."""
        logging.info("Generating sitemap...")
        start = time.time()

        pages = []

        index_url = url_for('index',_external=True)

        for url, page in app.navigation.get_page_dict().items():
            mtime = os.path.getmtime(page.page_path)
            if isinstance(mtime, numbers.Real):
                mtime = datetime.datetime.fromtimestamp(mtime)
            mtime.replace(tzinfo=pytz.UTC)
            lastmod = mtime.strftime('%Y-%m-%dT%H:%M:%S%z')
            pages.append({
                'loc': "%s%s" % (index_url, url),
                'lastmod': lastmod,
                'changefreq': page.meta_inf.sitemap_changefreq,
                'priority': page.meta_inf.sitemap_priority,
            })

        sitemap_xml = render_template_string(SITEMAP_TEMPLATE, pages=pages)

        end = time.time()
        logging.info("completed sitemap generation in %s seconds" %
                     (end - start))

        return sitemap_xml
