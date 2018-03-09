import datetime
import logging

from google.appengine.ext import ndb

from constants import Constants
from email_status import EmailStatus
from publish_datetime import PublishDatetime
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
            logging.error('ignoring conf email due to wrong state')
            return

        conf_sent = datetime.datetime.strptime(
            user_info['confirmation_sent'], PublishDatetime.FULL_DATE_TIME)
        timeout = datetime.timedelta(minutes=Constants.CONF_EMAIL_TIMEOUT)
        if datetime.datetime.utcnow() > conf_sent + timeout:
            logging.error('ignoring conf email expired, sent {} '.format(
                user_info['confirmation_sent']))
            return

        logging.info('Setting {} to confirmed'.format(user_id))
        User.update(user_id, email_status=EmailStatus.CONFIRMED_GOOD.name)
