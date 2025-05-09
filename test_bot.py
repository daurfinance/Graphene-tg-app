import unittest
from bot import get_or_create_user

class TestBot(unittest.TestCase):
    def test_get_or_create_user(self):
        user = get_or_create_user("123456")
        self.assertEqual(user.telegram_id, "123456")
        self.assertEqual(user.balance, 0)

if __name__ == "__main__":
    unittest.main()
