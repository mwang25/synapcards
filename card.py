import cgi
import datetime
import HTMLParser

from google.appengine.ext import ndb
from jinja2 import Markup
from constants import Constants
from publish_datetime import PublishDatetime


class CardError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class Card(ndb.Model):
    KIND = 'Card'
    owner = ndb.StringProperty()
    title = ndb.StringProperty()
    title_url = ndb.StringProperty()
    source = ndb.StringProperty()
    source_author = ndb.StringProperty()
    # StringProperty has limit of 1500 chars, text is unlimited.
    summary = ndb.TextProperty()
    detailed_notes = ndb.TextProperty()
    rating = ndb.IntegerProperty()
    max_rating = ndb.IntegerProperty()
    privacy = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    source_publish_datetime = ndb.DateTimeProperty()
    source_publish_datetime_format = ndb.StringProperty()
    creation_datetime = ndb.DateTimeProperty()
    last_update_datetime = ndb.DateTimeProperty()

    @classmethod
    def make_card_id(cls, user_id, card_num):
        return user_id + ':' + str(card_num)

    @classmethod
    def split_card_id(cls, card_id):
        a = card_id.split(':')
        return a[0], int(a[1])

    @classmethod
    def _get(cls, card_id):
        return ndb.Key(cls.KIND, card_id).get()

    @classmethod
    def get(cls, card_id, truncate=False):
        card = cls._get(card_id)
        if not card:
            raise CardError('Does not exist')

        return cls._fill_dict(card, truncate)

    @classmethod
    def exists(cls, card_id):
        result = cls._get(card_id)
        return result is not None

    @classmethod
    def add(
        cls,
        card_id,
        title,
        title_url,
        summary,
        author,
        source,
        publish_dt,
        tags,
        rating,
        detailed_notes
    ):
        if cls.exists(card_id):
            msg = 'Cannot add card with existing card_id ({})'.format(card_id)
            raise CardError(msg)

        if int(rating) < 1 or int(rating) > Constants.MAX_RATING:
            raise CardError('invalid rating ({})'.format(rating))

        (user_id, _) = cls.split_card_id(card_id)

        Card(
            key=ndb.Key(cls.KIND, card_id),
            title=title,
            title_url=title_url,
            summary=summary,
            source_author=author,
            source=source,
            source_publish_datetime=publish_dt.datetime,
            source_publish_datetime_format=publish_dt.output_format,
            tags=[t.strip() for t in tags.split(',')],
            rating=int(rating),
            detailed_notes=detailed_notes,
            owner=user_id,
            max_rating=Constants.MAX_RATING,
            privacy='public',
            creation_datetime=datetime.datetime.utcnow(),
            last_update_datetime=datetime.datetime.utcnow(),
        ).put()

    @classmethod
    def update(
        cls,
        card_id,
        title,
        title_url,
        summary,
        author,
        source,
        publish_dt,
        tags,
        rating,
        detailed_notes
    ):
        card = cls._get(card_id)
        if not card:
            raise CardError('Does not exist')

        if int(rating) < 1 or int(rating) > Constants.MAX_RATING:
            raise CardError('invalid rating ({})'.format(rating))

        card.title = title
        card.title_url = title_url
        card.summary = summary
        card.source_author = author
        card.source = source
        card.source_publish_datetime = publish_dt.datetime
        card.source_publish_datetime_format = publish_dt.output_format
        card.tags = [t.strip() for t in tags.split(',')]
        card.rating = int(rating)
        card.detailed_notes = detailed_notes
        card.last_update_datetime = datetime.datetime.utcnow()
        card.put()

    @classmethod
    def delete(cls, card_id):
        ndb.Key(cls.KIND, card_id).delete()

    @classmethod
    def delete_cards_by_user(cls, user_id):
        """Delete all cards added by specified user"""
        query = Card.query(Card.owner == user_id)
        keys = query.fetch(options=ndb.QueryOptions(keys_only=True))
        # According to docs, NDB will automatically collect multiple
        # calls to reduce round trips to server.
        [k.delete() for k in keys]

    @classmethod
    def latest_by_user(cls, user_id, count=3):
        """Return the last count cards added by specified user"""
        query = Card.query(Card.owner == user_id)
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(count)
        return [cls._fill_dict(r, truncate=True) for r in results]

    @classmethod
    def latest_top_rated(cls, count=5):
        # I don't think datastore allows me to query for entries where
        # Card.rating == Card.max_rating, so use global MAX_RATING.
        query = Card.query(Card.rating == Constants.MAX_RATING)
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(count)
        return [cls._fill_dict(r, truncate=True) for r in results]

    @classmethod
    def latest_featured(cls, user_id):
        query = Card.query(
                Card.owner == user_id,
                Card.tags.IN([Constants.FEATURED_CARDS]))
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(8)
        if results and len(results) > 0:
            return cls._fill_featured_values(results)

        return {'featured_cards_id': None}

    @classmethod
    def by_featured_cards_id(cls, card_id):
        if cls.exists(card_id):
            return cls._fill_featured_values([cls._get(card_id)])

        return {'featured_cards_id': None}

    @classmethod
    def _fill_featured_values(cls, results):
        values = {
            'featured_cards_id': results[0].key.string_id(),
            'featured_cards_title': results[0].title,
            'featured_cards_summary': results[0].summary,
            'featured_cards_published': str(PublishDatetime(
                results[0].source_publish_datetime,
                results[0].source_publish_datetime_format)),
            }

        # Get info about each of the featured cards
        cards = []
        for card_id in results[0].detailed_notes.split():
            if cls.exists(card_id):
                cards.append(cls.get(card_id, truncate=True))
        values['featured_cards'] = cards

        # Create links to previous featured cards
        prev_featured_cards = []
        for r in results[1:]:
            prev = {
                'featured_cards_id': r.key.string_id(),
                'featured_cards_title': r.title,
                'featured_cards_published': str(PublishDatetime(
                    r.source_publish_datetime,
                    r.source_publish_datetime_format)),
            }
            prev_featured_cards.append(prev)

        values['prev_featured_cards'] = prev_featured_cards

        return values

    @classmethod
    def _truncate_string(cls, s1, s2, max_len):
        """ Return a truncated s2 where s1 + s2 <= max_len words. """
        s1_len = len(s1.split(' '))
        s2_len = len(s2.split(' '))
        MIN_S2_LEN = 6
        if s1_len + s2_len <= max_len or s2_len < MIN_S2_LEN:
            return s2, False

        truncate_point = MIN_S2_LEN if s1_len > max_len else max_len - s1_len

        return ' '.join(s2.split(' ')[0:truncate_point]), True

    @classmethod
    def _format_detailed_notes(cls, s1, s2, card_id, truncate):
        if not truncate:
            return Markup(HTMLParser.HTMLParser().unescape(s2))

        (notes, trunc) = cls._truncate_string(
                s1, cgi.escape(s2), Constants.MAX_CARD_WORDS)
        if trunc:
            notes += '...<a href="{}/card/{}">[more]</a>'.format(
                    Constants.HOMEPAGE, card_id)
        return Markup(HTMLParser.HTMLParser().unescape(notes))

    @classmethod
    def _fill_dict(cls, card, truncate):
        return {
            'card_id': card.key.string_id(),
            'author': card.source_author,
            'source': card.source,
            'published': str(PublishDatetime(
                card.source_publish_datetime,
                card.source_publish_datetime_format)),
            'tags': ', '.join([u.encode('ascii') for u in card.tags]),
            'rating': card.rating,
            'max_rating': card.max_rating,
            'title': card.title,
            'title_url': card.title_url,
            'summary': card.summary,
            'detailed_notes': cls._format_detailed_notes(
                card.summary,
                card.detailed_notes,
                card.key.string_id(),
                truncate)
        }
