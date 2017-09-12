from google.appengine.ext import ndb


class GlobalStats(ndb.Model):
    KIND = 'GlobalStats'
    CARDS = 'cards'
    USERS = 'users'
    VIEWS = 'views'

    count = ndb.IntegerProperty()

    @classmethod
    def total_cards(cls):
        result = ndb.Key(cls.KIND, cls.CARDS).get()
        return result.count

    @classmethod
    def total_users(cls):
        result = ndb.Key(cls.KIND, cls.USERS).get()
        return result.count

    @classmethod
    def total_views(cls):
        result = ndb.Key(cls.KIND, cls.VIEWS).get()
        return result.count

    @classmethod
    def incr_views(cls):
        result = ndb.Key(cls.KIND, cls.VIEWS).get()
        result.count += 1
        result.put()
