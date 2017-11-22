import datetime

from google.appengine.ext import ndb
from constants import Constants


class UserOperationError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class User(ndb.Model):
    KIND = 'User'
    # StringProperty has limit of 1500 chars, text is unlimited.
    firebase_id = ndb.StringProperty()
    email = ndb.StringProperty()
    timezone = ndb.StringProperty()
    profile = ndb.TextProperty()
    # auto_now_add=True in DateTimeProperties mysteriously creates two entries.
    created = ndb.DateTimeProperty()
    total_cards = ndb.IntegerProperty()
    next_card_num = ndb.IntegerProperty()
    max_cards = ndb.IntegerProperty()

    @classmethod
    def _query_user_id(cls, user_id):
        k = ndb.Key(cls.KIND, user_id)
        result = k.get()
        return result

    @classmethod
    def _query_firebase_id(cls, firebase_id):
        results = User.query(User.firebase_id == firebase_id).fetch(1)
        return None if len(results) == 0 else results[0]

    @classmethod
    def query_most_cards(cls):
        query = User.query(User.total_cards > 0)
        results = query.order(-User.total_cards).fetch(5)
        return [cls._fill_dict(r) for r in results]

    @classmethod
    def exists(cls, user_id=None, firebase_id=None):
        result = cls.get(user_id, firebase_id)
        return result is not None

    @classmethod
    def get(cls, user_id=None, firebase_id=None):
        if user_id is None and firebase_id is None:
            raise RuntimeError('must specify either user_id or firebase_id')

        if user_id is not None:
            result = cls._query_user_id(user_id)
        elif firebase_id is not None:
            result = cls._query_firebase_id(firebase_id)
        return None if result is None else cls._fill_dict(result)

    @classmethod
    def add(cls, user_id, firebase_id, email, profile='', timezone='UTC'):
        User(
            key=ndb.Key(cls.KIND, user_id),
            firebase_id=firebase_id,
            email=email,
            timezone=timezone,
            profile=profile,
            created=datetime.datetime.utcnow(),
            total_cards=0,
            next_card_num=1,
            max_cards=Constants.MAX_CARDS_PER_USER,
            ).put()

    @classmethod
    def delete(cls, user_id):
        k = ndb.Key(cls.KIND, user_id)
        k.delete()

    @classmethod
    def update(cls, orig_user_id, new_user_id, email, profile, timezone):
        result = cls._query_user_id(orig_user_id)
        if orig_user_id != new_user_id:
            cls.delete(orig_user_id)
            cls.add(new_user_id, result.firebase_id, email, profile, timezone)
        else:
            result.email = email
            result.profile = profile
            result.timezone = timezone
            result.put()

        return cls.get(new_user_id)

    @classmethod
    def incr_cards(cls, user_id):
        user = cls._query_user_id(user_id)
        user.total_cards += 1
        user.next_card_num += 1
        user.put()

    @classmethod
    def decr_cards(cls, user_id):
        user = cls._query_user_id(user_id)
        user.total_cards -= 1
        user.put()

    @classmethod
    def _fill_dict(cls, result):
        values = {
            'user_id': result.key.string_id(),
            'email': result.email,
            'profile': result.profile,
            'timezone': result.timezone,
            'total_cards': result.total_cards,
            'next_card_num': result.next_card_num,
            'max_cards': result.max_cards,
            }
        return values
