from ajax_handler import AjaxHandler
from user import User
from user_manager import UserManager
from user_manager import UserManagerError
from user_id import BadUserIdError


class SigninAjax(AjaxHandler):
    def get(self):
        (firebase_id, email) = self.get_firebase_info()
        if firebase_id is not None:
            user_info = User.get(firebase_id=firebase_id)
            # If no record of this synapcard user, add new account
            if user_info is None:
                try:
                    user_info = UserManager.add(firebase_id, email)
                except (UserManagerError, BadUserIdError) as err:
                    user_info = {'error_message': err.message}
                except Exception as e:
                    msg = str(type(e)) + ':' + ''.join(e.args)
                    user_info = {'error_message': msg}

        self.write_response(user_info)
