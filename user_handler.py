import webapp2

from card import Card
from constants import Constants
from global_stats import GlobalStats
from jinja_wrapper import JinjaWrapper
from update_frequency import UpdateFrequency
from user_manager import UserManager


class UserHandler(webapp2.RequestHandler):
    def get(self, user_id):
        values = UserManager().get(user_id)
        if values and values['user_id'] == user_id:
            GlobalStats.incr_views()
            values['timezones'] = Constants.SUPPORTED_TIMEZONES
            values['update_frequencies'] = UpdateFrequency.as_list()
            values['user_cards'] = Card.latest_by_user(user_id)
            values.update(Card.latest_featured(user_id))
            values['following'].sort()
            values['following_count'] = len(values['following'])
            values['followers'].sort()
            values['followers_count'] = len(values['followers'])
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
