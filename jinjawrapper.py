import os
import jinja2

mydir = os.path.dirname(__file__)
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(mydir, 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class JinjaWrapper():

    @staticmethod
    def get_template(filename):
        return JINJA_ENVIRONMENT.get_template(filename)
