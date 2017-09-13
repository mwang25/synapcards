import webapp2

from card import Card
from constants import Constants
from globalstats import GlobalStats
from jinjawrapper import JinjaWrapper
from user import User


class UserHandler(webapp2.RequestHandler):
    def get(self, user_id):
        values = User.by_id(user_id)
        if values['user_id'] == user_id:
            GlobalStats.incr_views()
            card_values = Card.latest_featured(user_id)
            values.update(card_values)
            template = JinjaWrapper.get_template('user.html')
            self.response.write(template.render(values))
        else:
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write('<html><body>\n')
            self.response.write('Oops, could not find user {}'.format(user_id))
            self.response.write('<br>')
            self.response.write(
                '<a href="{}">[back to homepage]</a>\n'.format(
                    Constants.HOMEPAGE))
            self.response.write('</body></html>')
