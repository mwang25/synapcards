from operator import attrgetter
import webapp2

from card_stats import CardStats
from constants import Constants
from global_stats import GlobalStats
from jinja_wrapper import JinjaWrapper


class TagMapHandler(webapp2.RequestHandler):
    def get(self):
        GlobalStats.incr_views()
        args = self._parse_args()
        values = {'homepage': Constants.HOMEPAGE}
        tags = CardStats.get_all_tags_with_counts()
        if args['sort_by'] == 'count':
            # Luckily all tags are already sorted by name, since it is the
            # key, and sorting by count preserves the order of the names with
            # equal counts.
            tags.sort(key=attrgetter('count'), reverse=True)
        else:
            tags.sort(key=attrgetter('name'))

        values['all_tags'] = u'  '.join([unicode(t) for t in tags])
        template = JinjaWrapper.get_template('tag_map.html')
        self.response.write(template.render(values))

    def _parse_args(self):
        """Extract the args and return them in a dict"""
        args = {'sort_by': 'name'}

        if len(self.request.get('sort_by')) > 0:
            args['sort_by'] = self.request.get('sort_by')

        return args
