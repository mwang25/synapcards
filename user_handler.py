import webapp2

from card import Card
from constants import Constants
from global_stats import GlobalStats
from jinja_wrapper import JinjaWrapper
from user import User


class UserHandler(webapp2.RequestHandler):
    def get(self, user_id):
        values = User.get(user_id)
        if values is not None and values['user_id'] == user_id:
            GlobalStats.incr_views()
            values['timezones'] = Constants.SUPPORTED_TIMEZONES
            values['user_cards'] = Card.latest_by_user(user_id)
            values.update(Card.latest_featured(user_id))
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
