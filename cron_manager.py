import datetime
# from google.appengine.api import app_identity
from google.appengine.api import mail

from card import Card
from constants import Constants
from update_frequency import UpdateFrequency
from user import User


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

    def _get_followed_users(self, user_ids):
        """Return list of users follwed by the given user_ids"""
        followed = []
        for user_id in user_ids:
            user = User.get(user_id)
            followed += User.split_strip(user['following'])

        # There might be duplicate user_ids in the list, so remove duplicates.
        return list(set(followed))

    def _fill_users(self, user_ids, min_update_dt, max_update_dt):
        """Return dict of user_id : list of updated cards"""
        d = {}
        args = {
            'count': 100,
            'min_update_datetime': min_update_dt,
            'max_update_datetime': max_update_dt}
        for user_id in user_ids:
            args['user_id'] = user_id
            d[user_id] = Card.search(args)
        return d

    def _build_bodies(
            self, following, card_dict, min_update_dt, max_update_dt):
        unsubscribe = u'To unsubscribe, simply reply to this email.'

        # User enabled updates but is not following anyone
        if len(following) == 0:
            follow_instructions = u"""Currently, you are not following any users.
                After you start following some Synapcards users, this email
                will contain a list of newly added or updated cards by the
                users you follow."""
            plain = follow_instructions
            plain += u'\n\n'
            plain += unsubscribe

            html = u'<html><head></head><body>'
            html += follow_instructions
            html += u'<br><br>'
            html += unsubscribe
            html += u'</body></html>'
            return plain, html

        cards = []
        # convert multiple users separated by comma into a list
        for u in User.split_strip(following):
            cards += card_dict[u]
        (plain_new, plain_upd, html_new, html_upd) = self._split_and_format(
            cards, min_update_dt, max_update_dt)
        num_new = len(plain_new)
        num_upd = len(plain_upd)

        first_line = u'You are following: {}'.format(following)
        second_line = u'There are {} new and updated cards.'.format(
            len(cards))

        plain = first_line
        plain += u'\n'
        plain = second_line
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

        html = u'<html><head></head><body>'
        html += first_line
        html += u'<br>'
        html += second_line
        html += u'<br>'
        if num_new:
            html += u'<b>New cards ({}):</b><br>'.format(num_new)
            for c in html_new:
                html += c
        if num_upd:
            html += u'<b>Updated cards ({}):</b><br>'.format(num_upd)
            for c in html_upd:
                html += c
        html += u'<br>'
        html += unsubscribe
        html += u'</body></html>'

        return plain, html

    def _send_email(self):
        now = datetime.datetime.utcnow()
        today = datetime.datetime(now.year, now.month, now.day)
        max_update_dt = today

        freq_list = [UpdateFrequency.DAILY.value]
        # On Sunday (6), also send out weekly updates
        if now.weekday() == 6:
            freq_list += [UpdateFrequency.WEEKLY.value]

        for freq in freq_list:
            email_dict = User.get_update_emails(freq)
            # followed_users is list of all users being followed at this freq
            followed_users = self._get_followed_users(email_dict.keys())
            days = 1 if freq == UpdateFrequency.DAILY.value else 7
            min_update_dt = today - datetime.timedelta(days=days)
            card_dict = self._fill_users(
                followed_users, min_update_dt, max_update_dt)

            message = mail.EmailMessage(
                sender='synapcards@gmail.com',
                subject='Your {} update from synapcards.com'.format(freq),
                reply_to='unsubscribe@{}.appspotmail.com'.format(
                    Constants.PROJECT_ID))
            for user_id in email_dict.keys():
                user = User.get(user_id)
                message.to = user['email']
                (message.body, message.html) = self._build_bodies(
                    user['following'], card_dict, min_update_dt, max_update_dt)
                message.send()
