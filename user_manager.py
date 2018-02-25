import logging

from google.appengine.ext import ndb

from card import Card
from card_stats import CardStats
from constants import Constants
from global_stats import GlobalStats
from update_frequency import UpdateFrequency
from user import User
from user_id import BadUserIdError
from user_id import UserId


class UserManagerError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class UserManager():
    @ndb.transactional(xg=True)
    def get_with_add_option(self, firebase_id, email):
        """Get info about user using firebase_id, if not found, add user"""
        # Must do the get and add within the same atomic transaction
        user_info = User.get(firebase_id=firebase_id)
        if user_info:
            return user_info['user_id']

        # Add this as new user as long as MAX_USERS is not exceeded.
        if GlobalStats.total_users() >= Constants.MAX_USERS:
            raise UserManagerError('cannot add any more users')

        user_id = UserId.generate_id(email)
        User.add(user_id, firebase_id, email)
        GlobalStats.incr_users()
        return user_id

    @ndb.transactional()
    def _decr_card_count(self, count):
        GlobalStats.decr_cards(count)

    def _delete_all_user_cards(self, user_id):
        count = 0
        more_cards = True
        while more_cards:
            cards = Card.latest_by_user(user_id, 50)
            more_cards = len(cards) > 0
            for c in cards:
                count += 1
                # This logic belongs in CardManager, but I don't want
                # user_manager to depend on card_manager, and also I want to
                # update global card count only once.
                CardStats.decr_authors(c['authors'])
                CardStats.decr_source(c['source'])
                CardStats.decr_tags(c['tags'])
                Card.delete(c['card_id'])

            self._decr_card_count(count)
            count = 0

    @ndb.transactional(xg=True)
    def _delete_user_and_update_counts(self, user_id):
        User.delete(user_id)
        GlobalStats.decr_users()
        GlobalStats.incr_deleted_users()

    def delete(self, user_id):
        self._delete_all_user_cards(user_id)
        self._delete_user_and_update_counts(user_id)
        return {}

    @ndb.transactional()
    def update(self, user_id, values):
        if not UpdateFrequency.valid(values['update_frequency']):
            raise UserManagerError('invalid or unsupported update frequency')
        if values['timezone'] not in Constants.SUPPORTED_TIMEZONES:
            raise UserManagerError('invalid or unsupported timezone')

        settings = User.get(user_id)
        if settings['user_id'] != values['user_id']:
            if settings['total_cards'] > 0:
                raise UserManagerError(
                    'cannot change user id after adding cards')

            try:
                UserId.validate(values['user_id'])
            except BadUserIdError as err:
                return {'error_message': err.message}
            except Exception as e:
                msg = str(type(e)) + ':' + ''.join(e.args)
                return {'error_message': msg}

        return User.update(
            user_id,
            values['user_id'],
            values['email'],
            values['profile'],
            values['timezone'],
            values['update_frequency'],
            )

    @ndb.transactional()
    def update_email_freq_status(self, email, freq=None, status=None):
        user = User.get(email=email)
        if not user:
            logging.info("could not find user for " + email)
            return

        logging.info("user_id=" + user['user_id'])
        if freq:
            logging.info("(unsubscribe) freq=" + freq)
        if status:
            logging.info("(bounce) status=" + status)

        User.update(
            user['user_id'],
            user['user_id'],
            user['email'],
            user['profile'],
            user['timezone'],
            freq,
            status,
            )
