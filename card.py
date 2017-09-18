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
            return {'card_id1': None}
        return cls._fill_values([result], truncate)

    @classmethod
    def latest_top_rated(cls):
        # This assumes max_rating is 5.  I don't datastore allows me to query
        # for entries where rating == max_rating.
        query = Card.query(Card.rating == 5)
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(4)
        return cls._fill_values(results)

    @classmethod
    def latest_featured(cls, user_id):
        query = Card.query(
                Card.owner == user_id,
                Card.tags.IN([Constants.FEATURED_CARDS]))
        query1 = query.order(-Card.last_update_datetime)
        results = query1.fetch(8)
        if results is None:
            return {
                'featured_cards_id': None,
                'card_id1': None,
                }
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
        if len(results) > 1:
            pub = results[1].source_publish_datetime.strftime(
                results[1].source_publish_datetime_format)
            values['featured_cards_published1'] = pub
            values['featured_cards_id1'] = results[1].key.string_id()
            values['featured_cards_title1'] = results[1].title
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
        values = {
            'card_id1': results[0].key.string_id(),
            'author1': results[0].source_author,
            'source1': results[0].source,
            'published1': results[0].source_publish_datetime.strftime(
                results[0].source_publish_datetime_format),
            'tags1': [u.encode('ascii') for u in results[0].tags],
            'rating1': results[0].rating,
            'max_rating1': results[0].max_rating,
            'title1': results[0].title,
            'title_url1': results[0].title_url,
            'summary1': results[0].summary,
            }
        values['detailed_notes1'] = cls._format_detailed_notes(
                results[0].summary,
                results[0].detailed_notes,
                results[0].key.string_id(),
                truncate)

        if len(results) > 1:
            values['card_id2'] = results[1].key.string_id()
            values['author2'] = results[1].source_author
            values['source2'] = results[1].source
            values['published2'] = results[1].source_publish_datetime.strftime(
                results[1].source_publish_datetime_format)
            values['tags2'] = [u.encode('ascii') for u in results[1].tags]
            values['rating2'] = results[1].rating
            values['max_rating2'] = results[1].max_rating
            values['title2'] = results[1].title
            values['title_url2'] = results[1].title_url
            values['summary2'] = results[1].summary
            values['detailed_notes2'] = cls._format_detailed_notes(
                    results[1].summary,
                    results[1].detailed_notes,
                    results[1].key.string_id(),
                    truncate)

            values['card_id3'] = results[2].key.string_id()
            values['author3'] = results[2].source_author
            values['source3'] = results[2].source
            values['published3'] = results[2].source_publish_datetime.strftime(
                results[2].source_publish_datetime_format)
            values['tags3'] = [u.encode('ascii') for u in results[2].tags]
            values['rating3'] = results[2].rating
            values['max_rating3'] = results[2].max_rating
            values['title3'] = results[2].title
            values['title_url3'] = results[2].title_url
            values['summary3'] = results[2].summary
            values['detailed_notes3'] = cls._format_detailed_notes(
                    results[2].summary,
                    results[2].detailed_notes,
                    results[2].key.string_id(),
                    truncate)

            values['card_id4'] = results[3].key.string_id()
            values['author4'] = results[3].source_author
            values['source4'] = results[3].source
            values['published4'] = results[3].source_publish_datetime.strftime(
                results[3].source_publish_datetime_format)
            values['tags4'] = [u.encode('ascii') for u in results[3].tags]
            values['rating4'] = results[3].rating
            values['max_rating4'] = results[3].max_rating
            values['title4'] = results[3].title
            values['title_url4'] = results[3].title_url
            values['summary4'] = results[3].summary
            values['detailed_notes4'] = cls._format_detailed_notes(
                    results[3].summary,
                    results[3].detailed_notes,
                    results[3].key.string_id(),
                    truncate)

        return values
