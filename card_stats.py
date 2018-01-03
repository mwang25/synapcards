from google.appengine.ext import ndb

from card import Card
from tag import Tag


class CardStats(ndb.Model):
    KIND = 'CardStats'
    AUTHOR_PARENT = ('Field', 'Author')
    SOURCE_PARENT = ('Field', 'Source')
    TAG_PARENT = ('Field', 'Tag')
    count = ndb.IntegerProperty()

    @classmethod
    def _empty_data(cls, data):
        if not data or len(data) == 0:
            return True
        return False

    @classmethod
    def _make_key(cls, parent, data):
        seq = list(parent) + [cls.KIND, data]
        return ndb.Key(flat=seq)

    @classmethod
    def _make_parent_key(cls, parent):
        return ndb.Key(flat=list(parent))

    @classmethod
    def _make_frozenset(cls, tags):
        if not tags or len(tags) == 0:
            return frozenset([])
        return frozenset(Tag.as_list(tags))

    @classmethod
    def _incr(cls, key):
        """Increment the key's count.  If not in db, create with count of 1"""
        result = key.get()
        if result:
            result.count += 1
            result.put()
        else:
            CardStats(key=key, count=1).put()

    @classmethod
    def incr_author(cls, author):
        if cls._empty_data(author):
            return

        cls._incr(cls._make_key(cls.AUTHOR_PARENT, author))

    @classmethod
    def incr_source(cls, source):
        if cls._empty_data(source):
            return

        cls._incr(cls._make_key(cls.SOURCE_PARENT, source))

    @classmethod
    def incr_tags(cls, tags):
        if cls._empty_data(tags):
            return

        for t in Tag.as_list(tags):
            cls._incr(cls._make_key(cls.TAG_PARENT, t))

    @classmethod
    def _decr(cls, key):
        """Decrement the key's count.  Delete entry if count is 0"""
        result = key.get()
        if result:
            if result.count <= 1:
                key.delete()
            else:
                result.count -= 1
                result.put()

    @classmethod
    def decr_author(cls, author):
        if cls._empty_data(author):
            return

        cls._decr(cls._make_key(cls.AUTHOR_PARENT, author))

    @classmethod
    def decr_source(cls, source):
        if cls._empty_data(source):
            return

        cls._decr(cls._make_key(cls.SOURCE_PARENT, source))

    @classmethod
    def decr_tags(cls, tags):
        if cls._empty_data(tags):
            return

        for t in Tag.as_list(tags):
            cls._decr(cls._make_key(cls.TAG_PARENT, t))

    @classmethod
    def _diff(cls, parent, orig, new):
        if orig != new:
            if len(orig):
                cls._decr(cls._make_key(parent, orig))
            if len(new):
                cls._incr(cls._make_key(parent, new))

    @classmethod
    def diff_author(cls, orig, new):
        cls._diff(cls.AUTHOR_PARENT, orig, new)

    @classmethod
    def diff_source(cls, orig, new):
        cls._diff(cls.SOURCE_PARENT, orig, new)

    @classmethod
    def diff_tags(cls, orig, new):
        orig_set = cls._make_frozenset(orig)
        new_set = cls._make_frozenset(new)
        for t in new_set - orig_set:
            cls._incr(cls._make_key(cls.TAG_PARENT, t))
        for t in orig_set - new_set:
            cls._decr(cls._make_key(cls.TAG_PARENT, t))

    @classmethod
    def _get_all(cls, parent_key):
        keys = CardStats.query(ancestor=parent_key).fetch(keys_only=True)
        # I think key.id() is an array of bytes, so convert to utf-8 before
        # sending it back to the caller.
        return [k.id().decode('utf-8', 'replace') for k in keys]

    @classmethod
    def get_all_authors(cls):
        return cls._get_all(cls._make_parent_key(cls.AUTHOR_PARENT))

    @classmethod
    def get_all_sources(cls):
        return cls._get_all(cls._make_parent_key(cls.SOURCE_PARENT))

    @classmethod
    def get_all_tags(cls):
        return cls._get_all(cls._make_parent_key(cls.TAG_PARENT))
