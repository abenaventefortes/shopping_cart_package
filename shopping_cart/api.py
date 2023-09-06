"""
Class representing a shopping cart.
"""

import logging
import json
import os

from .database import Database


class ShoppingCart:
    """
    Class representing a shopping cart.

    Attributes:
        db (Database): A connection to the SQLite database.
        items (list): A list of dictionaries, each representing an item in the cart.
    """

    def __init__(self):
        """
        Initialize the shopping cart with an empty list of items and a database connection.
        """
        self.log_console = None
        self.db = Database()
        self.items = self.get_all_items()

        current_dir = os.path.dirname(__file__)
        log_file_path = os.path.join(current_dir, 'logs', 'shopping_cart.log')

        logging.basicConfig(level=logging.INFO, filename=log_file_path,
                            format="%(asctime)s - %(levelname)s - %(message)s")

        logging.info("Shopping cart initialized.")

    def get_all_items(self):
        """Retrieve all items from the database."""
        with self.db.conn:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT id, item, price FROM cart")
            return [{"id": row[0], "item": row[1], "price": row[2]} for row in cursor.fetchall()]

    def add_item(self, item, price):
        """
        Add an item with its price to the shopping cart.

        Args:
            item (str): The name of the item.
            price (float): The price of the item.

        Returns:
            int: The ID of the added item.

        Raises:
            ValueError: If the input types for item or price are invalid.
        """
        # Validate the input
        if not isinstance(item, str) or not isinstance(price, (int, float)):
            raise ValueError("Invalid input types for item or price.")

        # Create a dictionary representing the item and its price
        item_data = {"item": item, "price": price}
        # Append the item to the items list
        self.items.append(item_data)
        # Add the item to the database and get its ID
        item_id = self.db.add_item(item, price)
        item_data["id"] = item_id
        # Logger
        logging.info(f"Item {item} with ID {item_id} and price {float(price):.2f} $ added to the cart.")

        return item_id

    def remove_item(self, item):
        """
        Remove an item from the shopping cart.

        Args:
            item (str): Name of the item to be removed.

        Returns:
            None
        """
        # Iterate through the items and remove the specified item
        for i in self.items:
            if i["item"] == item:
                self.items.remove(i)
                logging.info(f"Item {item} removed from the cart.")
                break
        # Remove the item from the database
        self.db.remove_item(item)

    def get_item(self, item_name):
        """
        Retrieve details of a specific item from the shopping cart.

        Args:
            item_name (str): Name of the item to retrieve.

        Returns:
            dict: Dictionary containing item details, or None if not found.
        """
        # Iterate through the items to find the specified item
        for i in self.items:
            if i["item"] == item_name:
                return i
        return None

    def get_count(self):
        """
        Get the total number of items in the shopping cart.

        Returns:
            int: Total number of items in the cart.
        """
        return len(self.items)

    def get_total_price(self):
        """
        Calculate the total price of all items in the shopping cart.

        Returns:
            float: Total price of all items.
        """
        # Use the sum function with a generator expression to calculate the total price
        return sum(i["price"] for i in self.items)

    def update_item(self, old_name, new_name=None, new_price=None):
        if new_name is None and new_price is None:
            logging.warning("No updates provided.")
            return

        # Update the internal list of items
        for item in self.items:
            if item["item"] == old_name:
                if new_name is not None:
                    item["item"] = new_name
                if new_price is not None:
                    item["price"] = new_price
                break

        # Update the database
        result = self.db.update_item(old_name, new_name, new_price)
        logging.info(
            f"Updated item {old_name} to {new_name if new_name else old_name} with price {new_price if new_price else 'unchanged'} in the cart API.")
        return result

    def refresh_items(self):
        """Refresh the internal list of items from the database."""
        self.items = self.get_all_items()

    def export_shopping_list(self, filename):
        """Export the shopping list to a file."""
        with open(filename, 'w') as file:
            for item in self.items:
                file.write(f"{item['item']}, {item['price']}\n")
        logging.info(f"Shopping list exported to {filename}.")

    def export_cart_to_json(self, filename: str):
        """
        Export the shopping cart to a JSON file.

        Args:
            filename (str): The name of the JSON file to export to.

        Raises:
            FileNotFoundError: If the file cannot be opened for writing.
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.items, f)
            logging.info(f"Shopping cart exported to {filename}")
        except FileNotFoundError:
            logging.error(f"Failed to export shopping cart to {filename}. File not found.")

    def export_logs(self, filename):
        """
        Export the logs to a file.

        Args:
            filename (str): The name of the file to export the logs to.

        Returns:
            None
        """
        try:
            with open(filename, 'w') as file:
                log_messages = self.get_log_messages()
                file.write('\n'.join(log_messages))
            logging.info(f"Logs exported to {filename}.")
        except Exception as e:
            logging.error(f"Error exporting logs to {filename}: {e}")

    def get_log_messages(self):
        """
        Get the log messages from the log console.

        Returns:
            list: List of log messages.
        """
        log_messages = self.log_console.toPlainText().split('\n')
        return log_messages
