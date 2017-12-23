from google.appengine.ext import ndb


class GlobalStats(ndb.Model):
    KIND = 'GlobalStats'
    CARDS = 'cards'
    USERS = 'users'
    DELETED_USERS = 'deleted_users'
    VIEWS = 'views'

    count = ndb.IntegerProperty()

    @classmethod
    def total_cards(cls):
        result = ndb.Key(cls.KIND, cls.CARDS).get()
        return result.count

    @classmethod
    def incr_cards(cls):
        result = ndb.Key(cls.KIND, cls.CARDS).get()
        result.count += 1
        result.put()

    @classmethod
    def decr_cards(cls, count=1):
        result = ndb.Key(cls.KIND, cls.CARDS).get()
        result.count -= count
        result.put()

    @classmethod
    def total_users(cls):
        result = ndb.Key(cls.KIND, cls.USERS).get()
        return result.count

    @classmethod
    def incr_users(cls):
        result = ndb.Key(cls.KIND, cls.USERS).get()
        result.count += 1
        result.put()

    @classmethod
    def decr_users(cls):
        result = ndb.Key(cls.KIND, cls.USERS).get()
        result.count -= 1
        result.put()

    @classmethod
    def incr_deleted_users(cls):
        result = ndb.Key(cls.KIND, cls.DELETED_USERS).get()
        result.count += 1
        result.put()

    @classmethod
    def total_views(cls):
        result = ndb.Key(cls.KIND, cls.VIEWS).get()
        return result.count

    @classmethod
    def incr_views(cls):
        result = ndb.Key(cls.KIND, cls.VIEWS).get()
        result.count += 1
        result.put()
