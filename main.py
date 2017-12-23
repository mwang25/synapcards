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
import webapp2

from card_ajax import CardAjax
from card_handler import CardHandler
from featured_cards_handler import FeaturedCardsHandler
from index_handler import IndexHandler
from search_handler import SearchHandler
from signin_ajax import SigninAjax
from signin_handler import SigninHandler
from user_ajax import UserAjax
from user_handler import UserHandler


app = webapp2.WSGIApplication([
    ('/signinajax', SigninAjax),
    ('/signin', SigninHandler),
    ('/userajax', UserAjax),
    ('/user/([\d\w_]+)', UserHandler),
    ('/cardajax', CardAjax),
    ('/card/([\d\w_]+:\d+)', CardHandler),
    ('/featuredcards/([\d\w_]+:\d+)', FeaturedCardsHandler),
    ('/search', SearchHandler),
    ('/(.*)', IndexHandler),
    ], debug=True)
