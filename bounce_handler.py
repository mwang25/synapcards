# Copyright 2016 Google Inc. All rights reserved.
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
import logging

from google.appengine.ext.webapp.mail_handlers import BounceNotificationHandler
import webapp2

from email_status import EmailStatus
from user_manager import UserManager


class BounceHandler(BounceNotificationHandler):
    def receive(self, bounce_message):
        # logging.info('Received bounce post ... [%s]', self.request)
        # logging.info('Bounce original: %s', bounce_message.original)
        logging.info('Bounce from: %s', bounce_message.original['from'])
        # bad dest address is in the to field, looks like mwangxyz@gmail.com
        logging.info('Bounce to: %s', bounce_message.original['to'])
        # logging.info('Bounce notification: %s', bounce_message.notification)
        UserManager().update_email_freq_status(
            bounce_message.original['to'], status=EmailStatus.BOUNCED.name)


app = webapp2.WSGIApplication([BounceHandler.mapping()], debug=True)
