import random
import re

from user import User


class BadUserIdError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class UserId:
    MIN_CHARACTERS = 3
    MAX_CHARACTERS = 16
    RANDOM_DIGITS = 6
    MAX_TRIES = 20

    @classmethod
    def validate(cls, user_id):
        print 'user_id is ' + user_id
        if (len(user_id) < cls.MIN_CHARACTERS):
            raise BadUserIdError(
                'must be at least {} characters'.format(cls.MIN_CHARACTERS))

        if (len(user_id) > cls.MAX_CHARACTERS):
            raise BadUserIdError(
                'can be at most {} characters'.format(cls.MAX_CHARACTERS))

        m = re.match(r'([a-z])([a-z\d\._]+)([a-z\d])', user_id)
        if m is not None:
            print 'Group0:' + m.group(0)
            print 'Group1:' + m.group(1)
            print 'Group2:' + m.group(2)
            print 'Group3:' + m.group(3)
        if m is None or m.group(0) != user_id:
            raise BadUserIdError('illegal character')

        # TODO: check for duplicate

    @classmethod
    def generate_id(cls, email):
        """convert email address to valid user id"""
        m = re.match(r'([\w\d\._]+)', email)
        # Lower case everything and make sure it does not exceed length
        user_id = m.group(1).lower()[0:cls.MAX_CHARACTERS]

        loop_count = 0
        orig_user_id = user_id
        while len(user_id) < UserId.MIN_CHARACTERS or User.exists(user_id):
            user_id = UserId.generate_random_id(orig_user_id)
            loop_count += 1
            if loop_count > cls.MAX_TRIES:
                raise BadUserIdError(
                    'Could not generate a valid synapcard user id')
        return user_id

    @classmethod
    def generate_random_id(cls, user_id):
        """append some random digits to the user_id"""
        r = random.randint(1, 10 ** cls.RANDOM_DIGITS - 1)
        return user_id[0:cls.MAX_CHARACTERS - cls.RANDOM_DIGITS] + str(r)


def run_tests():
    try:
        user_id = 'wjc'
        UserId.validate(user_id)
        print 'ok:' + user_id

        user_id = 'xyz.1683_b_c.def'
        UserId.validate(user_id)
        print 'ok:' + user_id
    except BadUserIdError as err:
        print err.message

    try:
        user_id = 'ki'
        UserId.validate(user_id)
        print 'FAIL!  expected exception' + user_id
    except BadUserIdError as err:
        print err.message

    try:
        user_id = '123alpha'
        UserId.validate(user_id)
        print 'FAIL!  expected exception' + user_id
    except BadUserIdError as err:
        print err.message

    try:
        user_id = 'alphA'
        UserId.validate(user_id)
        print 'FAIL!  expected exception' + user_id
    except BadUserIdError as err:
        print err.message

    try:
        user_id = 'beta7.'
        UserId.validate(user_id)
        print 'FAIL!  expected exception' + user_id
    except BadUserIdError as err:
        print err.message

    try:
        user_id = 'miDDle'
        UserId.validate(user_id)
        print 'FAIL!  expected exception' + user_id
    except BadUserIdError as err:
        print err.message

    try:
        email = 'mwang@gmail.com'
        user_id = UserId.generate_id(email)
        print 'FAIL!  got' + user_id if user_id != 'mwang' else 'ok'
    except BadUserIdError as err:
        print err.message

    try:
        email = 'jack.63_blahabc@gmail.com'
        user_id = UserId.generate_id(email)
        print 'FAIL!  got' + user_id if user_id != 'jack.63_blahabc' else 'ok'
    except BadUserIdError as err:
        print err.message

    print 'random id: ' + UserId.generate_random_id('abc')
    print 'random id: ' + UserId.generate_random_id('xyz')


if __name__ == "__main__":
    run_tests()
