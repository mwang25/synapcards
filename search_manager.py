from card import Card
from constants import Constants
from publish_datetime import PublishDatetime
from user import User


class SearchManagerError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class SearchManager():
    @classmethod
    def search(cls, args):
        values = {
            'cards': [],
            'summarized_cards': [],
            'search_stats': '',
        }
        if args.get('new_search', False):
            return values

        # hook for triggering some special operation
        # if args.get('spec_op', 'false').lower() == 'true':

        # First get total cards that matches filter
        total = len(Card.search(args, keys_only=True))
        if total == 0:
            values['search_stats'] = 'no cards matched your search'
            return values

        # Now get the number of cards user asked for
        cards = Card.search(args)
        if len(cards) > Constants.SEARCH_SUMMARIZE_THRESHOLD:
            values['summarized_cards'] = [cls._summarize(c) for c in cards]
        else:
            values['cards'] = cards
        values['search_stats'] = '{} of {} results shown'.format(
            len(cards), total)
        return values

    @classmethod
    def search_for_dump(cls, args):
        user_tzname = User.get_tzname(args['user_id'])
        cards = Card.search(args, truncate=False, web=False)
        for c in cards:
            c['created_loc'] = cls._localize_timestamp(
                c['created'], user_tzname)
            c['updated_loc'] = cls._localize_timestamp(
                c['updated'], user_tzname)
            c['title'] = cls._format_for_dump(c['title'])
            c['summary'] = cls._format_for_dump(c['summary'])
            c['detailed_notes'] = cls._format_for_dump(c['detailed_notes'])

        return {'cards': cards}

    @classmethod
    def _summarize(cls, card):
        line = u'({}/{}) {} [{}] {}'.format(
            card['rating'],
            Constants.MAX_RATING,
            card['authors'],
            card['source'],
            card['title'])
        return {
            'card_id': card['card_id'],
            'line': line}

    @classmethod
    def _localize_timestamp(cls, timestamp, user_tzname):
        # TODO: unify this func with copy in card_manager
        pdt = PublishDatetime.parse_string(timestamp)
        pdt.set_timezone(user_tzname)
        return str(pdt)

    @classmethod
    def _format_for_dump(cls, s):
        # This is not the full list of characters that need to escaped, but
        # the most likely ones are here.
        s = s.replace('\\', '\\\\')
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        return s
