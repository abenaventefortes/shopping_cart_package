# Database Class

The  `Database`  class is responsible for handling database operations for the shopping cart.

## Attributes

-  `conn (sqlite3.Connection)` : A connection to the SQLite database.

## Methods

###  `__init__()` 

Initialize the database connection and ensure the table exists.

- Parameters: None
- Returns: None

###  `create_table()` 

Create the table for the shopping cart if it doesn't exist.

- Parameters: None
- Returns: None

###  `add_item(item, price)` 

Add an item with its price to the database.

- Parameters:
  -  `item (str)` : The name of the item.
  -  `price (float)` : The price of the item.
- Returns:
  -  `int` : The ID of the added item.

###  `remove_item(item)` 

Remove an item from the database.

- Parameters:
  -  `item (str)` : Name of the item to be removed.
- Returns: None

###  `ensure_database_version()` 

Ensure the database schema is up-to-date.

- Parameters: None
- Returns: None

###  `update_schema(current_version)` 

Update the database schema based on the current version.

- Parameters:
  -  `current_version (int)` : The current version of the database schema.
- Returns: None

###  `update_item(old_name, new_name=None, new_price=None)` 

Update item information in the database.

- Parameters:
  -  `old_name (str)` : The current name of the item.
  -  `new_name (str, optional)` : The new name of the item (default: None).
  -  `new_price (float, optional)` : The new price of the item (default: None).
- Returns: None
