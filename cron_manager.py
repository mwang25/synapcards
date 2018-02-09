import datetime
# from google.appengine.api import app_identity
from google.appengine.api import mail

from card import Card
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

    def _split_and_format(self, cards, min_dt, max_dt):
        plain_new = []
        plain_updated = []
        html_new = []
        html_updated = []
        for c in cards:
            link = u'<a href={}/card/{}>{}</a>'.format(
                Constants.HOMEPAGE, c['card_id'], c['card_id'])
            body = u'({}/{}) {}'.format(
                c['rating'], Constants.MAX_RATING, c['title'])
            creation_dt = datetime.datetime.strptime(c['created'], '%m/%d/%Y')
            if creation_dt >= min_dt and creation_dt < max_dt:
                plain_new.append(u'{} {}\n'.format(c['card_id'], body))
                html_new.append(u'{} {}<br>'.format(link, body))
            else:
                plain_updated.append(u'{} {}\n'.format(c['card_id'], body))
                html_updated.append(u'{} {}<br>'.format(link, body))

        return plain_new, plain_updated, html_new, html_updated

    def _build_bodies(self):
        args = {'user_id': 'mwang25', 'count': 100}

        now = datetime.datetime.utcnow()
        today = datetime.datetime(now.year, now.month, now.day)
        args['min_update_datetime'] = today - datetime.timedelta(days=1)
        args['max_update_datetime'] = today
        cards = Card.search(args)

        (plain_new, plain_upd, html_new, html_upd) = self._split_and_format(
            cards, args['min_update_datetime'], args['max_update_datetime'])
        num_new = len(plain_new)
        num_upd = len(plain_upd)

        first_line = u'The users you followed have updates\n'
        unsubscribe = u'To unsubscribe, simply reply to this email.'
        plain = first_line
        plain += u'\n'
        if num_new:
            plain += u'New cards ({}):\n'.format(num_new)
            for c in plain_new:
                plain += c
        if num_upd:
            plain += u'Updated cards ({}):\n'.format(num_upd)
            for c in plain_upd:
                plain += c
        plain += u'\n'
        plain += unsubscribe
        plain += u'\n'

        html = u'<html><head></head><body>'
        html += first_line
        html += u'<br>'
        if num_new:
            html += u'<b>New cards ({}):</b><br>'.format(num_new)
            for c in html_new:
                html += c
        if num_upd:
            html += u'<b>Updated cards ({}):</b><br>'.format(num_upd)
            for c in html_upd:
                html += c
        html += unsubscribe
        html += u'<br>'
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
