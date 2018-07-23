from ajax_handler import AjaxHandler
from card import CardError
from card_manager import CardManager
from card_manager import CardManagerError
from like_manager import LikeManager
from user import User


class LikeAjax(AjaxHandler):
    def post(self):
        (firebase_id, email) = self.get_firebase_info()
        if firebase_id:
            user_dict = User.get(firebase_id=firebase_id)
            card_dict = {'signed_in_user_id': user_dict['user_id']}
            post_data = self.get_post_data()
            action = post_data['action']

            try:
                if action == 'like':
                    # Call CardManager first since it has better error checking
                    card_dict.update(CardManager.like(post_data))
                    LikeManager().like(post_data)
                elif action == 'unlike':
                    card_dict.update(CardManager.unlike(post_data))
                    LikeManager().unlike(post_data)
                else:
                    msg = 'invalid action ' + action
                    card_dict['error_message'] = msg
            except (
                    CardError,
                    CardManagerError,
                    ) as err:
                card_dict['error_message'] = err.message
            except Exception as e:
                msg = str(type(e)) + ':' + ''.join(e.args)
                card_dict['error_message'] = msg
        else:
            msg = 'authentication failed, please refresh page or sign in again'
            card_dict = {'error_message': msg}

        self.write_response(card_dict)
