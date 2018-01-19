from card import Card
from constants import Constants


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
        # if args['spec_op'].lower() == 'true':

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
