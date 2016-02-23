/*
Title: Writing Pages
Description: How to write content for MDWeb
Order: 4
*/

#Writing MDWeb Content

##Content

Site content is simply markdown formatted files. Each page on the site has it's
own file and the directory structure defines the navigation.

The content files currently support standard markdown with the addition of a
meta-information section at the beginning of each file which is parsed during
the content scan.

##Navigation Structure

Each directory under /content defines a section in the navigation structure.
If a file named index.md exists in the directory it is used as the landing page
for that section in the navigation. The index.md file in the root of the
content directory is the "home" page. Note that the navigation template
currently only supports one level of nesting, support for deeper navigation
levels could easily be added by updating (overriding) the navigation template.


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


##Content Meta Fields
* *Title:* The page title. In the provided templates this will be used in the
`<title>` tag and in the page header.

* *Nav Name:* The name that will appear in the navigation

* *Description:* The page description. In the provided templates this will be
used in meta description tag.

* *Author:* The page author. This is useful for blog posts and articles.

* *Date:* The page creation date. This is useful for blog posts and articles.

* *Order:* The order the page will appear in navigation.

* *Template:* The template to use for page rendering. Defaults to page.html
