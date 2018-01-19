from google.appengine.ext import ndb


class GlobalStats(ndb.Model):
    KIND = 'GlobalStats'
    CARDS_PARENT = ['Parent', 'cards']
    CARDS_LEAF = [KIND, 'cards']
    USERS_PARENT = ['Parent', 'users']
    USERS_LEAF = [KIND, 'users']
    DELETED_USERS_LEAF = [KIND, 'deleted_users']
    VIEWS_PARENT = ['Parent', 'views']
    VIEWS_LEAF = [KIND, 'views']

    count = ndb.IntegerProperty()

    @classmethod
    def _make_cards_key(cls):
        return ndb.Key(flat=cls.CARDS_PARENT + cls.CARDS_LEAF)

    @classmethod
    def total_cards(cls):
        result = cls._make_cards_key().get()
        return result.count if result else 0

    @classmethod
    def incr_cards(cls):
        key = cls._make_cards_key()
        result = key.get()
        if result:
            result.count += 1
            result.put()
        else:
            GlobalStats(key=key, count=1).put()

    @classmethod
    def decr_cards(cls, count=1):
        result = cls._make_cards_key().get()
        result.count -= count
        result.put()

    @classmethod
    def _make_users_key(cls):
        return ndb.Key(flat=cls.USERS_PARENT + cls.USERS_LEAF)

    @classmethod
    def total_users(cls):
        result = cls._make_users_key().get()
        return result.count if result else 0

    @classmethod
    def incr_users(cls):
        key = cls._make_users_key()
        result = key.get()
        if result:
            result.count += 1
            result.put()
        else:
            GlobalStats(key=key, count=1).put()

    @classmethod
    def decr_users(cls):
        result = cls._make_users_key().get()
        result.count -= 1
        result.put()

    @classmethod
    def _make_deleted_users_key(cls):
        return ndb.Key(flat=cls.USERS_PARENT + cls.DELETED_USERS_LEAF)

    @classmethod
    def incr_deleted_users(cls):
        key = cls._make_deleted_users_key()
        result = key.get()
        if result:
            result.count += 1
            result.put()
        else:
            GlobalStats(key=key, count=1).put()

    @classmethod
    def _make_views_key(cls):
        return ndb.Key(flat=cls.VIEWS_PARENT + cls.VIEWS_LEAF)

    @classmethod
    def total_views(cls):
        result = cls._make_views_key().get()
        return result.count if result else 0

    @classmethod
    def incr_views(cls):
        key = cls._make_views_key()
        result = key.get()
        if result:
            result.count += 1
            result.put()
        else:
            GlobalStats(key=key, count=1).put()
