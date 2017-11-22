from global_stats import GlobalStats
from card import Card
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
    def add(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])

        user_dict = User.get(user_id)
        if user_dict['total_cards'] >= user_dict['max_cards']:
            raise CardManagerError('User max card limit reached')

        card_id = Card.make_card_id(user_id, user_dict['next_card_num'])
        Card.add(
            card_id,
            values['title'],
            values['title_url'],
            values['summary'],
            values['author'],
            values['source'],
            values['tags'],
            values['rating'],
            values['detailed_notes'])
        User.incr_cards(user_id)
        GlobalStats.incr_cards()
        return Card.get(card_id)

    @classmethod
    def update(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])

        card_id = Card.make_card_id(user_id, values['card_num'])
        Card.update(
            card_id,
            values['title'],
            values['title_url'],
            values['summary'],
            values['author'],
            values['source'],
            values['tags'],
            values['rating'],
            values['detailed_notes'])
        return Card.get(card_id)

    @classmethod
    def delete(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])

        card_id = Card.make_card_id(user_id, values['card_num'])
        Card.delete(card_id)
        User.decr_cards(user_id)
        GlobalStats.decr_cards()

    @classmethod
    def get(cls, values):
        # No authentication check for just getting the card
        card_id = Card.make_card_id(values['user_id'], values['card_num'])
        return Card.get(card_id)
