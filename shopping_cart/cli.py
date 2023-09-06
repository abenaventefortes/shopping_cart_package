"""
Provides a command-line interface for the shopping cart application.

The ShoppingCartCLI class parses command-line arguments and calls methods
on a ShoppingCart instance to perform actions like adding, removing, and
listing items.
"""

import os
import sys
import argparse
import logging
from PyQt5 import QtWidgets
from .api import ShoppingCart
from .gui import ShoppingCartGUI

# Set up logging
current_dir = os.path.dirname(__file__)
log_file_path = os.path.join(current_dir, 'logs', 'shopping_cart.log')
logging.basicConfig(level=logging.INFO, filename=log_file_path, format="%(asctime)s - %(levelname)s - %(message)s")


class ShoppingCartCLI:
    """
    A class to manage the shopping cart via a command-line interface (CLI).

    Attributes:
        cart (ShoppingCart): An instance of the ShoppingCart class.
        parser (argparse.ArgumentParser): Command-line argument parser.
    """

    def __init__(self):
        """
        Initialize the ShoppingCartCLI class.
        """
        self.cart = ShoppingCart()
        self.parser = self.setup_parser()

    @staticmethod
    def setup_parser():
        """
        Set up the command-line argument parser.

        Returns:
            argparse.ArgumentParser: The configured parser.
        """
        # Create a parser object
        parser = argparse.ArgumentParser(description="Shopping Cart CLI")

        # Define command-line arguments
        parser.add_argument("-a", "--add", nargs=2, metavar=('ITEM', 'PRICE'),
                            help="Add an item with its price to the cart. Example: -a 'Apple' 1.2")
        parser.add_argument("-r", "--remove", metavar='ITEM',
                            help="Remove an item from the cart. Example: -r 'Apple'")
        parser.add_argument("-l", "--list", action="store_true",
                            help="List all items in the cart. Example: -l")
        parser.add_argument("-u", "--update", nargs='+',
                            help="Update the name and/or price of an item in the cart. Examples: -u 'Apple' 'Orange' "
                                 "1.3 or -u 'Apple' 1.3 or -u 'Apple' 'Orange'")
        parser.add_argument("-t", "--total", action="store_true",
                            help="Display the total price of all items in the cart. Example: -t")
        parser.add_argument("-c", "--count", action="store_true",
                            help="Get the total number of items in the cart. Example: -c")
        parser.add_argument("-g", "--get", metavar='ITEM',
                            help="Retrieve details of a specific item from the cart. Example: -g 'Apple'")
        parser.add_argument("-f", "--refresh", action="store_true",
                            help="Refresh the internal list of items from the database. Example: -f")
        parser.add_argument("-e", "--export-list", metavar='FILENAME',
                            help="Export the shopping list to a file. Example: -e 'shopping_list.txt'")
        parser.add_argument("-xl", "--export-logs", metavar='FILENAME',
                            help="Export the logs to a file. Example: -xl 'logs.txt'")
        parser.add_argument("-xc", "--export-cart", metavar='FILENAME',
                            help="Export the shopping cart to a JSON file")

        return parser

    def main(self):
        """
        The main entry point for the CLI.
        """
        # Parse command-line arguments
        args = self.parser.parse_args()

        # If no arguments are provided, launch the GUI
        if not any(vars(args).values()):
            self.launch_gui()
        else:
            self.run(args)

    def launch_gui(self):
        """
        Launch the graphical user interface (GUI) for the shopping cart.
        """
        app = QtWidgets.QApplication(sys.argv)
        window = ShoppingCartGUI(cart=self.cart)  # Pass 'cart' as an argument
        window.show()
        sys.exit(app.exec_())

    def run(self, args):
        """
        Execute CLI commands based on parsed arguments.

        Args:
            args (argparse.Namespace): Parsed command-line arguments.
        """
        # Handle 'add' command
        if args.add:
            item, price = args.add
            try:
                self.cart.add_item(item, float(price))
                print(f"Added {item} with price {price} to the cart.")
            except ValueError:
                print(f"Error: Invalid price provided for {item}. Please provide a valid number.")

        # Handle 'remove' command
        if args.remove:
            try:
                self.cart.remove_item(args.remove)
                print(f"Removed {args.remove} from the cart.")
            except Exception as e:
                print(f"Error removing item: {e}")

        # Handle 'list' command
        if args.list:
            items = self.cart.items
            for item in items:
                print(f"{item['item']} - {item['price']:.2f} $")

        # Handle 'total' command
        if args.total:
            total_price = self.cart.get_total_price()
            print(f"Total price of all items: {total_price:.2f} $")

        # Handle 'count' command
        if args.count:
            count = self.cart.get_count()
            print(f"Total number of items in the cart: {count}")

        # Handle 'get' command
        if args.get:
            item_details = self.cart.get_item(args.get)
            if item_details:
                print(f"Item: {item_details['item']}, Price: {item_details['price']:.2f} $")
            else:
                print(f"Item {args.get} not found in the cart.")

        # Handle 'refresh' command
        if args.refresh:
            self.cart.refresh_items()
            print("Refreshed the internal list of items from the database.")

            # Handle 'update' command
            if args.update:
                # Validate the number of arguments for the 'update' command
                if len(args.update) < 2 or len(args.update) > 3:
                    print("Error: Invalid number of arguments for --update.")
                    return

                # Extract the old item name
                old_item = args.update[0]

                # Determine if a new item name is provided
                new_item = None if len(args.update) == 2 and args.update[1].replace('.', '', 1).isdigit() else \
                    args.update[1]

                # Determine if a new price is provided
                new_price = None if new_item else float(args.update[1])

                # If three arguments are provided, the last one is the new price
                if len(args.update) == 3:
                    new_price = float(args.update[2])

                # Update the item in the cart
                self.cart.update_item(old_item, new_item, new_price)
                print(
                    f"Updated item {old_item} to {new_item if new_item else old_item} with price {new_price if new_price else 'unchanged'} in the cart.")

                # Handle 'export_list' command
                if args.export_list:
                    self.cart.export_shopping_list(args.export_list)
                    print(f"Shopping list exported to {args.export_list}.")

                # Handle 'export_cart' command
                if args.export_cart:
                    self.cart.export_cart_to_json(args.export_cart)
                    print(f"Shopping cart exported to {args.export_cart}")

                # Handle 'export_logs' command
                if args.export_logs:
                    self.cart.export_logs(args.export_logs)
                    print(f"Logs exported to {args.export_logs}")


def main():
    """
    The main function to execute the ShoppingCartCLI.
    """
    # Create an instance of the ShoppingCartCLI class
    shopping_cart_cli = ShoppingCartCLI()

    # Run the main function of the ShoppingCartCLI instance
    shopping_cart_cli.main()


if __name__ == "__main__":
    # Execute the main function if the script is run as the main module
    main()
