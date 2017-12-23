from card import Card
from card_stats import CardStats
from constants import Constants
from global_stats import GlobalStats
from user import User
from user_id import BadUserIdError
from user_id import UserId


class UserManagerError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class UserManager():
    @classmethod
    def add(cls, firebase_id, email):
        if GlobalStats.total_users() >= Constants.MAX_USERS:
            raise UserManagerError('cannot add any more users')
        if User.exists(firebase_id=firebase_id):
            raise UserManagerError('duplicate firebase id detected')

        user_id = UserId.generate_id(email)
        User.add(user_id, firebase_id, email)
        GlobalStats.incr_users()

        user_info = User.get(user_id)
        if user_info is None:
            raise UserManagerError('cannot find newly added user')
        return user_info

    @classmethod
    def _delete_all_user_cards(cls, user_id):
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
                CardStats.decr_author(c['author'])
                CardStats.decr_source(c['source'])
                CardStats.decr_tags(c['tags'])
                Card.delete(c['card_id'])

        GlobalStats.decr_cards(count)

    @classmethod
    def delete(cls, user_id):
        cls._delete_all_user_cards(user_id)
        User.delete(user_id)
        GlobalStats.decr_users()
        GlobalStats.incr_deleted_users()
        return {}

    @classmethod
    def update(cls, user_id, values):
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
            )
