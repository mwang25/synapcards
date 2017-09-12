# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# from google.cloud import datastore
# in appengine, must use ndb, cannot import datastore directly
from google.appengine.ext import ndb

import pytz
import webapp2

from cardhandler import CardHandler
from featuredcardshandler import FeaturedCardsHandler
from indexhandler import IndexHandler
from userhandler import UserHandler


class CardOldHandler(webapp2.RequestHandler):
    def get(self, card_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('You requested card {}\n'.format(card_id))
        k = ndb.Key('Card', card_id)
        # data = Card(key=k, title=u'abc', title_url=u'https')
        # data.put()
        result = k.get()
        # query = datastore_client.query(kind='cards')
        # query.key_filter(task_key, '=')
        # query.add_filter('priority', '>=', 4)
        # query.order = ['-priority']
        # query = self.datastore_client.query()
        # results = list(query.fetch(limit=5))
        # print 'Got {} results'.format(len(results))
        # result = results[0]
        self.response.write('key:{}\n'.format(result.key.string_id()))
        self.response.write('Title:{}\n'.format(result.title))
        self.response.write('Title_url:{}\n'.format(result.title_url))
        self.response.write('Rating:{}\n'.format(result.rating))
        self.response.write('Summary:{}\n'.format(result.summary))
        self.response.write('DetailedNotes:{}\n'.format(result.detailed_notes))
        self.response.write('Tags:{}\n'.format(
            [u.encode('ascii') for u in result.tags]))
        publish_dt = result.source_publish_datetime
        self.response.write('Published:{}\n'.format(
            publish_dt.strftime('%B %Y')))

        # datetimes in ndb are UTC but are naive, so attach UTC timezeone.
        creation_dt = pytz.utc.localize(result.creation_datetime)
        mytz = pytz.timezone('US/Pacific')
        # I want to do creation_dt.astimezone(mytz)
        self.response.write('Card created:{}\n'.format(
            creation_dt.astimezone(mytz).strftime('%m/%d/%Y %H:%M %Z')))


class UserOldHandler(webapp2.RequestHandler):
    def get(self, user_id):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Show profile for user {}'.format(user_id))


app = webapp2.WSGIApplication([
    ('/user/([\d\w_]+)', UserHandler),
    ('/card/([\d\w_]+:\d+)', CardHandler),
    ('/featuredcards/([\d\w_]+:\d+)', FeaturedCardsHandler),
    ('/(.*)', IndexHandler),
    ], debug=True)
