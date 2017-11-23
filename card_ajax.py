from ajax_handler import AjaxHandler
from user import User
from card import CardError
from card_manager import CardManager
from card_manager import CardManagerError
from publish_datetime import PublishDatetimeError


class CardAjax(AjaxHandler):
    def post(self):
        (firebase_id, email) = self.get_firebase_info()
        if firebase_id:
            user_info = User.get(firebase_id=firebase_id)
            user_id = user_info['user_id']
            card_dict = {'signed_in_user_id': user_id}
            post_data = self.get_post_data()
            action = post_data['action']

            try:
                if action == 'get':
                    if post_data['card_num'] > 0:
                        card_dict.update(CardManager.get(post_data))
                elif action == 'save':
                    if post_data['card_num'] == '0':
                        card_dict.update(
                            CardManager.add(user_id, post_data))
                    else:
                        card_dict.update(
                            CardManager.update(user_id, post_data))
                elif action == 'delete':
                    CardManager.delete(user_id, post_data)
                else:
                    msg = 'invalid action ' + action
                    card_dict['error_message'] = msg
            except (CardError, CardManagerError, PublishDatetimeError) as err:
                card_dict['error_message'] = err.message
            except Exception as e:
                msg = str(type(e)) + ':' + ''.join(e.args)
                card_dict['error_message'] = msg

        self.write_response(card_dict)
