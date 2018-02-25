import unittest

from update_frequency import UpdateFrequency


class TestUpdateFrequency(unittest.TestCase):

    def test_as_list(self):
        self.assertEqual(
            set(UpdateFrequency.as_list()), set(['never', 'daily', 'weekly']))

    def test_valid(self):
        self.assertTrue(UpdateFrequency.valid('never'))
        self.assertTrue(UpdateFrequency.valid('daily'))
        self.assertTrue(UpdateFrequency.valid('weekly'))

        # Enum name is case sensitive
        self.assertFalse(UpdateFrequency.valid('WEEKLY'))

        self.assertFalse(UpdateFrequency.valid('monthly'))

    def test_name(self):
        self.assertEqual(UpdateFrequency.NEVER.value, 'never')


if __name__ == '__main__':
    unittest.main()
