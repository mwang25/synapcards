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

        if len(self.request.get('user_id')) > 0:
            args['user_id'] = self.request.get('user_id')

        if len(self.request.get('author')) > 0:
            args['source_author'] = self.request.get('author')

        if len(self.request.get('source')) > 0:
            args['source'] = self.request.get('source')

        if len(self.request.get('tags')) > 0:
            tags = self.request.get('tags').split(',')
            args['tags'] = [t.strip() for t in tags]

        # args['rating'] = '4 or higher'
        if len(self.request.get('rating')) > 0:
            args['rating'] = self.request.get('rating')

        if len(self.request.get('count')) > 0:
            args['count'] = int(self.request.get('count'))

        return args
