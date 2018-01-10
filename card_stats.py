from google.appengine.ext import ndb

from card_node import CardNode
from tag import Tag


class CardStats(ndb.Model):
    KIND = 'CardStats'
    AUTHOR_PARENT = ('Field', 'Author')
    SOURCE_PARENT = ('Field', 'Source')
    TAG_PARENT = ('Field', 'Tag')
    count = ndb.IntegerProperty()

    @classmethod
    def _make_key(cls, parent, data):
        seq = list(parent) + [cls.KIND, data]
        return ndb.Key(flat=seq)

    @classmethod
    def _make_parent_key(cls, parent):
        return ndb.Key(flat=list(parent))

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
    def _diff(cls, parent, orig, new):
        orig_set = frozenset(CardNode.as_list(orig))
        new_set = frozenset(CardNode.as_list(new))
        for s in new_set - orig_set:
            cls._incr(cls._make_key(parent, s))
        for s in orig_set - new_set:
            cls._decr(cls._make_key(parent, s))

    @classmethod
    def incr_authors(cls, authors):
        cls._diff(cls.AUTHOR_PARENT, None, authors)

    @classmethod
    def incr_source(cls, source):
        cls._diff(cls.SOURCE_PARENT, None, source)

    @classmethod
    def incr_tags(cls, tags):
        cls._diff(cls.TAG_PARENT, None, tags)

    @classmethod
    def decr_authors(cls, authors):
        cls._diff(cls.AUTHOR_PARENT, authors, None)

    @classmethod
    def decr_source(cls, source):
        cls._diff(cls.SOURCE_PARENT, source, None)

    @classmethod
    def decr_tags(cls, tags):
        cls._diff(cls.TAG_PARENT, tags, None)

    @classmethod
    def diff_authors(cls, orig, new):
        cls._diff(cls.AUTHOR_PARENT, orig, new)

    @classmethod
    def diff_source(cls, orig, new):
        cls._diff(cls.SOURCE_PARENT, orig, new)

    @classmethod
    def diff_tags(cls, orig, new):
        cls._diff(cls.TAG_PARENT, orig, new)

    @classmethod
    def _key_to_unicode(cls, key):
        """Given a utf-8 byte sequence, return unicode string"""
        return key.decode('utf-8', 'replace')

    @classmethod
    def _get_all(cls, parent_key, keys_only=True):
        items = CardStats.query(ancestor=parent_key).fetch(keys_only=keys_only)
        # I think key.id() is an array of bytes encoded in utf-8.  Decode to
        # unicode before returning to user.
        if keys_only:
            return [cls._key_to_unicode(i.id()) for i in items]
        else:
            return items

    @classmethod
    def get_all_authors(cls):
        return cls._get_all(cls._make_parent_key(cls.AUTHOR_PARENT))

    @classmethod
    def get_all_sources(cls):
        return cls._get_all(cls._make_parent_key(cls.SOURCE_PARENT))

    @classmethod
    def get_all_tags(cls):
        return cls._get_all(cls._make_parent_key(cls.TAG_PARENT))

    @classmethod
    def get_all_tags_with_counts(cls):
        parent_key = cls._make_parent_key(cls.TAG_PARENT)
        tags = cls._get_all(parent_key, keys_only=False)
        return [Tag(cls._key_to_unicode(t.key.id()), t.count) for t in tags]
