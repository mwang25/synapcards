import webapp2

from constants import Constants
from jinja_wrapper import JinjaWrapper


class SigninHandler(webapp2.RequestHandler):
    def get(self):
        values = {
            'timezone': 'not set',
            'homepage': Constants.HOMEPAGE,
        }
        template = JinjaWrapper.get_template('signin.html')
        self.response.write(template.render(values))
