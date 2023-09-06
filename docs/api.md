# ShoppingCart API Documentation

The `ShoppingCart` class provides a simple interface to manage a shopping cart.

## Methods

### `__init__()`
Initializes the shopping cart with an empty list of items and a database connection.

### `add_item(item: str, price: float) -> None`
Adds an item with its price to the shopping cart.

### `remove_item(item: str) -> None`
Removes an item from the shopping cart.

### `get_item(item_name: str) -> dict`
Retrieves details of a specific item from the shopping cart.

### `get_count() -> int`
Returns the total number of items in the shopping cart.

### `get_total_price() -> float`
Calculates the total price of all items in the shopping cart.
