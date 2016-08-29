# Basic Usage

MDWeb is designed to be simple to use. Adding content to your site is as simple as droping a markdown file in the appropriate directory. The directory structure defines the naviagation and a special meta-information section at the top of the markdown files allows for customization of your pages.

After the initial setup (which is also incredibly easy) maintaining and updating your site should be easy-peasy.

## Content


Site content is simply Markdown formatted files. Each page on the site has it's
own file and the directory structure defines the navigation.

The content files currently support standard markdown with the addition of a
meta-information section at the beginning of each file which is parsed during
the content scan.

If you'd like to learn how to write Markdown I suggest reading [Daring Fireball](https://daringfireball.net/projects/markdown/basics).

## Example about/index.md


```
/*
Title: About MDWeb
Description: This description will go in the meta description tag
Nav Name: About MDWeb
Sitemap Priority: 0.9
Sitemap Changefreq: monthly
*/

MDWeb is painstakingly designed to be as minimalistic as possible while 
taking less than 5 minutes to setup and less than a minute to add 
content.

This project was borne out of my frustration with maintaining websites 
and adding content. I'm a firm believer in the ethos that CMS is an 
evil that should be rid from this world. I spent years fighting 
horrific battles with enemies such as Drupal, Wordpress and Joomla.
The things I saw during those dark days can not be unseen.

After years of battle, this weary web developmer built himself a tiny
oasis. This is MDWeb, I hope you find respite in it.
```

## Navigation Structure


Each directory under /content defines a section in the navigation structure.
If a file named index.md exists in the directory it is used as the landing page
for that section in the navigation. The index.md file in the root of the
content directory is the "home" page. Note that the navigation templates in some themes may only support one level of nesting, support for deeper navigation
levels could easily be added by updating (overriding) the navigation template.

### Example:
```
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

## Content Meta Fields

A meta-information section may be added to the beginning of each file. This section allows you to define customizations or override default behaviors for the page.

* *Author:* The page author. This is useful for blog posts and articles.

* *Date:* The page creation date. This is useful for blog posts and articles.

* *Description:* The page description. In the provided templates this will be
used in meta description tag.

* *Nav Name:* The name that will appear in the navigation.

* *Order:* The order the page will appear in navigation.

* *Sitemap Changefreq:* The change frequency value to use when generating the sitemap.

* *Sitemap Priority:* The priority value to use when generating the sitemap.

* *Template:* The template to use for page rendering. Defaults to page.html.

* *Title:* The page title. In the provided templates this will be used in the
`<title>` tag and in the page header.
