import webapp2

from card_stats import CardStats
from constants import Constants
from global_stats import GlobalStats
from jinja_wrapper import JinjaWrapper
from search_manager import SearchManager
from user import User


class SearchHandler(webapp2.RequestHandler):
    def get(self):
        GlobalStats.incr_views()
        args = self._parse_args()
        if args.get('text_dump', 'false') == 'true':
            values = SearchManager.search_for_dump(args)
            values['count'] = len(values['cards'])
            template = JinjaWrapper.get_template('text_dump.html')
        else:
            values = SearchManager.search(args)
            values['users'] = [''] + sorted(User.get_all())
            values['authors'] = [''] + sorted(CardStats.get_all_authors())
            values['sources'] = [''] + sorted(CardStats.get_all_sources())
            values['ratings'] = Constants.SEARCH_RATINGS
            values['counts'] = Constants.SEARCH_COUNTS
            values['homepage'] = Constants.HOMEPAGE
            template = JinjaWrapper.get_template('search.html')
        self.response.write(template.render(values))

    def _parse_args(self):
        """Extract the args and return them in a dict"""
        args = {}
        if '?' not in self.request.path_qs:
            args['new_search'] = True
            return args

        if len(self.request.get('tags')) > 0:
            tags = self.request.get('tags').split(',')
            args['tags'] = [t.strip() for t in tags]

        # All string params are handled the same way
        params = [
            'user_id',
            'author',
            'source',
            'rating',
            'count',
            'text_dump',
            'spec_op',
        ]
        for p in params:
            if len(self.request.get(p)) > 0:
                args[p] = self.request.get(p)

        return args
