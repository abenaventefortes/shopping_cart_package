import unittest
from unittest.mock import patch, MagicMock, create_autospec
from PyQt5.QtWidgets import QApplication, QLineEdit, QLabel, QPushButton, QVBoxLayout, QTextEdit
from shopping_cart.api import ShoppingCart
from shopping_cart.gui import ShoppingCartGUI


class TestShoppingCartGUI(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.patcher = patch('shopping_cart.gui.logging.Logger.info')
        self.mock_logger_info = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    @patch('shopping_cart.gui.QtLogHandler', autospec=True)
    @patch('shopping_cart.gui.logging.getLogger', autospec=True)
    def test_init(self, mock_get_logger, mock_qtloghandler):
        mock_qtextedit = create_autospec(QTextEdit)  # Using create_autospec
        cart = ShoppingCart()
        gui = ShoppingCartGUI(cart)

        self.assertIsInstance(gui, ShoppingCartGUI)
        mock_get_logger.assert_called_once()
        mock_get_logger().addHandler.assert_called_once_with(mock_qtloghandler.return_value)
        mock_get_logger().setLevel.assert_called_once()
        mock_qtloghandler.assert_called_once()

    @patch('shopping_cart.gui.QMessageBox.critical')
    def test_add_item_to_cart_invalid_price(self, mock_msgbox):
        cart = ShoppingCart()
        gui = ShoppingCartGUI(cart)

        gui.item_input = create_autospec(QLineEdit)  # Using autospec
        gui.price_input = create_autospec(QLineEdit)  # Using autospec

        gui.item_input.setText.return_value = "Apple"
        gui.price_input.setText.return_value = "invalid"

        gui.add_item_to_cart()
        mock_msgbox.assert_called_once()

    @patch('shopping_cart.gui.QtWidgets.QPushButton', autospec=True)
    @patch('shopping_cart.gui.QtWidgets.QLineEdit', autospec=True)
    @patch('shopping_cart.gui.QtWidgets.QLabel', autospec=True)
    @patch('shopping_cart.gui.QtWidgets.QVBoxLayout', autospec=True)
    @patch('shopping_cart.gui.CustomTableWidget', autospec=True)
    def test_init_ui(self, mock_table, mock_vbox, mock_label, mock_lineedit, mock_pushbutton):
        cart = ShoppingCart()
        gui = ShoppingCartGUI(cart)
        gui.init_ui()
        mock_pushbutton.assert_called()
        mock_lineedit.assert_called()
        mock_label.assert_called()
        mock_vbox.assert_called()
        mock_table.assert_called()

    @patch('shopping_cart.gui.CustomTableWidget', autospec=True)
    def test_refresh_table(self, mock_table):
        cart = ShoppingCart()
        gui = ShoppingCartGUI(cart)
        gui.cart = MagicMock()
        gui.cart.items = [{'id': 1, 'item': 'apple', 'price': 1.2}]
        gui.refresh_table()
        mock_table.blockSignals.assert_called()
        mock_table.setRowCount.assert_called()
        mock_table.insertRow.assert_called()
        mock_table.setItem.assert_called()
        mock_table.blockSignals.assert_called()


if __name__ == '__main__':
    unittest.main()
