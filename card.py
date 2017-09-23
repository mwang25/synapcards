import cgi

from google.appengine.ext import ndb
from jinja2 import Markup
from constants import Constants


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
    tags = ndb.StringProperty(repeated=True)
    source_publish_datetime = ndb.DateTimeProperty()
    source_publish_datetime_format = ndb.StringProperty()
    creation_datetime = ndb.DateTimeProperty()
    last_update_datetime = ndb.DateTimeProperty()

    @classmethod
    def by_id(cls, card_id, truncate):
        k = ndb.Key(cls.KIND, card_id)
        result = k.get()
        if result is None:
            return {'cards': []}
        return cls._fill_values([result], truncate)

    @classmethod
    def latest_top_rated(cls):
        # This assumes max_rating is 5.  I don't think datastore allows me to
        # query for entries where rating == max_rating.
        query = Card.query(Card.rating == 5)
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(5)
        return cls._fill_values(results)

    @classmethod
    def latest_featured(cls, user_id):
        query = Card.query(
                Card.owner == user_id,
                Card.tags.IN([Constants.FEATURED_CARDS]))
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(8)
        if results is None:
            return {'featured_cards_id': None}
        return cls._fill_featured_values(results)

    @classmethod
    def by_featured_cards_id(cls, card_id):
        k = ndb.Key(cls.KIND, card_id)
        result = k.get()
        if result is None:
            return {'featured_cards_id': None}
        return cls._fill_featured_values([result])

    @classmethod
    def _fill_featured_values(cls, results):
        values = {
            'featured_cards_id': results[0].key.string_id(),
            'featured_cards_title': results[0].title,
            'featured_cards_published':
                results[0].source_publish_datetime.strftime(
                    results[0].source_publish_datetime_format),
            }

        # Get info about each of the featured cards
        card_results = []
        for card_id in results[0].detailed_notes.split():
            r = ndb.Key(cls.KIND, card_id).get()
            if r is not None:
                card_results.append(r)

        values.update(cls._fill_values(card_results))

        # Create links to previous featured cards
        prev_featured_cards = []
        for r in results[1:]:
            prev = {
                'featured_cards_id': r.key.string_id(),
                'featured_cards_title': r.title,
                'featured_cards_published':
                    r.source_publish_datetime.strftime(
                        r.source_publish_datetime_format),
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
            return s2

        (notes, trunc) = cls._truncate_string(
                s1, cgi.escape(s2), Constants.MAX_CARD_WORDS)
        if trunc:
            notes += '...<a href="{}/card/{}">[more]</a>'.format(
                    Constants.HOMEPAGE, card_id)
        return Markup(notes)

    @classmethod
    def _fill_values(cls, results, truncate=True):
        cards = []
        for r in results:
            c = {
                'card_id': r.key.string_id(),
                'author': r.source_author,
                'source': r.source,
                'published': r.source_publish_datetime.strftime(
                    r.source_publish_datetime_format),
                'tags': [u.encode('ascii') for u in r.tags],
                'rating': r.rating,
                'max_rating': r.max_rating,
                'title': r.title,
                'title_url': r.title_url,
                'summary': r.summary,
                'detailed_notes': cls._format_detailed_notes(
                    r.summary, r.detailed_notes, r.key.string_id(), truncate)
            }
            cards.append(c)

        return {'cards': cards}
