import webapp2

from card import Card
from card_manager import CardManager
from constants import Constants
from global_stats import GlobalStats
from jinja_wrapper import JinjaWrapper


class CardHandler(webapp2.RequestHandler):
    def get(self, card_id):
        (user_id, card_num) = Card.split_card_id(card_id)
        if card_num == 0 or Card.exists(card_id):
            values = {'ratings': range(1, Constants.MAX_RATING + 1)}
            if card_num == 0:
                values['card'] = {}
            else:
                GlobalStats.incr_views()
                values['card'] = CardManager.get({
                    'user_id': user_id,
                    'card_num': card_num,
                    })

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
