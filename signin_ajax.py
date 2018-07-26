import logging

from ajax_handler import AjaxHandler
from user_manager import UserManager
from user_manager import UserManagerError
from user_id import BadUserIdError


class SigninAjax(AjaxHandler):
    def get(self):
        (firebase_id, email) = self.get_firebase_info()
        if firebase_id:
            try:
                user_id = UserManager().get_with_add_option(firebase_id, email)
                user_info = UserManager().get(user_id)
            except (UserManagerError, BadUserIdError) as err:
                user_info = {'error_message': err.message}
            except Exception as e:
                msg = str(type(e)) + ':' + ''.join(e.args)
                user_info = {'error_message': msg}
        else:
            logging.error("could not find firebase_id")
            user_info = {'error_message': 'internal error: no firebase_id'}

        self.write_response(user_info)
