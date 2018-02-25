from enum import Enum


class UpdateFrequency(Enum):
    NEVER = 'never'
    WEEKLY = 'weekly'
    DAILY = 'daily'

    @staticmethod
    def as_list():
        # Return values in a particular order to make UI look nicer
        # return [e.value for e in UpdateFrequency]
        return ['never', 'weekly', 'daily']

    @staticmethod
    def valid(e):
        return e in UpdateFrequency.as_list()
