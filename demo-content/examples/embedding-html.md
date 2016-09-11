/*
Title: Embedding HTML Example
Nav Name: Embedding HTML
Description: An example of embedding HTML into a page
Order: 4
Teaser: A helpful example for embedding raw HTML into a content file
    for advanced content rendering.
Sitemap Priority: 0.5
Sitemap Changefreq: monthly
*/

# Embedding HTML

The Markdown parser used supports embeddable HTML. For example, the following
block:

    <table style="width:100%;border:1px solid black;">
      <tr>
        <td>Jill</td>
        <td>Smith</td> 
        <td>50</td>
      </tr>
      <tr>
        <td>Eve</td>
        <td>Jackson</td> 
        <td>94</td>
      </tr>
    </table>

will be rendered as:

<table style="width:100%;border:1px solid black;">
  <tr>
    <td>Jill</td>
    <td>Smith</td> 
    <td>50</td>
  </tr>
  <tr>
    <td>Eve</td>
    <td>Jackson</td> 
    <td>94</td>
  </tr>
</table>
