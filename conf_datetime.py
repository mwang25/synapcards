import datetime

from constants import Constants


class ConfDatetime:
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, dt):
        self.conf_sent_dt = dt
        timeout = datetime.timedelta(minutes=Constants.CONF_EMAIL_TIMEOUT)
        self.conf_expired_dt = dt + timeout

    @classmethod
    def from_string(cls, conf_sent):
        return cls(
            datetime.datetime.strptime(conf_sent, cls.DATE_TIME_FORMAT))

    def expired(self):
        return datetime.datetime.utcnow() > self.conf_expired_dt

    def __str__(self):
            return self.conf_sent_dt.strftime(self.DATE_TIME_FORMAT)


def run_tests():
    cdt = ConfDatetime.from_string('2017-03-20 06:00:01')
    print cdt.expired()
    print str(cdt)

    cdt = ConfDatetime(datetime.datetime.utcnow())
    print cdt.expired()
    print str(cdt)


if __name__ == "__main__":
    run_tests()
