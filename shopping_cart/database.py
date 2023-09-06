"""
Provides a Database class to handle SQLite database operations for the
shopping cart application.

The Database class manages connecting to the database, creating tables,
performing CRUD operations on items, and updating the database schema.
"""

import os
import logging
import sqlite3

CURRENT_DIR = os.path.dirname(__file__)
log_file_path = os.path.join(CURRENT_DIR, 'logs', 'shopping_cart.log')

logging.basicConfig(level=logging.INFO, filename=log_file_path, format="%(asctime)s - %(levelname)s - %(message)s")


class Database:
    """
    Class to handle database operations for the shopping cart.

    Attributes:
        conn (sqlite3.Connection): A connection to the SQLite database.
    """

    def __init__(self):
        """
        Initialize the database connection and ensure the table exists.
        """
        database_file_path = os.path.join(CURRENT_DIR, 'data/shopping_cart.db')
        self.conn = sqlite3.connect(database_file_path)

        # Ensure the table for the cart exists
        self.create_table()

        # Ensure the database is up-to-date
        self.ensure_database_version()

        # Logging
        logging.info("Database connection initialized.")

    def create_table(self):
        """
        Create the table for the shopping cart if it doesn't exist.
        """
        with self.conn:
            # Execute the SQL command to create the table
            self.conn.execute("""
               CREATE TABLE IF NOT EXISTS cart (
               id INTEGER PRIMARY KEY, 
               item TEXT, 
               price REAL
               )
               """)

    def add_item(self, item, price):
        """
        Add an item with its price to the database.

        Args:
            item (str): The name of the item.
            price (float): The price of the item.

        Returns:
            int: The ID of the added item.
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""INSERT INTO cart (item, price) VALUES (?, ?)""", (item, price))
            item_id = cursor.lastrowid  # Get the ID of the newly added item
        logging.info(f"Item {item} with ID {item_id} and price {price} added to the database.")
        return item_id  # Return the ID

    def remove_item(self, item):
        """
        Remove an item from the database.

        Args:
            item (str): Name of the item to be removed.

        Returns:
            None
        """
        with self.conn:
            # Execute the SQL command to delete the item from the table
            self.conn.execute("""DELETE FROM cart WHERE item = ?""", (item,))
            # Logging
            logging.info(f"Item {item} removed from the database.")

    def ensure_database_version(self):
        """Ensure the database schema is up-to-date."""
        with self.conn:
            # Create a table for schema version if it doesn't exist
            self.conn.execute("""
               CREATE TABLE IF NOT EXISTS schema_version (
               version INTEGER
               )
               """)

            # Check the current schema version
            cursor = self.conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()

            # If there's no version, it's a new database
            if not result:
                current_version = 0
            else:
                current_version = result[0]

            # Update the schema if necessary
            self.update_schema(current_version)

    def update_schema(self, current_version):
        """Update the database schema based on the current version."""
        if current_version < 1:
            with self.conn:
                # Create a new table with the desired schema
                self.conn.execute("""
                   CREATE TABLE cart_new (
                   id INTEGER PRIMARY KEY,
                   item TEXT NOT NULL,
                   price REAL NOT NULL
                   )
                   """)

                # Copy data from the old table to the new table
                self.conn.execute("INSERT INTO cart_new(item, price) SELECT item, price FROM cart")

                # Drop the old table
                self.conn.execute("DROP TABLE cart")

                # Rename the new table to the old table's name
                self.conn.execute("ALTER TABLE cart_new RENAME TO cart")

                # Update the schema version
                self.conn.execute("INSERT INTO schema_version (version) VALUES (1)")

    def update_item(self, old_name, new_name=None, new_price=None):
        """Update item information in the database."""
        with self.conn:
            cursor = self.conn.cursor()
            if new_name and new_price:
                cursor.execute("UPDATE cart SET item = ?, price = ? WHERE item = ?", (new_name, new_price, old_name))
            elif new_name:
                cursor.execute("UPDATE cart SET item = ? WHERE item = ?", (new_name, old_name))
            elif new_price:
                cursor.execute("UPDATE cart SET price = ? WHERE item = ?", (new_price, old_name))
            self.conn.commit()  # Ensure changes are committed to the database
