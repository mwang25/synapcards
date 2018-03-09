import datetime
import logging

from google.appengine.api import mail
from google.appengine.ext import ndb

from card import Card
from card_stats import CardStats
from constants import Constants
from email_status import EmailStatus
from global_stats import GlobalStats
from update_frequency import UpdateFrequency
from user import User
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
                # batch updates to the global card count.
                CardStats.decr_authors(c['authors'])
                CardStats.decr_source(c['source'])
                CardStats.decr_tags(c['tags'])
                Card.delete(c['card_id'])

            self._decr_card_count(count)
            count = 0

    @ndb.transactional()
    def _cleanup_follows(self, user_id):
        """Remove this user from other users followers and following list"""
        user = User.get(user_id)

        # For all users this user is following, remove this user from their
        # followers field.
        for u in user['following']:
            if not u == user_id:
                t_user = User.get(u)
                User.update(
                    u,
                    followers=list(set(t_user['followers']) - set([user_id]))
                    )

        # For all users who are following this user, remove this user from
        # their following field.
        for u in user['followers']:
            if not u == user_id:
                t_user = User.get(u)
                User.update(
                    u,
                    following=list(set(t_user['following']) - set([user_id]))
                    )

    @ndb.transactional(xg=True)
    def _delete_user_and_update_counts(self, user_id):
        User.delete(user_id)
        GlobalStats.decr_users()
        GlobalStats.incr_deleted_users()

    def delete(self, user_id):
        """Delete user.  Note this is not the same as changing user id."""
        self._delete_all_user_cards(user_id)
        self._cleanup_follows(user_id)
        self._delete_user_and_update_counts(user_id)
        return {}

    def _user_id_change_allowed(self, user_info):
        if user_info['total_cards'] > 0:
            raise UserManagerError('cannot change user id after adding cards')
        if len(user_info['following']) > 0:
            raise UserManagerError(
                'cannot change user id after following users')
        if len(user_info['followers']) > 0:
            raise UserManagerError(
                'cannot change user id after being followed')

    def _user_id_unique(self, user_id):
        if User.exists(user_id):
            raise UserManagerError('that user id is already taken')

    def _validate_update(self, values):
        if not UpdateFrequency.valid(values['update_frequency']):
            raise UserManagerError('invalid or unsupported update frequency')
        if values['timezone'] not in Constants.SUPPORTED_TIMEZONES:
            raise UserManagerError('invalid or unsupported timezone')

    @ndb.transactional()
    def _change_user_id_main(self, user_id, values):
        """Most of change user_id can be done inside transaction."""
        # All these checks will raise exception if they fail.
        user_info = User.get(user_id)
        self._user_id_change_allowed(user_info)
        new_user_id = values['user_id']
        self._user_id_unique(new_user_id)
        UserId.validate(new_user_id)
        self._validate_update(values)

        # Add a new user with new user_id using a mix of existing settings
        # and any possible new settings passed in.
        # The new user is created with the existing email and update_freq
        # so that any changes can be detected by the calling function.
        User.add(
            new_user_id,
            user_info['firebase_id'],
            user_info['email'],
            user_info['email_status'],
            user_info['update_frequency'],
            values['profile'],
            values['timezone'],
            user_info['followers'],
            user_info['following'],
            )

    def change_user_id(self, user_id, values):
        """Change user_id and other settings."""
        self._change_user_id_main(user_id, values)
        # Must delete the original user_id outside of the transaction
        # because this user_id row was locked down during the transaction.
        User.delete(user_id)
        # Update user in case the email or update_freq was changed.
        return self.update(values['user_id'], values)

    @ndb.transactional()
    def update(self, user_id, values):
        """Change user settings, but not user_id."""
        self._validate_update(values)

        # If email address is blank, make sure email status is UNINITIALIZED
        user_info = User.get(user_id)
        status = user_info['email_status']
        if len(values['email']) == 0:
            status = EmailStatus.UNINITIALIZED.name
            values['update_frequency'] = UpdateFrequency.NEVER.value

        conf_sent = None
        if self._should_send_conf_email(user_info, values):
            self._send_conf_email(values['email'])
            status = EmailStatus.WAIT_FOR_CONF.name
            conf_sent = datetime.datetime.utcnow()

        return User.update(
            user_id,
            email=values['email'],
            update_frequency=values['update_frequency'],
            email_status=status,
            confirmation_sent=conf_sent,
            profile=values['profile'],
            timezone=values['timezone'],
            )

    @ndb.transactional()
    def update_email_freq(self, email, freq):
        user = User.get(email=email)
        if not user:
            logging.error("could not find user for " + email)
            return

        logging.info('user={} email_freq={}'.format(user['user_id'], freq))
        User.update(user['user_id'], update_frequency=freq)

    @ndb.transactional()
    def update_email_status(self, email, status):
        user = User.get(email=email)
        if not user:
            logging.error('could not find user for ' + email)
            return

        user_id = user['user_id']
        logging.info('user={} email_status={}'.format(user_id, status.name))
        User.update(user_id, email_status=status.name)

    def _should_send_conf_email(self, user_info, values):
        """Return True if a conf email should be sent"""
        # Can't send out email if it is blank
        if len(values['email']) == 0:
            return False

        # New users changing their freq
        never = UpdateFrequency.NEVER.value
        if (user_info['email_status'] == EmailStatus.UNINITIALIZED.name
                and user_info['update_frequency'] == never
                and values['update_frequency'] != never):
            return True

        # Changing email address
        if user_info['email'] != values['email']:
            return True

    def _send_conf_email(self, email):
        text_body = ('Please confirm this email address for use with '
                     'synapcards.com by simply replying to this email.')
        mail.EmailMessage(
            to=email,
            sender='synapcards@gmail.com',
            subject='Please confirm this email address',
            reply_to='confirm@{}.appspotmail.com'.format(Constants.PROJECT_ID),
            body=text_body
            ).send()

    @ndb.transactional()
    def _follow_common(self, req_user_id, user_id, f):
        req_user = User.get(req_user_id)
        if not req_user:
            logging.error("could not find req_user_id " + req_user_id)
            return

        user = User.get(user_id)
        if not user:
            logging.error("could not find user_id " + user_id)
            return

        User.update(
            req_user['user_id'],
            following=f(req_user['following'], [user_id]),
            )

        User.update(
            user['user_id'],
            followers=f(user['followers'], [req_user_id]),
            )

    def follow(self, req_user_id, user_id):
        logging.info('{} following {}'.format(req_user_id, user_id))
        self._follow_common(
            req_user_id, user_id, lambda x, y: list(set(x) | set(y)))

    def unfollow(self, req_user_id, user_id):
        logging.info('{} unfollowing {}'.format(req_user_id, user_id))
        self._follow_common(
            req_user_id, user_id, lambda x, y: list(set(x) - set(y)))
