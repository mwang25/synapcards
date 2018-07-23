from card import Card
from like import Like


class LikeManager():
    def like(self, values):
        # Existence of card_id and user_id was already verified in
        # previous call to CardManager.like
        user_id = values['user_id']
        card_id = values['card_id']
        card_owner, _ = Card.split_card_id(card_id)
        Like.like(user_id, card_id, card_owner)

    def unlike(self, values):
        # Delete the entry regardless of whether card_id or user_id exists
        user_id = values['user_id']
        card_id = values['card_id']
        Like.unlike(user_id, card_id)
