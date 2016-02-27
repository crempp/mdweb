from flask.views import View
from flask import render_template, abort, current_app as app


class Index(View):
    """The one view to rule them all. MDWeb has one single entry point. The
    MDWeb routing system (not Flasks) determines the how to handle the request
    and what markdown file to load.
    """

    methods = ['GET']

    def dispatch_request(self, path): # pylint: disable=W0221
        """Dispatch request"""

        page = app.get_page(path)

        if page is None:
            abort(404)

        if page.meta_inf.template:
            page_template = page.meta_inf.template
        else:
            page_template = 'page.html'

        context = {
            'page': page.page_html,
            'meta': page.meta_inf,
        }

        return render_template(page_template, **context)
