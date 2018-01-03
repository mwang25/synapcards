import re


class TagError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class Tag:
    @classmethod
    def validate(cls, tag):
        if not isinstance(tag, unicode):
            raise TagError('tag must be unicode')

        str = tag.encode('utf-8')
        if ord(str[0]) < 0x80:
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
    tags = [u'happy', u'Happy', u'7 Habits', u'kai\u738b', u'\u738b\u732b']
    for t in tags:
        try:
            print 'validating tag:' + t
            Tag.validate(t)
            print 'PASS:' + t
        except TagError as err:
            print 'FAILED!!!! with ' + err.message

    tags = ['hi', u'_hi']
    for t in tags:
        try:
            print 'validating tag:' + t
            Tag.validate(t)
            print 'FAILED!  did not get exception on ' + t
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
