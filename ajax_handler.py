import json
import webapp2

import google.auth.transport.requests
import google.oauth2.id_token
import requests_toolbelt.adapters.appengine

requests_toolbelt.adapters.appengine.monkeypatch()
HTTP_REQUEST = google.auth.transport.requests.Request()


class AjaxHandler(webapp2.RequestHandler):
    def _write_cors_headers(self):
        """Write headers needed required by ajax preflight requests"""
        self.response.headers.add_header('Access-Control-Allow-Origin', '*')
        self.response.headers.add_header(
            'Access-Control-Allow-Headers', 'Authorization')
        self.response.headers.add_header(
            'Access-Control-Allow-Methods', 'POST, GET, PUT')

    def options(self):
        self._write_cors_headers()

    def get_firebase_info(self):
        if 'Authorization' in self.request.headers:
            id_token = self.request.headers['Authorization'].split(' ').pop()
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, HTTP_REQUEST)
            if claims:
                return claims['sub'], claims['email']

        return None, None

    def get_post_data(self):
        return json.loads(self.request.body)

    def write_response(self, user_info):
        obj = {}
        if user_info is not None:
            obj.update(user_info)
            if 'user_id' in user_info:
                obj['signed_in_user_id'] = user_info['user_id']

        self.response.content_type = 'application/json'
        self._write_cors_headers()
        self.response.write(json.dumps(obj))
