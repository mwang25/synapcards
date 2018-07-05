import calendar
import datetime
import re


class PublishDatetimeError(RuntimeError):
    def __init__(self, arg):
        self.message = arg


class PublishDatetime:
    SUPPORTED_FORMATS = ['%Y', '%B %Y', '%m/%d/%Y']
    CREATE_UPDATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, dt=None, output_format=None):
        self.datetime = dt
        self.output_format = output_format

    @classmethod
    def parse_string(cls, s):
        # As special case, if s is blank, leave object uninitialized
        if not s or len(s) == 0:
            return cls()

        # YYYY
        m = re.match(r'^([\d]{4})$', s)
        if m:
            return cls(
                datetime.datetime(year=int(m.group(1)), month=1, day=1),
                '%Y')

        # mm/YYYY
        m = re.match(r'^([\d]{1,2})/([\d]{4})$', s)
        if m:
            month = int(m.group(1))
            return cls(
                datetime.datetime(year=int(m.group(2)), month=month, day=1),
                '%B %Y')

        # Month YYYY
        m = re.match(r'^([\w]+)\s([\d]{4})$', s)
        if m:
            month = m.group(1)
            if month in calendar.month_name:
                return cls(
                    datetime.datetime(
                        year=int(m.group(2)),
                        month=list(calendar.month_name).index(month),
                        day=1),
                    '%B %Y')

        # mm/dd/YYYY
        m = re.match(r'^([\d]{1,2})/([\d]{1,2})/([\d]{4})$', s)
        if m:
            month = int(m.group(1))
            day = int(m.group(2))
            return cls(
                datetime.datetime(year=int(m.group(3)), month=month, day=day),
                '%m/%d/%Y')

        raise PublishDatetimeError('Bad date format')

    def __str__(self):
        if self.datetime and self.output_format:
            return self.datetime.strftime(self.output_format)
        else:
            return ''


def run_tests():
    try:
        p = PublishDatetime().parse_string('1999')
        print p.datetime
        print p.output_format
        print p

        p = PublishDatetime().parse_string('4/1999')
        print p.datetime
        print p.output_format
        print p

        p = PublishDatetime().parse_string('July 1999')
        print p.datetime
        print p.output_format
        print p

        p = PublishDatetime().parse_string('5/20/1999')
        print p.datetime
        print p.output_format
        print p

    except PublishDatetimeError as err:
        print err.message

    try:
        s = '99'
        print 'Now try bad string ' + s
        p = PublishDatetime().parse_string(s)
    except PublishDatetimeError as err:
        print err.message

    try:
        s = '333/1999'
        print 'Now try bad string ' + s
        p = PublishDatetime().parse_string(s)
    except PublishDatetimeError as err:
        print err.message

    try:
        s = 'blah 1999'
        print 'Now try bad string ' + s
        p = PublishDatetime().parse_string(s)
    except PublishDatetimeError as err:
        print err.message


if __name__ == "__main__":
    run_tests()
