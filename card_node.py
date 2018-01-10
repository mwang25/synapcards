import re

from card_attr import CardAttr


class CardNodeError(RuntimeError):
    def __init__(self, message, name, attr):
        self.message = message
        self.name = name
        self.attr = attr


class CardNode(object):
    """Base class for author, source, tags classes"""
    def __init__(self, attr, name, count):
        self.node_attr = attr
        self.name = name
        self.count = count
        self.validate()

    @classmethod
    def as_list(cls, names):
        """Given multiple names separated by commas, return as list"""
        if not names:
            return []
        split = [n.strip() for n in names.split(',')]
        return filter(lambda n: len(n) > 0, split)

    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.count)

    def validate(self):
        if not isinstance(self.name, unicode):
            raise CardNodeError('must be unicode', self.name, self.node_attr)

        # Convert name to byte sequence and reject if the first byte is an
        # ascii special character, such as _
        str = self.name.encode('utf-8')
        if ord(str[0]) < 0x80:
            m = re.match(r'([a-zA-Z0-9]).*', self.name)
            if not m:
                raise CardNodeError(
                    'illegal first character', self.name, self.node_attr)


def run_tests():
    a = CardNode(CardAttr.AUTHOR, u'mike', 1)
    print a.__unicode__()

    try:
        b = CardNode(CardAttr.AUTHOR, u'_mike', 2)
        print b
    except CardNodeError as err:
        print 'PASS: got expected error'
        print '  message: ' + err.message
        print '  name: ' + err.name
        print '  attr: {}'.format(err.attr)

    try:
        c = CardNode(CardAttr.AUTHOR, 'mike', 3)
        print c
    except CardNodeError as err:
        print 'PASS: got expected error'
        print '  message: ' + err.message
        print '  name: ' + err.name
        print '  attr: {}'.format(err.attr)

    l = CardNode.as_list(None)
    print l

    l = CardNode.as_list('')
    print l

    l = CardNode.as_list('mike, jane, ')
    print l


if __name__ == "__main__":
    run_tests()
