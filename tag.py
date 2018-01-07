from operator import attrgetter
import re


class TagError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class Tag:
    def __init__(self, name, count=0):
        Tag.validate(name)
        self.name = name
        self.count = count

    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.count)

    @classmethod
    def validate(cls, name):
        if not isinstance(name, unicode):
            raise TagError('tag name must be unicode')

        str = name.encode('utf-8')
        if ord(str[0]) < 0x80:
            m = re.match(r'([a-zA-Z0-9]).*', name)
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

    t1 = Tag(u'hi')
    print t1

    t2 = Tag(u'hi', 3)
    print t2

    try:
        t3 = Tag('hi', 5)
        print t3
    except TagError as err:
        print 'PASS: got expected error on ascii hi'
        print 'error message: ' + err.message

    l = [Tag(u'hi', 30), Tag(u'bye', 1), Tag(u'sam', 10)]
    print 'Sort list by name:'
    l.sort(key=attrgetter('name'))
    print u' '.join(unicode(t) for t in l)

    print 'Sort list by count:'
    l.sort(key=attrgetter('count'), reverse=True)
    print u' '.join(unicode(t) for t in l)


if __name__ == "__main__":
    run_tests()
