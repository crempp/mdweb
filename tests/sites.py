"""MDWeb Sites for testing"""
from dateutil import parser
from mdweb.MDSite import MDSite

index_md_file_string = u"""/*
Title: MDWeb
Description: The minimalistic markdown NaCMS
Date: February 1st, 2016
Sitemap Priority: 0.9
Sitemap ChangeFreq: daily
*/
"""

layout_file_string = u"""
<!DOCTYPE HTML>
<html>
  <body>
  <header
  {% include 'navigation.html' %}
  </header>

  {% block body %}{% endblock %}

  </body>
</html>
"""

navigation_file_string = """
<div class="navbar-header">
  <button type="button" class="navbar-toggle collapsed" data-toggle="collapse"
          data-target=".navbar-collapse" aria-expanded="false" aria-controls="navbar">
    <span class="sr-only">Toggle navigation</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
  </button>
  <a class="navbar-brand" href="/">
    <span class="small-home"><img src="/static/images/logo_30X50_trans.png" ></span>
    <span class="large-home">{{ navigation.page.meta_inf.nav_name }}</span>
  </a>
</div>
<div class="collapse navbar-collapse">
  <ul class="nav navbar-nav nav-links">
    <li class="ll_nav_menu_home">
      <a tabindex="0" href="/" data-dest="home">
        <div class="nav-link-text">
          <span class="large-home">home</span>
        </div>
      </a>
    </li>
    {% for nav in navigation.children -%}
    <li class="ll_nav_menu_{{ nav.name|lower }}">
      <a tabindex="0" {%if nav.has_page %}href="/{{ nav.page.url_path }}"{% endif %} data-dest="{{ nav.name|lower }}">
        <div class="nav-link-text">{{ nav.name }}</div>
      </a>
    </li>
  {% endfor -%}
  </ul>
</div>
"""

page_file_string = u"""
{% extends "layout.html" %}

{% block title %}
{% if meta.title -%}
- {{ meta.title }}
{% endif %}
{% endblock %}

{% block body %}
<article id="page-{{ meta.nav_name|lower|replace(' ','-') }}" class="page">
  <div class="panel panel-default">
    <div class="panel-heading">
      <span class="panel-title">
        {{ meta.title }}
      </span>
      <span class="pull-right byline">
        {% if meta.author %}
        by {{ meta.author }}
        {% endif %}
        {% if meta.date %}
        on {{ meta.date }}
        {% endif %}
      </span>
      <div class="clearfix visible-xs-block"></div>
    </div>
    <div class="panel-body">
      {{ page | safe}}
    </div>
  </div>
</article>
{% endblock %}
"""

pagehome_file_string = """
{% extends "layout.html" %}
{% block body %}
  <article id="page-home">
    {# Home Section #}
    <div class="jumbotron" data-section-id="home">
      <div class="container">
        <div class="row">
          <div class="col-md-4 home-teaser-container">
            <img src="{{ navigation.page.meta_inf.teaser_image }}">
          </div>
          <div class="col-md-8">
            {#<h1>{{ navigation.page.meta_inf.title }}</h1>#}
            {{ page | safe}}
          </div>
        </div>
      </div>
    </div>

    {# Section for each nav entry #}
    {% for nav in navigation.children if nav.children|length > 0 -%}
    <div class="panel panel-default" data-section-id="{{ nav.name|lower }}">
      <div class="panel-heading">
        <span class="panel-title">
          {{ nav.name }}
        </span>
        <span class="pull-right read-more">
          <a href="{{ nav.page.url_path }}">
            more {{ nav.name | lower }}
            <span class="glyphicon glyphicon-arrow-right" aria-hidden="true"></span>
          </a>
        </span>
      </div>
      <div class="panel-body">
        <div class="row">


          {% for page in nav.child_pages|sorted_pages('date',6) %}
          <div class="col-sm-6 col-md-4">
            <div class="thumbnail">
              {% if page.meta_inf.teaser_image %}
              <a href="/{{ page.url_path }}">
                <img src="{{ page.meta_inf.teaser_image }}">
              </a>
              {% endif %}
              <div class="caption">
                <h3 class="thumbnail-title">
                  <a href="/{{ page.url_path }}">{{ page.meta_inf.title }}</a>
                </h3>
                <p>
                  <div class="text-muted byline">
                    {% if page.meta_inf.author %}
                    by {{ page.meta_inf.author }}
                    {% endif %}
                    {% if page.meta_inf.date %}
                    on {{ page.meta_inf.date }}
                    {% endif %}
                  </div>
                  <div class="thumbnail-teaser">
                    {{ page.meta_inf.teaser }}
                  </div>
                </p>
                <a href="/{{ page.url_path }}">Read more...</a>
              </div>
            </div>
          </div>
          {% endfor %}

        </div>
      </div>
    </div>
    {% endfor %}

  </article>
{% endblock %}
"""

debughelper_file_string = """
<div id="md_debug_helper">
{#  <nav class="navbar navbar-default">#}
  <nav class="md_navbar">
{#    <div class="container-fluid">#}
    <div class="md_container">
      <!-- Collect the nav links, forms, and other content for toggling -->
      <div class="">
        <ul class="md_navbar_nav">
          {% for section in debug|sort %}
          <li class="md_debug_menu_section">
            <a id="md_debug_section_link_{{ section }}"
               data-section="{{ section }}"
               href="#">{{ section }}</a>
          </li>
          {% endfor %}
        </ul>
      </div><!-- /.navbar-collapse -->
    </div><!-- /.container-fluid -->
  </nav>
  <div id="md_debug_display">
    {% for section in debug|sort %}
    <div id="md_debug_display_{{ section }}" class="md_debug_display_section">
      <pre>
{{ debug[section] }}
      </pre>
    </div>
    {% endfor %}
  </div>
</div>
"""


class MDTestSite(MDSite):
    
    """Test site for use with real FS"""

    class MDConfig:  # pylint: disable=R0903

        """Config class for testing."""

        DEBUG = False
        SECRET_KEY = 'create_a_secret_key_for_use_in_production'
        CONTENT_PATH = 'demo-content/'
        THEME = 'bootstrap'
        TESTING = True
        GA_TRACKING_ID = 'UA-00000000-1'
        DEBUG_HELPER = False
        
        
class MDTestSiteDebugHelper(MDSite):

    """Test site for use with fake FS and debug helper enabled."""

    class MDConfig:  # pylint: disable=R0903

        """Config class for testing."""

        DEBUG = False
        SECRET_KEY = 'create_a_secret_key_for_use_in_production'
        CONTENT_PATH = 'demo-content/'
        THEME = 'bootstrap'
        TESTING = True
        GA_TRACKING_ID = 'UA-00000000-1'
        DEBUG_HELPER = True


class MDFakeFSTestSite(MDSite):
    
    """Test site for use with fake FS."""

    class MDConfig:  # pylint: disable=R0903

        """Config class for testing."""

        DEBUG = False
        SECRET_KEY = 'create_a_secret_key_for_use_in_production'
        CONTENT_PATH = '/my/content/'
        THEME = '/my/theme/'
        TESTING = True
        GA_TRACKING_ID = False
        DEBUG_HELPER = False
        
        
class MDFakeFSNoThemeTestSite(MDSite):
    
    """Test site for use with fake FS and missing theme directory."""

    class MDConfig:  # pylint: disable=R0903

        """Config class for testing."""

        DEBUG = False
        SECRET_KEY = 'create_a_secret_key_for_use_in_production'
        CONTENT_PATH = '/my/content/'
        THEME = '/my/missing/theme/'
        TESTING = True
        GA_TRACKING_ID = False
        DEBUG_HELPER = False


class MDFakeFSNoContentTestSite(MDSite):
    
    """Test site for use with fake FS and missing theme directory."""
    
    class MDConfig:  # pylint: disable=R0903
        
        """Config class for testing."""
        
        DEBUG = False
        SECRET_KEY = 'create_a_secret_key_for_use_in_production'
        CONTENT_PATH = '/my/missing/content/'
        THEME = '/my/theme/'
        TESTING = True
        GA_TRACKING_ID = False
        DEBUG_HELPER = False


def populate_fakefs(self):
    """Fake file system setup"""
    
    self.fs.CreateFile('/my/content/400.md')
    self.fs.CreateFile('/my/content/403.md')
    self.fs.CreateFile('/my/content/404.md')
    self.fs.CreateFile('/my/content/500.md')
    self.fs.CreateFile('/my/content/robots.txt')
    self.fs.CreateFile('/my/content/humans.txt')
    self.fs.CreateFile('/my/content/favicon.ico')
    self.fs.CreateFile('/my/content/crossdomain.xml')
    self.fs.CreateFile('/my/content/index.md',
                       contents=index_md_file_string).SetMTime(
        parser.parse('Thu, 28 Jun 2015 14:17:15 +0000')
    )
    self.fs.CreateFile('/my/content/about/index.md').SetMTime(
        parser.parse('Wed, 27 Jun 2015 13:12:15 +0000')
    )
    self.fs.CreateFile('/my/content/contact/index.md').SetMTime(
        parser.parse('Tue, 26 Jun 2015 12:06:15 +0000')
    )
    self.fs.CreateFile('/my/content/assets/logo.png')
    
    self.fs.CreateFile('/my/theme/assets/css/style.css')
    self.fs.CreateFile('/my/theme/assets/js/site.js')
    self.fs.CreateFile('/my/theme/templates/layout.html',
                       contents=layout_file_string).SetMTime(
        parser.parse('Thu, 28 Jun 2015 14:17:15 +0000')
    )
    self.fs.CreateFile('/my/theme/templates/navigation.html',
                       contents=navigation_file_string).SetMTime(
        parser.parse('Thu, 28 Jun 2015 14:17:15 +0000')
    )
    self.fs.CreateFile('/my/theme/templates/page.html',
                       contents=page_file_string).SetMTime(
        parser.parse('Thu, 28 Jun 2015 14:17:15 +0000')
    )
    self.fs.CreateFile('/my/theme/templates/page_home.html',
                       contents=pagehome_file_string).SetMTime(
        parser.parse('Thu, 28 Jun 2015 14:17:15 +0000')
    )
