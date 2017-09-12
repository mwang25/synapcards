from google.appengine.ext import ndb


class User(ndb.Model):
    KIND = 'User'
    # StringProperty has limit of 1500 chars, text is unlimited.
    profile = ndb.TextProperty()
    total_cards = ndb.IntegerProperty()

    @classmethod
    def by_id(cls, user_id):
        k = ndb.Key(cls.KIND, user_id)
        result = k.get()
        if result is None:
            return {'user_id': None}
        return cls._fill_values(result)

    @classmethod
    def _fill_values(cls, result):
        values = {
            'user_id': result.key.string_id(),
            'user_profile': result.profile,
            'user_total_cards': result.total_cards,
            }
        return values
