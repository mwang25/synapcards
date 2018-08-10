from operator import attrgetter

from card_attr import CardAttr
from card_node import CardNode
from card_node import CardNodeError
from constants import Constants


class TagNode(CardNode):
    def __init__(self, name, count):
        super(TagNode, self).__init__(CardAttr.TAG, name, count)

    def search_link(self):
        return u'<a href="{}/search?tags={}&count=100">{}</a> ({})'.format(
            Constants.HOMEPAGE, self.name, self.name, self.count)


def run_tests():
    tags = [u'happy', u'Happy', u'7 Habits', u'kai\u738b', u'\u738b\u732b']
    for t in tags:
        try:
            print 'validating tag:' + t
            TagNode(t, 1)
            print 'PASS:' + t
        except CardNodeError as err:
            print 'FAILED!!!! with ' + err.message

    tags = ['hi', u'_hi']
    for t in tags:
        try:
            print 'validating tag:' + t
            TagNode(t, 1)
            print 'FAILED!  did not get exception on ' + t
        except CardNodeError as err:
            print 'PASS: got expected error on ' + t
            print '  error message: ' + err.message

    tlist = TagNode.as_list(None)
    if tlist == []:
        print 'PASS (on None)'
    else:
        print 'FAILED!!! None'

    tlist = TagNode.as_list('')
    if tlist == []:
        print 'PASS (on empty string)'
    else:
        print 'FAILED!!! empty string'

    tlist = TagNode.as_list('jack')
    if tlist == ['jack']:
        print 'PASS: {}'.format(tlist)
    else:
        print 'FAILED!!! list'

    tlist = TagNode.as_list('jack,  jill , sam,')
    if tlist == ['jack', 'jill', 'sam']:
        print 'PASS: {}'.format(tlist)
    else:
        print 'FAILED!!! list'

    t1 = TagNode(u'hi', 1)
    print unicode(t1)

    t2 = TagNode(u'hi', 3)
    print unicode(t2)

    try:
        t3 = TagNode('hi', 5)
        print t3
    except CardNodeError as err:
        print 'PASS: got expected error on ascii hi'
        print '  error message: ' + err.message

    l = [TagNode(u'hi', 30), TagNode(u'bye', 1), TagNode(u'sam', 10)]
    print 'Sort list by name:'
    l.sort(key=attrgetter('name'))
    print u' '.join(unicode(t) for t in l)

    print 'Sort list by count:'
    l.sort(key=attrgetter('count'), reverse=True)
    print u' '.join(unicode(t) for t in l)


if __name__ == "__main__":
    run_tests()
