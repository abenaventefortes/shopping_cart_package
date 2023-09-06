"""
Provides a PyQt5 graphical user interface for the shopping cart application.

The main ShoppingCartGUI class creates the application window, widgets,
and layout. It connects signals from widgets to slots that perform actions
like adding items and exporting data.

CustomTableWidget provides a QTableWidget with a context menu to remove items.

QtLogHandler is a custom log handler that directs log messages to a QTextEdit.
"""

import os
import sys
import logging

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox

from shopping_cart.api import ShoppingCart

current_dir = os.path.dirname(__file__)
log_file_path = os.path.join(current_dir, 'logs', 'shopping_cart.log')

logging.basicConfig(level=logging.INFO, filename=log_file_path, format="%(asctime)s - %(levelname)s - %(message)s")

# Gui UI Dark Mode Style
DARK_STYLE = """
    QWidget {
        background-color: #2E2E2E;
        color: #F2F2F2;
    }
    QPushButton {
        background-color: #555555;
        border: none;
        padding: 5px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #666666;
    }
    QPushButton:pressed {
        background-color: #777777;
    }
    QTableWidget {
        gridline-color: #1E1E1E;
    }
    QHeaderView::section {
        background-color: #3C3C3C;
        padding: 5px;
        border: 1px solid #6c6c6c;
    }
    QLineEdit {
        background-color: #3C3C3C;
        padding: 5px;
        border: 1px solid #6c6c6c;
        border-radius: 3px;
    }
    QErrorMessage {
        background-color: #2E2E2E;
    }
"""


class ShoppingCartGUI(QtWidgets.QWidget):
    """
    Main GUI class for the ShoppingCart application.

    Provides the user interface for the shopping cart application, allowing
    users to add items with their prices, view the total price, and see a log
    of actions performed.
    """

    def __init__(self, cart=None):
        """
        Initialize the GUI components and the ShoppingCart API.

        Sets up the GUI layout, initializes the shopping cart API, and configures
        the logging handler to display logs in the GUI.
        """
        super().__init__()

        # Apply the dark theme to the GUI
        self.total_label = QtWidgets.QLabel("Total Cost:")
        qt = QtWidgets.QApplication.instance()
        qt.setStyleSheet(DARK_STYLE)

        # Initialize the shopping cart API
        self.cart = cart if cart else ShoppingCart()

        # Set up the GUI layout and components
        self.init_ui()

        # Editing mode set to false by default when initializing class
        self.toggle_edit_mode(False)

        # Configure the logging handler to display logs in the GUI
        self.configure_logging_handler()
        log_handler = QtLogHandler(self.log_console)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)

        # Load items from the database into the table
        self.refresh_table()

    def init_ui(self):
        """
        Set up the GUI layout and components.

        Creates and configures all the widgets used in the GUI, such as labels,
        buttons, input fields, and the table. Also sets up the layout and connects
        widget signals to their respective slots.
        """
        # Create a vertical layout for the main window
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create and configure the title label
        self.title_label = QtWidgets.QLabel("Shopping Cart")
        self.layout.addWidget(self.title_label)

        # Create and configure the table to display items in the cart
        self.table = CustomTableWidget(self.cart, self)
        self.table.setColumnCount(2)  # Two columns: Item and Price
        self.table.setHorizontalHeaderLabels(["Item", "Price"])
        self.layout.addWidget(self.table)

        # Create a horizontal layout for displaying the total cost
        self.total_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.total_layout)

        # Create a horizontal layout for adding new items
        self.add_layout = QtWidgets.QHBoxLayout()

        # Adjust the table column width
        self.table.horizontalHeader().setStretchLastSection(True)

        # Create and configure labels and fields for item name
        self.item_label = QtWidgets.QLabel("Item Name:")
        self.add_layout.addWidget(self.item_label)
        self.item_input = QtWidgets.QLineEdit(self)
        self.add_layout.addWidget(self.item_input)

        # Create and configure labels and fields for item price
        self.price_label = QtWidgets.QLabel("Price:")
        self.add_layout.addWidget(self.price_label)
        self.price_input = QtWidgets.QLineEdit(self)
        self.add_layout.addWidget(self.price_input)

        # Create and configure the button to add items to the cart
        self.add_button = QtWidgets.QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_item_to_cart)
        self.add_layout.addWidget(self.add_button)

        # Add the horizontal layout to the main layout
        self.layout.addLayout(self.add_layout)

        # Toggled ID column
        self.table.setColumnCount(3)  # Three columns: ID, Item, and Price
        self.table.setHorizontalHeaderLabels(["ID", "Item", "Price"])
        self.table.setColumnHidden(0, True)  # Hide the ID column by default

        # Create and configure the label for the total cost
        self.total_layout.addWidget(self.total_label)

        # Create and configure the display for the total cost
        self.total_display = QtWidgets.QLabel("0.00 $")
        self.total_layout.addWidget(self.total_display)

        self.table.itemChanged.connect(self.handle_item_changed)

        # Add the log console for displaying logs
        self.log_console = QtWidgets.QTextEdit(self)
        self.log_console.setReadOnly(True)
        self.layout.addWidget(self.log_console)
        self.log_console.hide()  # Initially hide the log console

        # Create a menu bar
        menu_bar = QtWidgets.QMenuBar(self)
        self.layout.setMenuBar(menu_bar)

        # Create an options menu
        options_menu = menu_bar.addMenu("Options")

        # Create a 'Toggle Options' sub-menu
        toggle_options_menu = options_menu.addMenu("Toggle Options")

        # Add an action to toggle the ID column visibility
        toggle_id_action = QtWidgets.QAction("ID Column", self)
        toggle_id_action.setCheckable(True)
        toggle_id_action.toggled.connect(self.toggle_id_column)
        toggle_options_menu.addAction(toggle_id_action)

        # Add an action to toggle the logging console visibility
        toggle_log_action = QtWidgets.QAction("Logging Console", self)
        toggle_log_action.triggered.connect(self.toggle_logging_console)
        toggle_options_menu.addAction(toggle_log_action)

        # Create an 'Export' sub-menu
        export_menu = options_menu.addMenu("Export")

        # Add an action to export the shopping list
        export_cart_action = QtWidgets.QAction("Export Cart", self)
        export_cart_action.triggered.connect(self.export_cart)
        export_menu.addAction(export_cart_action)

        # Add an action to export the logs
        export_logs_action = QtWidgets.QAction("Export Logs", self)
        export_logs_action.triggered.connect(self.export_logs)
        export_menu.addAction(export_logs_action)

        # Add an action to toggle the ability to edit items in the table
        toggle_edit_action = QtWidgets.QAction("Toggle Edit Mode", self)
        toggle_edit_action.setCheckable(True)
        toggle_edit_action.setChecked(False)  # Editing is disabled by default
        toggle_edit_action.toggled.connect(self.toggle_edit_mode)
        toggle_options_menu.addAction(toggle_edit_action)

    def add_item_to_cart(self):
        """
        Add the specified item and price to the cart and update the table.

        This method retrieves the item name and price from the input fields,
        adds them to the cart, and updates the table to reflect the changes.
        """
        item_name = self.item_input.text()
        try:
            item_price = float(self.price_input.text())
            item_id = self.cart.add_item(item_name, item_price)
            self.refresh_table()
            self.item_input.clear()
            self.price_input.clear()
            self.calculate_total()
            logging.info(f"Item {item_name} with ID {item_id} and price {item_price:.2f} $ added via GUI.")
        except ValueError as e:
            logging.error(f"Exception occurred: {e}")
            QMessageBox.critical(self, "Invalid Input", "Illegal character in price. Please enter a valid number.")

    def calculate_total(self):
        """
            Calculate and display the total cost of items in the cart.

            This method calculates the total price of all items in the cart
            and displays the result in the total display field.
            """
        total = self.cart.get_total_price()
        if total is None:  # Handle the case when there are no items
            total = 0.0
        self.total_display.setText(f"{total:.2f} $")

    def refresh_table(self):
        self.table.blockSignals(True)  # Block signals temporarily
        self.table.setRowCount(0)  # Clear the table
        items = self.cart.items
        for item in items:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(item['id'])))
            self.table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(item['item']))
            self.table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(f"{item['price']:.2f} $"))
        self.calculate_total()
        self.table.blockSignals(False)  # Unblock signals
        logging.info("Table refreshed with updated items.")

    def handle_item_changed(self, item):
        row = item.row()
        column = item.column()

        self.table.blockSignals(True)  # Block signals temporarily

        try:
            # If the item name is changed
            if column == 1:
                new_name = item.text()
                item_id = int(self.table.item(row, 0).text())
                old_name = self.table.item(row, 1).text()
                new_price = float(self.table.item(row, 2).text().replace(" $", "").strip())
                self.cart.update_item(old_name, new_name, new_price)  # Use the update_item method
                logging.info(f"Item with ID {item_id} updated to {new_name} via GUI.")
                self.table.item(row, 1).setText(new_name)

                # Recalculate the total immediately after updating the item's name
                self.calculate_total()

            # If the item price is changed
            elif column == 2:
                new_price_str = item.text().replace(" $", "").strip()
                new_price = float(new_price_str)  # This will raise ValueError if invalid
                item_name = self.table.item(row, 1).text()
                self.cart.update_item(item_name, new_price=new_price)
                self.calculate_total()
                logging.info(f"Price for item {item_name} updated to {new_price:.2f} $ via GUI.")
                self.table.item(row, 2).setText(f"{new_price:.2f} $")

            self.table.blockSignals(False)  # Unblock signals

        except ValueError as e:
            logging.error(f"Exception occurred: {e}")
            QMessageBox.critical(self, "Invalid Input", "Illegal character in price. Please enter a valid number.")
            item_name = self.table.item(row, 1).text()
            db_item = self.cart.get_item(item_name)  # Get the item details from the database
            if db_item:
                self.table.item(row, 2).setText(f"{db_item['price']:.2f} $")  # Revert to old price from the database
            self.table.blockSignals(False)  # Unblock signals

        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            QMessageBox.critical(self, "Error", str(e))
            self.table.blockSignals(False)  # Unblock signals

    def export_shopping_list(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Shopping List", "",
                                                            "Text Files (*.txt);;All Files (*)")
        if filename:
            self.cart.export_shopping_list(filename)

    def export_logs(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Logs", "",
                                                            "Text Files (*.txt);;All Files (*)")
        if filename:
            with open(filename, 'w') as file:
                file.write(self.log_console.toPlainText())
            logging.info(f"Logs exported to {filename}.")

    def export_cart(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Export Cart")
        msg_box.setText("How would you like to export the cart?")

        json_button = msg_box.addButton("JSON File", QMessageBox.ActionRole)
        text_button = msg_box.addButton("Text File", QMessageBox.ActionRole)
        both_button = msg_box.addButton("Export Both", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Cancel)

        msg_box.exec_()
        clicked_button = msg_box.clickedButton()

        if clicked_button == both_button:
            base_filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Cart", "", "All Files (*)"
            )
            if base_filename:
                json_filename = f"{base_filename}.json"
                text_filename = f"{base_filename}.txt"
                self.cart.export_cart_to_json(json_filename)
                self.cart.export_shopping_list(text_filename)
                logging.info(
                    f"Cart exported to {json_filename} as JSON and {text_filename} as text."
                )

        elif clicked_button == json_button:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Cart as JSON", "", "JSON Files (*.json);;All Files (*)"
            )
            if filename:
                self.cart.export_cart_to_json(filename)
                logging.info(f"Cart exported to {filename} as JSON.")

        elif clicked_button == text_button:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Cart as Text", "", "Text Files (*.txt);;All Files (*)"
            )
            if filename:
                self.cart.export_shopping_list(filename)
                logging.info(f"Cart exported to {filename} as text.")

    def toggle_id_column(self, checked):
        """
            Toggle the visibility of the ID column.

            Args:
                checked (bool): Whether the ID column should be visible or not.
            """
        self.table.setColumnHidden(0, not checked)

    def toggle_logging_console(self):
        """
        Toggle the visibility of the logging console.

        This method shows or hides the logging console based on its current visibility.
        """
        if self.log_console.isVisible():
            self.log_console.hide()
        else:
            self.log_console.show()

    def toggle_edit_mode(self, checked):
        if checked:
            self.table.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
            self.table.setStyleSheet("background-color: #8B0000")  # Dark Red
        else:
            self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            self.table.setStyleSheet("")  # Reset to default background color and text color

    def configure_logging_handler(self):
        log_handler = QtLogHandler(self.log_console)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)


class CustomTableWidget(QtWidgets.QTableWidget):
    """
    Custom QTableWidget with a context menu to remove items.

    Provides a table widget that allows users to right-click on an item and remove it
    from the shopping cart.
    """

    def __init__(self, cart, parent=None):
        """
        Initialize the custom table widget.

        Args:
            cart (ShoppingCart): The shopping cart API instance.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.cart = cart

        # Allow multiple rows to be selected
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

    def contextMenuEvent(self, event):
        """
        Reimplement the contextMenuEvent to provide a custom context menu.

        Args:
            event (QEvent): The context menu event.
        """
        menu = QtWidgets.QMenu(self)
        remove_action = menu.addAction("Remove")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == remove_action:
            selected_rows = set([index.row() for index in self.selectedIndexes()])
            for row in sorted(selected_rows, reverse=True):
                item_name = self.item(row, 1).text()  # Get item name from the second column
                self.cart.remove_item(item_name)
                self.removeRow(row)
            self.parent().calculate_total()  # Update the total after removing items


class QtLogHandler(logging.Handler):
    """
    Custom logging handler to direct log messages to a QTextEdit widget.
    Provides a handler that takes log messages and appends them to a specified QTextEdit widget.
   """

    def __init__(self, log_widget):
        """
        Initialize the handler.

        Args:
            log_widget (QTextEdit): The widget to which log messages will be directed.
        """
        super().__init__()
        self.widget = log_widget

    def emit(self, record):
        """
        Emit a log message to the QTextEdit widget.

        Args:
            record (LogRecord): The log record to be emitted.
        """
        msg = self.format(record)
        self.widget.append(msg)


# Initialize the application and GUI
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShoppingCartGUI()
    window.show()
    sys.exit(app.exec_())
