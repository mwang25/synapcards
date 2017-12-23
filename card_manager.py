from card import Card
from card_stats import CardStats
from constants import Constants
from global_stats import GlobalStats
from publish_datetime import PublishDatetime
from user import User


class CardManagerError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class CardManager():
    @classmethod
    def _verify_user_id(cls, user_id1, user_id2):
        if user_id1 != user_id2:
            raise CardManagerError('permission denied: user_id mismatch')

    @classmethod
    def _verify_required_fields(cls, values):
        if len(values['title']) == 0:
            raise CardManagerError('Card must have title')

    @classmethod
    def _verify_values(cls, values):
        rating = int(values['rating'])
        if int(rating) < 1 or int(rating) > Constants.MAX_RATING:
            raise CardManagerError('invalid rating ({})'.format(rating))

    @classmethod
    def add(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])
        cls._verify_required_fields(values)
        cls._verify_values(values)

        user_dict = User.get(user_id)
        if user_dict['total_cards'] >= user_dict['max_cards']:
            raise CardManagerError('User max card limit reached')

        card_id = Card.make_card_id(user_id, user_dict['next_card_num'])
        if Constants.FEATURED_CARDS in values['tags']:
            values['title_url'] = '{}/featuredcards/{}'.format(
                Constants.HOMEPAGE, card_id)

        Card.add(
            card_id,
            values['title'],
            values['title_url'],
            values['summary'],
            values['author'],
            values['source'],
            PublishDatetime().parse_string(values['published']),
            values['tags'],
            int(values['rating']),
            values['detailed_notes'])

        CardStats.incr_author(values['author'])
        CardStats.incr_source(values['source'])
        CardStats.incr_tags(values['tags'])
        User.incr_cards(user_id)
        GlobalStats.incr_cards()

        return Card.get(card_id)

    @classmethod
    def update(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])
        cls._verify_required_fields(values)
        cls._verify_values(values)

        card_id = Card.make_card_id(user_id, values['card_num'])
        orig = Card.get(card_id)
        Card.update(
            card_id,
            values['title'],
            values['title_url'],
            values['summary'],
            values['author'],
            values['source'],
            PublishDatetime().parse_string(values['published']),
            values['tags'],
            int(values['rating']),
            values['detailed_notes'])

        CardStats.diff_author(orig['author'], values['author'])
        CardStats.diff_source(orig['source'], values['source'])
        CardStats.diff_tags(orig['tags'], values['tags'])

        return Card.get(card_id)

    @classmethod
    def delete(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])

        card_id = Card.make_card_id(user_id, values['card_num'])
        orig = Card.get(card_id)
        Card.delete(card_id)
        CardStats.decr_author(orig['author'])
        CardStats.decr_source(orig['source'])
        CardStats.decr_tags(orig['tags'])
        User.decr_cards(user_id)
        GlobalStats.decr_cards()

    @classmethod
    def get(cls, values):
        # No authentication check for just getting the card
        card_id = Card.make_card_id(values['user_id'], values['card_num'])
        return Card.get(card_id)
