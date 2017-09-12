import webapp2

from card import Card
from constants import Constants
from jinjawrapper import JinjaWrapper


class FeaturedCardsHandler(webapp2.RequestHandler):
    def get(self, card_id):
        values = Card.by_featured_cards_id(card_id)
        if values['featured_cards_id'] == card_id:
            template = JinjaWrapper.get_template('featuredcards.html')
            self.response.write(template.render(values))
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<html><body>\n')
            self.response.write(
                'Oops, could not find featured card {}'.format(card_id))
            self.response.write('<br>')
            self.response.write(
                '<a href="{}">[back to homepage]</a>'.format(
                    Constants.HOMEPAGE))
            self.response.write('\n</body></html>')
