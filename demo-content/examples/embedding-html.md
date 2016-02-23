/*
Title: Embedding HTML
Description: How to embed HTML
Author: Chad Rempp
Date: 2014/12/28
Order: 2
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
