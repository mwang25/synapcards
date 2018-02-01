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

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2


class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        # from looke like this: Michael Wang <mwang25@gmail.com>
        logging.info("inbound email from: " + mail_message.sender)
        # to looks like this: unsubscribe@fireproto-5c009.appspotmail.com
        logging.info("email to: " + mail_message.to)
        logging.info("subject line: " + mail_message.subject)
        plaintext_bodies = mail_message.bodies('text/plain')
        html_bodies = mail_message.bodies('text/html')
        i = 0
        for content_type, body in plaintext_bodies:
            plaintext = body.decode()
            logging.info("text body [%d]: %s", i, plaintext)
            i += 1
        i = 0
        for content_type, body in html_bodies:
            html = body.decode()
            logging.info("html body [%d]: %s", i, html)
            i += 1


app = webapp2.WSGIApplication([EmailHandler.mapping()], debug=True)
