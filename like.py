import datetime

from google.appengine.ext import ndb

from constants import Constants
from publish_datetime import PublishDatetime


class Like(ndb.Model):
    KIND = 'Like'
    liker = ndb.StringProperty()
    card_id = ndb.StringProperty()
    card_owner = ndb.StringProperty()
    like_datetime = ndb.DateTimeProperty()

    @classmethod
    def like(cls, liker, card_id, card_owner):
        likes = cls._search({'liker': liker, 'card_id': card_id})
        if len(likes):
            return

        Like(
          liker=liker,
          card_id=card_id,
          card_owner=card_owner,
          like_datetime=datetime.datetime.utcnow()
        ).put()

    @classmethod
    def unlike(cls, liker, card_id):
        likes = cls._search(
            {'liker': liker, 'card_id': card_id},
            keys_only=True)
        for k in likes:
            k.delete()

    @classmethod
    def latest_likes_by(cls, user_id, count):
        likes = cls._search({
            'liker': user_id,
            'count': count,
        })
        return [cls._fill_dict(k) for k in likes]

    @classmethod
    def latest_likes_of(cls, user_id, min_datetime, max_datetime):
        """Return likes received by specified user_id"""
        likes = cls._search({
            'card_owner': user_id,
            'min_datetime': min_datetime,
            'max_datetime': max_datetime,
        })
        return [cls._fill_dict(k) for k in likes]

    @classmethod
    def _search(cls, args, keys_only=False):
        query = Like.query()
        if 'card_id' in args:
            query = query.filter(Like.card_id == args['card_id'])
        if 'card_owner' in args:
            query = query.filter(Like.card_owner == args['card_owner'])
        if 'liker' in args:
            query = query.filter(Like.liker == args['liker'])
        if 'min_datetime' in args:
            query = query.filter(
                Like.like_datetime >= args['min_datetime'])
        if 'max_datetime' in args:
            query = query.filter(
                Like.like_datetime < args['max_datetime'])
        query = query.order(-Like.like_datetime)
        if keys_only:
            return query.fetch(keys_only=True)
        else:
            count = int(args.get('count', Constants.SEARCH_DEFAULT_COUNT))
            return query.fetch(count)

    @classmethod
    def _fill_dict(cls, like):
        return {
            'timestamp': str(PublishDatetime(
                like.like_datetime,
                PublishDatetime.CREATE_UPDATE_FORMAT)),
            'liker': like.liker,
            'card_id': like.card_id,
            'card_owner': like.card_owner,
        }
