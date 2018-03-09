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
import re

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2

from conf_manager import ConfManager
from update_frequency import UpdateFrequency
from user_manager import UserManager


class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        # from looke like this: Michael Wang <mwang25@gmail.com>
        logging.info("inbound email from: " + mail_message.sender)
        email = self._extract_email(mail_message.sender)
        if not email:
            return
        logging.info("extracted email=" + email)

        # to looks like this: unsubscribe@fireproto-5c009.appspotmail.com
        logging.info("email to: " + mail_message.to)
        to = self._extract_to(mail_message.to)
        if not to:
            return
        logging.info("extracted to=" + to)

        if to == 'unsubscribe':
            UserManager().update_email_freq(email, UpdateFrequency.NEVER.value)
        elif to == 'confirm':
            ConfManager().process_email(email)
        else:
            logging.info("unsupported to=" + to)

    def _extract_email(self, full_email):
        m = re.match(r'.*<([\w\d\._]+@.+)>', full_email)
        if m:
            return m.group(1)

        logging.info("could not extract email from " + full_email)
        return None

    def _extract_to(self, full_to):
        m = re.match(r'([\w]+)@.+', full_to)
        if m:
            return m.group(1)

        logging.info("could not extract to from " + full_to)
        return None


app = webapp2.WSGIApplication([EmailHandler.mapping()], debug=True)
