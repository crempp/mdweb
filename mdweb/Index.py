"""MDWeb Index View."""
from flask.views import View
from flask import render_template, abort, current_app as app


class Index(View):
    """The one view to rule them all.

    MDWeb has one single entry point. The MDWeb routing system (not Flasks)
    determines the how to handle the request and what markdown file to load.
    """

    methods = ['GET']

    @classmethod
    def render(cls, page):
        """Render the given page using the configured theme."""
        if page.meta_inf.template:
            page_template = page.meta_inf.template
        else:
            page_template = 'page.html'

        context = {
            'page': page.page_html,
            'meta': page.meta_inf,
        }

        return render_template(page_template, **context)

    def dispatch_request(self, path=None, page=None):  # pylint: disable=W0221
        """Dispatch request."""
        if page is None:
            page = app.get_page(path)

            if page is None:
                abort(404)

        return self.render(page)
