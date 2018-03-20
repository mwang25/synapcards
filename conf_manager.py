import logging

from google.appengine.ext import ndb

from conf_datetime import ConfDatetime
from email_status import EmailStatus
from user import User


class ConfManager():
    @ndb.transactional()
    def process_email(self, email):
        user_info = User.get(email=email)
        if not user_info:
            logging.error('could not find user for ' + email)
            return

        user_id = user_info['user_id']
        logging.info('{} is in {} conf_sent {}'.format(
            user_id,
            user_info['email_status'],
            user_info['confirmation_sent']))

        # check for correct state and time range
        if user_info['email_status'] != EmailStatus.WAIT_FOR_CONF.name:
            logging.error('ignoring conf email: wrong state '
                          + user_info['email_status'])
            return

        if ConfDatetime.from_string(user_info['confirmation_sent']).expired():
            logging.error('ignoring conf email: expired, conf_sent '
                          + user_info['confirmation_sent'])
            User.update(
                user_id, email_status=EmailStatus.CONF_TIMED_OUT.name)
            return

        logging.info('Setting {} to CONFIRMED_GOOD'.format(user_id))
        User.update(user_id, email_status=EmailStatus.CONFIRMED_GOOD.name)
