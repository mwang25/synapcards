# from google.appengine.api import app_identity
from google.appengine.api import mail

from constants import Constants


class CronManagerError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class CronManager():
    def run(self):
        # Success = 200, error = 500
        try:
            self._send_email()
        except:
            return 500
        return 200

    def _build_bodies(self):
        first_line = u'The users you followed have updates\n'
        unsubscribe = u'To unsubscribe, simply reply to this email.'
        update = u'mwang25:125 (5/5) subject line \u725b'
        plain = first_line
        plain += u'mwang25:\n'
        plain += update
        plain += u'\n'
        plain += unsubscribe
        plain += u'\n'

        html = u'<html><head></head><body>'
        html += first_line
        html += u'<br>'
        html += u'mwang25:<br>'
        html += u'<a href={}/card/mwang25:125>{}</a>'.format(
            Constants.HOMEPAGE, update)
        html += u'<br>'
        html += unsubscribe
        html += u'</body></html>'
        return plain, html

    def _send_email(self):
        # Original code creates a sender of
        # fireproto-5c009@appspot.gserviceaccount.com
        # But GCP console will not accept that as a sender.
        # sender = '{}@appspot.gserviceaccount.com'.format(
        #    app_identity.get_application_id())
        sender = 'synapcards@gmail.com'
        message = mail.EmailMessage(
            sender=sender,
            subject="Your daily update from synapcards.com")

        message.to = "mwang25@gmail.com"
        message.reply_to = 'unsubscribe@{}.appspotmail.com'.format(
            Constants.PROJECT_ID)
        (plain, html) = self._build_bodies()
        message.body = plain
        message.html = html
        message.send()
