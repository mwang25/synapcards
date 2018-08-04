from card import Card
from constants import Constants
from like import Like
from publish_datetime import PublishDatetime
from user import User


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

    def _augment_like(self, k, tzname):
        card = Card.get(k['card_id'])
        k['title'] = card['title']
        # Convert the like timestamp to just MDY in user's timezone
        pdt = PublishDatetime.parse_string(k['timestamp'])
        pdt.set_timezone(tzname)
        pdt.output_format = PublishDatetime.MDY_FORMAT
        k['date'] = str(pdt)
        return k

    def latest_likes_by(self, user_id, count=Constants.SEARCH_DEFAULT_COUNT):
        tzname = User.get(user_id)['timezone']
        likes = Like.latest_likes_by(user_id, count)
        return [self._augment_like(k, tzname) for k in likes]

    def latest_likes_of(self, user_id, min_datetime, max_datetime):
        tzname = User.get(user_id)['timezone']
        likes = Like.latest_likes_of(user_id, min_datetime, max_datetime)
        return [self._augment_like(k, tzname) for k in likes]
