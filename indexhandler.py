import webapp2

from card import Card
from constants import Constants
from globalstats import GlobalStats
from jinjawrapper import JinjaWrapper


class IndexHandler(webapp2.RequestHandler):
    def get(self, path):
        if path == '' or path == '/' or path.startswith('index.htm'):
            GlobalStats.incr_views()
            values = Card.latest_top_rated()
            values['total_cards'] = GlobalStats.total_cards()
            values['total_users'] = GlobalStats.total_users()
            values['total_views'] = GlobalStats.total_views()
            values['homepage'] = Constants.HOMEPAGE
            template = JinjaWrapper.get_template('index.html')
            self.response.write(template.render(values))
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<html><body>\n')
            self.response.write('Oops, could not find page {}'.format(path))
            self.response.write('<br>')
            self.response.write(
                '<a href="{}">[back to homepage]</a>'.format(
                    Constants.HOMEPAGE))
            self.response.write('\n</body></html>')
