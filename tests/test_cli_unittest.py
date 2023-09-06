import unittest
from unittest.mock import patch
from shopping_cart.cli import ShoppingCartCLI


class ShoppingCartCLITest(unittest.TestCase):
    def setUp(self):
        self.shopping_cart_cli = ShoppingCartCLI()

    @patch("shopping_cart.ShoppingCart")
    def test_launch_gui(self, mock_shopping_cart):
        self.shopping_cart_cli.launch_gui()
        mock_shopping_cart.assert_called_once()

    @patch("argparse.ArgumentParser.parse_args")
    def test_main_launch_gui(self, mock_parse_args):
        mock_parse_args.return_value = None
        with patch("sys.exit") as mock_sys_exit:
            self.shopping_cart_cli.main()
            mock_sys_exit.assert_called_once_with(0)

    @patch("argparse.ArgumentParser.parse_args")
    def test_main_run(self, mock_parse_args):
        mock_parse_args.return_value = "dummy_args"
        with patch("sys.exit") as mock_sys_exit:
            with patch("shopping_cart.ShoppingCartCLI.run") as mock_run:
                self.shopping_cart_cli.main()
                mock_run.assert_called_once_with("dummy_args")
                mock_sys_exit.assert_called_once_with(0)

    @patch("builtins.print")
    @patch("shopping_cart.ShoppingCart.add_item")
    def test_run_add_item(self, mock_add_item, mock_print):
        args = argparse.Namespace(add=["Apple", "1.99"])
        self.shopping_cart_cli.run(args)
        mock_add_item.assert_called_once_with("Apple", 1.99)
        mock_print.assert_called_once_with("Added Apple with price 1.99 to the cart.")

    @patch("builtins.print")
    @patch("shopping_cart.ShoppingCart.remove_item")
    def test_run_remove_item(self, mock_remove_item, mock_print):
        args = argparse.Namespace(remove="Apple")
        self.shopping_cart_cli.run(args)
        mock_remove_item.assert_called_once_with("Apple")
        mock_print.assert_called_once_with("Removed Apple from the cart.")

    @patch("builtins.print")
    @patch("shopping_cart.ShoppingCart.items", [{"item": "Apple", "price": 1.99}])
    def test_run_list_items(self, mock_print):
        args = argparse.Namespace(list=True)
        self.shopping_cart_cli.run(args)
        mock_print.assert_called_once_with("Apple - 1.99 $")

    @patch("builtins.print")
    @patch("shopping_cart.ShoppingCart.get_total_price")
    def test_run_total_price(self, mock_get_total_price, mock_print):
        mock_get_total_price.return_value = 10.99
        args = argparse.Namespace(total=True)
        self.shopping_cart_cli.run(args)
        mock_get_total_price.assert_called_once()
        mock_print.assert_called_once_with("Total price of all items: 10.99 $")

    @patch("builtins.print")
    @patch("shopping_cart.ShoppingCart.get_count")
    def test_run_count_items(self, mock_get_count, mock_print):
        mock_get_count.return_value = 5
        args = argparse.Namespace(count=True)
        self.shopping_cart_cli.run(args)
        mock_get_count.assert_called_once()
        mock_print.assert_called_once_with("Total number of items in the cart: 5")

    @patch("builtins.print")
    @patch("shopping_cart.ShoppingCart.get_item")
    def test_run_get_item(self, mock_get_item, mock_print):
        mock_get_item.return_value = {"item": "Apple", "price": 1.99}
        args = argparse.Namespace(get="Apple")
        self.shopping_cart_cli.run(args)
        mock_get_item.assert_called_once_with("Apple")
        mock_print.assert_called_once_with("Item: Apple, Price: 1.99 $")

    @patch("shopping_cart.ShoppingCart.refresh_items")
    @patch("builtins.print")
    def test_run_refresh_items(self, mock_print, mock_refresh_items):
        args = argparse.Namespace(refresh=True)
        self.shopping_cart_cli.run(args)
        mock_refresh_items.assert_called_once()
        mock_print.assert_called_once_with("Refreshed the internal list of items from the database.")


if __name__ == "__main__":
    unittest.main()
