import unittest
from unittest.mock import patch, MagicMock
from shopping_cart.database import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchone.return_value = (1,)
        self.mock_conn.cursor.return_value = self.mock_cursor
        with patch('shopping_cart.database.sqlite3.connect', return_value=self.mock_conn):
            self.db = Database()
        self.mock_cursor.execute.reset_mock()  # Reset the mock after Database initialization

    def test_create_table(self):
        self.db.create_table()
        self.mock_conn.execute.assert_called()

    def test_ensure_database_version(self):
        self.db.ensure_database_version()
        self.mock_cursor.execute.assert_called_with("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")

    @patch('shopping_cart.database.sqlite3.connect')
    def test_add_item(self, mock_connect):
        mock_connect.return_value = self.mock_conn
        self.db.add_item("apple", 1.2)
        self.mock_cursor.execute.assert_called_with("INSERT INTO cart (item, price) VALUES (?, ?)", ("apple", 1.2))

    @patch('shopping_cart.database.sqlite3.connect')
    def test_remove_item(self, mock_connect):
        mock_connect.return_value = self.mock_conn  # Use the mock_conn created in setUp
        print("Before remove_item")  # Debugging print
        self.db.remove_item("Apple")
        print("After remove_item")  # Debugging print
        self.mock_conn.execute.assert_called_with("DELETE FROM cart WHERE item = ?", ("Apple",))  # Changed this line

    @patch('shopping_cart.database.sqlite3.connect')
    def test_update_item(self, mock_connect):
        mock_connect.return_value = self.mock_conn
        self.db.update_item("Apple", "Orange", 2.0)
        self.mock_cursor.execute.assert_called_with("UPDATE cart SET item = ?, price = ? WHERE item = ?",
                                                    ("Orange", 2.0, "Apple"))


if __name__ == '__main__':
    unittest.main()