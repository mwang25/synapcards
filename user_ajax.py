from ajax_handler import AjaxHandler
from user import User
from user_manager import UserManager
from user_manager import UserManagerError
from user_id import BadUserIdError


class UserAjax(AjaxHandler):
    def post(self):
        (firebase_id, email) = self.get_firebase_info()
        if firebase_id:
            user_info = User.get(firebase_id=firebase_id)
            user_id = user_info['user_id']
            post_data = self.get_post_data()
            action = post_data['action']

            try:
                if action == 'edit':
                    if user_id == post_data['user_id']:
                        user_info = UserManager().update(user_id, post_data)
                    else:
                        user_info = UserManager().change_user_id(
                            user_id, post_data)

                elif action == 'delete':
                    user_info = UserManager().delete(user_id)
                elif action == 'follow':
                    user_info = UserManager().follow(
                        user_id, post_data['user_id'])
                elif action == 'unfollow':
                    user_info = UserManager().unfollow(
                        user_id, post_data['user_id'])
                elif action == 'force_send_conf':
                    user_info = UserManager().force_send_conf(user_id)
                else:
                    msg = 'invalid action ' + action
                    user_info = {'error_message': msg}
            except (UserManagerError, BadUserIdError) as err:
                user_info = {'error_message': err.message}
            except Exception as e:
                msg = str(type(e)) + ':' + ''.join(e.args)
                user_info = {'error_message': msg}

        self.write_response(user_info)
