import re


class TagError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class Tag:
    @classmethod
    def validate(cls, tag):
        m = re.match(r'([a-zA-Z0-9]).*', tag)
        if not m:
            raise TagError('illegal first character in tag')

    @classmethod
    def as_list(cls, tags):
        """Given multiple tags separated by commas, return as list"""
        if not tags:
            return []
        split = [t.strip() for t in tags.split(',')]
        return filter(lambda t: len(t) > 0, split)


def run_tests():
    try:
        tags = ['happy', 'Happy', '7 Habits of Happy', u'kai\u738b']
        for t in tags:
            print 'validating tag:' + t
            Tag.validate(t)
            print 'PASS:' + t
    except TagError as err:
        print 'FAILED!!!! with ' + err.message

    try:
        tags = [u'\u738bkai']
        for t in tags:
            print 'validating tag:' + t
            Tag.validate(t)
            print 'FAILED!  unexpected exception ' + t
    except TagError as err:
        print 'PASS: got expected error on ' + t
        print 'error message: ' + err.message

    tlist = Tag.as_list(None)
    if tlist == []:
        print 'PASS (on None)'
    else:
        print 'FAILED!!! None'

    tlist = Tag.as_list('')
    if tlist == []:
        print 'PASS (on empty string)'
    else:
        print 'FAILED!!! empty string'

    tlist = Tag.as_list('jack')
    if tlist == ['jack']:
        print 'PASS: {}'.format(tlist)
    else:
        print 'FAILED!!! list'

    tlist = Tag.as_list('jack,  jill , sam,')
    if tlist == ['jack', 'jill', 'sam']:
        print 'PASS: {}'.format(tlist)
    else:
        print 'FAILED!!! list'


if __name__ == "__main__":
    run_tests()
