from author_node import AuthorNode
from card import Card
from card_node import CardNode
from card_stats import CardStats
from constants import Constants
from global_stats import GlobalStats
from publish_datetime import PublishDatetime
from tag_node import TagNode
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

        # create Tag and Author objects just to validate them
        [TagNode(t, 0) for t in CardNode.as_list(values['tags'])]
        [AuthorNode(t, 0) for a in CardNode.as_list(values['authors'])]

    @classmethod
    def _localize_timestamp(cls, timestamp, user_tzname):
        pdt = PublishDatetime.parse_string(timestamp)
        pdt.set_timezone(user_tzname)
        return str(pdt)

    @classmethod
    def add(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])
        cls._verify_required_fields(values)
        cls._verify_values(values)

        user_dict = User.get(user_id)
        if user_dict['total_cards'] >= user_dict['max_cards']:
            raise CardManagerError('User max card limit reached')

        card_id = Card.make_card_id(user_id, user_dict['next_card_num'])
        User.incr_next_card_num(user_id)

        if Constants.FEATURED_CARDS in values['tags']:
            values['title_url'] = '{}/featuredcards/{}'.format(
                Constants.HOMEPAGE, card_id)

        Card.add(
            card_id,
            values['title'],
            values['title_url'],
            values['summary'],
            CardNode.as_list(values['authors']),
            values['source'],
            PublishDatetime().parse_string(values['published']),
            CardNode.as_list(values['tags']),
            int(values['rating']),
            values['detailed_notes'])

        CardStats.incr_authors(values['authors'])
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
            CardNode.as_list(values['authors']),
            values['source'],
            PublishDatetime().parse_string(values['published']),
            CardNode.as_list(values['tags']),
            int(values['rating']),
            values['detailed_notes'])

        CardStats.diff_authors(orig['authors'], values['authors'])
        CardStats.diff_source(orig['source'], values['source'])
        CardStats.diff_tags(orig['tags'], values['tags'])

        return Card.get(card_id)

    @classmethod
    def delete(cls, user_id, values):
        cls._verify_user_id(user_id, values['user_id'])

        card_id = Card.make_card_id(user_id, values['card_num'])
        orig = Card.get(card_id)
        Card.delete(card_id)
        CardStats.decr_authors(orig['authors'])
        CardStats.decr_source(orig['source'])
        CardStats.decr_tags(orig['tags'])
        User.decr_cards(user_id)
        GlobalStats.decr_cards()

    @classmethod
    def like(cls, values):
        user_id = values['user_id']
        if not User.exists(user_id):
            msg = 'User does not exist ' + user_id
            raise CardManagerError(msg)

        card_id = values['card_id']
        card_dict = Card.get(card_id)
        liked_by = Card.liked_by_as_list(card_dict['liked_by'])
        Card.update_likes(card_id, list(set(liked_by) | set([user_id])))

        return cls.get(values)

    @classmethod
    def unlike(cls, values):
        # delete user_id even if it does not exist anymore
        user_id = values['user_id']

        card_id = values['card_id']
        card_dict = Card.get(card_id)
        liked_by = Card.liked_by_as_list(card_dict['liked_by'])
        Card.update_likes(card_id, list(set(liked_by) - set([user_id])))

        return cls.get(values)

    @classmethod
    def get(cls, values):
        # No authentication check for just getting the card
        # Use card_id if present, otherwise make it from user_id and card_num
        if 'card_id' in values:
            card_id = values['card_id']
        else:
            card_id = Card.make_card_id(values['user_id'], values['card_num'])
        card_dict = Card.get(card_id)

        # insert another set of timestamps localized to user's timezone
        user_tzname = User.get_tzname(values['user_id'])
        card_dict['created_loc'] = cls._localize_timestamp(
            card_dict['created'], user_tzname)
        card_dict['updated_loc'] = cls._localize_timestamp(
            card_dict['updated'], user_tzname)

        return card_dict
