import webapp2

from card import Card
from constants import Constants
from globalstats import GlobalStats
from jinjawrapper import JinjaWrapper


class CardHandler(webapp2.RequestHandler):
    def get(self, card_id):
        values = Card.by_id(card_id, truncate=False)
        if len(values['cards']) == 1:
            GlobalStats.incr_views()
            template = JinjaWrapper.get_template('card.html')
            self.response.write(template.render(values))
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<html><body>\n')
            self.response.write('Oops, could not find card {}'.format(card_id))
            self.response.write('<br>')
            self.response.write(
                '<a href="{}">[back to homepage]</a>'.format(
                    Constants.HOMEPAGE))
            self.response.write('\n</body></html>')
