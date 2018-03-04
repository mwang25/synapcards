import datetime

from google.appengine.ext import ndb
from constants import Constants
from email_status import EmailStatus
from update_frequency import UpdateFrequency


class UserOperationError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class User(ndb.Model):
    KIND = 'User'
    USER_PARENT = ['Parent', 'all']
    # StringProperty has limit of 1500 chars, text is unlimited.
    firebase_id = ndb.StringProperty()
    email = ndb.StringProperty()
    email_status = ndb.StringProperty()
    timezone = ndb.StringProperty()
    profile = ndb.TextProperty()
    # auto_now_add=True in DateTimeProperties mysteriously creates two entries.
    created = ndb.DateTimeProperty()
    total_cards = ndb.IntegerProperty()
    next_card_num = ndb.IntegerProperty()
    max_cards = ndb.IntegerProperty()
    following = ndb.StringProperty(repeated=True)
    followers = ndb.StringProperty(repeated=True)
    update_frequency = ndb.StringProperty()

    @classmethod
    def _make_key(cls, user_id):
        return ndb.Key(flat=cls.USER_PARENT + [cls.KIND, user_id])

    @classmethod
    def _make_parent_key(cls):
        return ndb.Key(flat=cls.USER_PARENT)

    @classmethod
    def _make_ancestor_query(cls):
        return User.query(ancestor=cls._make_parent_key())

    @classmethod
    def _query_user_id(cls, user_id):
        return cls._make_key(user_id).get()

    @classmethod
    def _query_firebase_id(cls, firebase_id):
        q = cls._make_ancestor_query()
        results = q.filter(User.firebase_id == firebase_id).fetch(1)
        return None if len(results) == 0 else results[0]

    @classmethod
    def _query_email(cls, email):
        q = cls._make_ancestor_query()
        results = q.filter(User.email == email).fetch(1)
        return None if len(results) == 0 else results[0]

    @classmethod
    def query_most_cards(cls):
        q = cls._make_ancestor_query()
        query = q.filter(User.total_cards > 0)
        results = query.order(-User.total_cards).fetch(5)
        return [cls._fill_dict(r) for r in results]

    @classmethod
    def get_update_emails(cls, update_frequency):
        email_dict = {}
        q = cls._make_ancestor_query()
        query = q.filter(User.update_frequency == update_frequency)
        keys = query.fetch(keys_only=True)
        for k in keys:
            user_id = k.id()
            user = cls.get(user_id)
            if user['email_status'] == EmailStatus.CONFIRMED_GOOD.name:
                email_dict[user_id] = user['email']
        return email_dict

    @classmethod
    def exists(cls, user_id=None, firebase_id=None):
        result = cls.get(user_id, firebase_id)
        return result is not None

    @classmethod
    def get_all(cls):
        keys = cls._make_ancestor_query().fetch(keys_only=True)
        return [k.id() for k in keys]

    @classmethod
    def get(cls, user_id=None, firebase_id=None, email=None):
        if not user_id and not firebase_id and not email:
            raise RuntimeError('must specify user_id, firebase_id, or email')

        if user_id:
            result = cls._query_user_id(user_id)
        elif firebase_id:
            result = cls._query_firebase_id(firebase_id)
        elif email:
            result = cls._query_email(email)
        return None if not result else cls._fill_dict(result)

    @classmethod
    def split_strip(cls, s):
        """Given elements in a comma separated string, return as a list"""
        if not s:
            return []
        if not len(s):
            return []
        return [element.strip() for element in s.split(',')]

    @classmethod
    def add(
            cls,
            user_id,
            firebase_id,
            email,
            email_status=EmailStatus.UNINITIALIZED.name,
            update_freq=UpdateFrequency.NEVER.value,
            profile='',
            timezone='UTC',
            followers=[],
            following=[]):
        User(
            key=cls._make_key(user_id),
            firebase_id=firebase_id,
            email=email,
            email_status=email_status,
            timezone=timezone,
            profile=profile,
            created=datetime.datetime.utcnow(),
            total_cards=0,
            next_card_num=1,
            max_cards=Constants.MAX_CARDS_PER_USER,
            following=followers,
            followers=following,
            update_frequency=update_freq,
            ).put()

        return cls.get(user_id)

    @classmethod
    def delete(cls, user_id):
        cls._make_key(user_id).delete()

    @classmethod
    def update(
            cls,
            user_id,
            email=None,
            email_status=None,
            update_frequency=None,
            profile=None,
            timezone=None,
            following=None,
            followers=None):
        result = cls._query_user_id(user_id)
        if email:
            result.email = email
        if profile:
            result.profile = profile
        if timezone:
            result.timezone = timezone
        # Specifically test for None because [] also tests false
        if following is not None:
            result.following = following
        if followers is not None:
            result.followers = followers
        if update_frequency:
            result.update_frequency = update_frequency
        # TODO: if email has changed, status should go to CONF_WAITING
        if email_status:
            result.email_status = email_status
        result.put()

        return cls.get(user_id)

    @classmethod
    def incr_next_card_num(cls, user_id):
        user = cls._query_user_id(user_id)
        user.next_card_num += 1
        user.put()

    @classmethod
    def incr_cards(cls, user_id):
        user = cls._query_user_id(user_id)
        user.total_cards += 1
        user.put()

    @classmethod
    def decr_cards(cls, user_id):
        user = cls._query_user_id(user_id)
        user.total_cards -= 1
        user.put()

    @classmethod
    def _fill_dict(cls, result):
        following = result.following if result.following else []
        followers = result.followers if result.followers else []
        update_frequency = UpdateFrequency.NEVER.value
        if result.update_frequency:
            update_frequency = result.update_frequency

        return {
            'user_id': result.key.string_id(),
            'firebase_id': result.firebase_id,
            'email': result.email,
            'email_status': result.email_status,
            'profile': result.profile,
            'timezone': result.timezone,
            'total_cards': result.total_cards,
            'next_card_num': result.next_card_num,
            'max_cards': result.max_cards,
            'following': following,
            'followers': followers,
            'update_frequency': update_frequency,
            }
