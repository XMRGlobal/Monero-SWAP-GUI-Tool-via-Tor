import sys
import os
import json
import requests
import random
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QTextEdit, QMessageBox, QListWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# === CONFIGURATION ===
ONION_ADDRESSES = [
    "cqy2caejjpclixkumyvb24agvyth67znr7koee5264i6ucjxno3rcaid.onion",
    "5a2k6b3ov6w2ryl5th3jnsrujqj4x4micvxz75pbeama47fzonnwwcyd.onion",
    "2syzexutltau2n455oryarrervet36fzj2sksxbkpmg5anzustojsvid.onion",
    "5arhxqhg6sbken6qfnlnb4ozw3m7kzhjafqhzt5fcgdpy5s7qcjfciad.onion",
]
TOR_PORT = 8000
SWAP_LOG_DIR = "/tmp/swap-id"
os.makedirs(SWAP_LOG_DIR, exist_ok=True)
COINS = ["XMR", "BTC", "ETH", "LTC", "DOGE", "ADA", "BCH", "SOL", "DOT", "TRX", "XLM"]

# === LOGGING ===
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# === GET WORKING ONION URL ===
def get_api_url():
    """Fetch a working API URL from the list of onion addresses."""
    for onion in random.sample(ONION_ADDRESSES, len(ONION_ADDRESSES)):
        api_url = f"http://{onion}:{TOR_PORT}"
        try:
            logging.debug(f"Testing API URL: {api_url}")
            response = requests.get(f"{api_url}/ping", timeout=10)
            if response.status_code == 200:
                logging.debug(f"Connected to API: {api_url}")
                return api_url
        except requests.RequestException as e:
            logging.warning(f"Failed to connect to {api_url}: {e}")
            continue
    logging.error("No available onion addresses!")
    QMessageBox.critical(None, "Connection Error", "No available onion addresses!")
    sys.exit(1)

API_URL = get_api_url()

# === THREAD CLASSES ===
class FetchRatesThread(QThread):
    """Thread for fetching exchange rates."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.finished.emit(data)
        except requests.RequestException as e:
            self.error.emit(str(e))

class CreateSwapThread(QThread):
    """Thread for creating a swap."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url, payload):
        super().__init__()
        self.url = url
        self.payload = payload

    def run(self):
        try:
            response = requests.post(self.url, json=self.payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.finished.emit(data)
        except requests.RequestException as e:
            self.error.emit(str(e))

class CheckSwapStatusThread(QThread):
    """Thread for checking swap status."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.finished.emit(data)
        except requests.RequestException as e:
            self.error.emit(str(e))

# === GUI CLASS ===
class XMRGlobalGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize the GUI layout and elements."""
        self.setWindowTitle("XMRGlobal.io Swap GUI-Tool via Tor")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        # From Coin
        layout.addWidget(QLabel("From Coin:"))
        self.from_coin_select = QComboBox()
        self.from_coin_select.addItems(COINS)
        layout.addWidget(self.from_coin_select)

        # To Coin
        layout.addWidget(QLabel("To Coin:"))
        self.to_coin_select = QComboBox()
        self.to_coin_select.addItems(COINS)
        layout.addWidget(self.to_coin_select)

        # Amount
        layout.addWidget(QLabel("Amount:"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        layout.addWidget(self.amount_input)

        # Fetch Rates Button
        self.fetch_rates_btn = QPushButton("Fetch Exchange Rate")
        self.fetch_rates_btn.clicked.connect(self.fetch_rates)
        layout.addWidget(self.fetch_rates_btn)

        # Rates Display
        self.rates_display = QTextEdit()
        self.rates_display.setReadOnly(True)
        layout.addWidget(self.rates_display)

        # Receiving Address
        layout.addWidget(QLabel("Receiving Address:"))
        self.receiving_address_input = QLineEdit()
        self.receiving_address_input.setPlaceholderText("Enter receiving address")
        layout.addWidget(self.receiving_address_input)

        # Refund Address
        layout.addWidget(QLabel("Refund Address:"))
        self.refund_address_input = QLineEdit()
        self.refund_address_input.setPlaceholderText("Enter refund address")
        layout.addWidget(self.refund_address_input)

        # Create Swap Button
        self.create_swap_btn = QPushButton("Create Swap")
        self.create_swap_btn.clicked.connect(self.create_swap)
        layout.addWidget(self.create_swap_btn)

        # Swap ID Input
        layout.addWidget(QLabel("Swap ID:"))
        self.swap_id_input = QLineEdit()
        self.swap_id_input.setPlaceholderText("Enter Swap ID to check status")
        layout.addWidget(self.swap_id_input)

        # Check Status Button
        self.check_status_btn = QPushButton("Check Swap Status")
        self.check_status_btn.clicked.connect(self.check_swap_status)
        layout.addWidget(self.check_status_btn)

        # View My Swaps Button
        self.view_swaps_btn = QPushButton("View My Swaps")
        self.view_swaps_btn.clicked.connect(self.view_swaps)
        layout.addWidget(self.view_swaps_btn)

        # Delete Swap Button
        self.delete_swap_btn = QPushButton("Delete Swap")
        self.delete_swap_btn.clicked.connect(self.delete_swap)
        layout.addWidget(self.delete_swap_btn)

        # Swaps List
        self.swaps_list = QListWidget()
        self.swaps_list.itemClicked.connect(self.on_swap_clicked)
        layout.addWidget(self.swaps_list)

        # Status Display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)

        # Set Layout
        self.setLayout(layout)

    def fetch_rates(self):
        """Fetch exchange rate for the selected coins and amount."""
        from_coin = self.from_coin_select.currentText()
        to_coin = self.to_coin_select.currentText()
        amount = self.amount_input.text().strip()

        if not amount:
            QMessageBox.warning(self, "Error", "Amount is required to check rates!")
            return

        url = f"{API_URL}/rate/{from_coin}/{to_coin}/{amount}"
        logging.debug(f"Fetching rates from: {url}")
        self.rates_display.setText("Fetching rate...")

        # Start the thread
        self.fetch_rates_thread = FetchRatesThread(url)
        self.fetch_rates_thread.finished.connect(self.on_fetch_rates_finished)
        self.fetch_rates_thread.error.connect(self.on_fetch_rates_error)
        self.fetch_rates_thread.start()

    def on_fetch_rates_finished(self, data):
        """Handle successful fetch rates response."""
        rate_with_commission = data.get("rate_with_commission", "N/A")
        min_amount = data.get("min_amount", "N/A")
        max_amount = data.get("max_amount", "N/A")

        # Format min_amount to display as a decimal number
        if isinstance(min_amount, float):
            min_amount = "{:.8f}".format(min_amount).rstrip('0').rstrip('.') if "." in "{:.8f}".format(min_amount) else "{:.8f}".format(min_amount)

        formatted_rate = (
            f"💱 **Exchange Rate**:\n"
            f"🔹 **1 {self.from_coin_select.currentText()} = {rate_with_commission} {self.to_coin_select.currentText()}**\n\n"
            f"📉 **Min Amount**: {min_amount} {self.from_coin_select.currentText()}\n"
            f"📈 **Max Amount**: {max_amount if max_amount else 'No Limit'} {self.from_coin_select.currentText()}"
        )

        self.rates_display.setText(formatted_rate)

    def on_fetch_rates_error(self, error):
        """Handle fetch rates error."""
        logging.error(f"Failed to fetch exchange rate: {error}")
        QMessageBox.critical(self, "Error", f"Failed to fetch exchange rate: {error}")
        self.rates_display.setText("Error fetching exchange rate.")

    def create_swap(self):
        """Create a swap by sending request to API."""
        from_coin = self.from_coin_select.currentText().lower()
        to_coin = self.to_coin_select.currentText().lower()
        amount = self.amount_input.text().strip()
        receiving_address = self.receiving_address_input.text().strip()
        refund_address = self.refund_address_input.text().strip()

        if not amount or not receiving_address or not refund_address:
            QMessageBox.warning(self, "Error", "All fields must be filled!")
            return

        # CAPTCHA verification
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        captcha_text = f"{num1} + {num2} = ?"
        captcha_answer, ok = QInputDialog.getText(self, "CAPTCHA", captcha_text)
        if not ok or not captcha_answer.isdigit() or int(captcha_answer) != num1 + num2:
            QMessageBox.warning(self, "Error", "CAPTCHA verification failed!")
            return

        # Ask for confirmation before proceeding
        confirm_msg = (
            f"🔹 **Swap Details:**\n"
            f"💱 {amount} {from_coin.upper()} → {to_coin.upper()}\n"
            f"📥 Receiving Address: {receiving_address}\n"
            f"🔄 Refund Address: {refund_address}\n\n"
            f"Do you want to proceed?"
        )
        
        reply = QMessageBox.question(self, "Confirm Swap", confirm_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Step 2: Send Swap Request
        swap_url = f"{API_URL}/swap"
        payload = {
            "from_coin": from_coin,
            "to_coin": to_coin,
            "amount": amount,
            "receiving_address": receiving_address,
            "refund_address": refund_address
        }

        # Start the thread
        self.create_swap_thread = CreateSwapThread(swap_url, payload)
        self.create_swap_thread.finished.connect(self.on_create_swap_finished)
        self.create_swap_thread.error.connect(self.on_create_swap_error)
        self.create_swap_thread.start()

    def on_create_swap_finished(self, swap_data):
        """Handle successful swap creation."""
        swap_id = swap_data.get("transaction_id", "Unknown")
        send_to_address = swap_data.get("send_to", "N/A")
        expected_amount = swap_data.get("expected_amount", "N/A")

        # Save swap details
        swap_file = os.path.join(SWAP_LOG_DIR, f"{swap_id}.json")
        with open(swap_file, "w") as file:
            json.dump(swap_data, file, indent=4)

        success_msg = (
            f"✅ **Swap Created Successfully!**\n"
            f"🔹 Swap ID: {swap_id}\n"
            f"📤 Please send {expected_amount} {self.from_coin_select.currentText().upper()} to:\n"
            f"➡️ {send_to_address}\n\n"
            f"💡 You can check your swap status anytime using the Swap ID."
        )

        QMessageBox.information(self, "Swap Created", success_msg)

        # Refresh swaps list
        self.view_swaps()

    def on_create_swap_error(self, error):
        """Handle swap creation error."""
        logging.error(f"Failed to create swap: {error}")
        QMessageBox.critical(self, "Error", f"Failed to create swap: {error}")

    def check_swap_status(self):
        """Check the status of an existing swap using the Swap ID."""
        swap_id = self.swap_id_input.text().strip()

        if not swap_id:
            QMessageBox.warning(self, "Error", "Swap ID is required!")
            return

        # CAPTCHA verification
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        captcha_text = f"{num1} + {num2} = ?"
        captcha_answer, ok = QInputDialog.getText(self, "CAPTCHA", captcha_text)
        if not ok or not captcha_answer.isdigit() or int(captcha_answer) != num1 + num2:
            QMessageBox.warning(self, "Error", "CAPTCHA verification failed!")
            return

        url = f"{API_URL}/swap/status/{swap_id}"
        logging.debug(f"Fetching swap status from: {url}")
        self.status_display.setText("Fetching swap status...")

        # Start the thread
        self.check_swap_status_thread = CheckSwapStatusThread(url)
        self.check_swap_status_thread.finished.connect(self.on_check_swap_status_finished)
        self.check_swap_status_thread.error.connect(self.on_check_swap_status_error)
        self.check_swap_status_thread.start()

    def on_check_swap_status_finished(self, swap_data):
        """Handle successful swap status fetch."""
        status = swap_data.get("status", "Unknown").upper()
        deposit_info = swap_data.get("deposit", {})
        withdrawal_info = swap_data.get("withdrawal", {})

        formatted_status = (
            f"🔹 **Swap ID**: {self.swap_id_input.text()}\n"
            f"📅 Created At: {swap_data.get('created_at', 'Unknown')}\n"
            f"🔄 **Status**: {status}\n\n"
            f"📤 **Deposit Details:**\n"
            f"   - Amount: {deposit_info.get('amount', 'N/A')} {deposit_info.get('symbol', '').upper()}\n"
            f"   - Address: {deposit_info.get('address', 'N/A')}\n"
            f"   - Explorer: {deposit_info.get('address_explorer_url', 'N/A')}\n\n"
            f"📥 **Withdrawal Details:**\n"
            f"   - Amount: {withdrawal_info.get('amount', 'N/A')} {withdrawal_info.get('symbol', '').upper()}\n"
            f"   - Address: {withdrawal_info.get('address', 'N/A')}\n"
            f"   - Explorer: {withdrawal_info.get('address_explorer_url', 'N/A')}\n"
        )

        self.status_display.setText(formatted_status)

    def on_check_swap_status_error(self, error):
        """Handle swap status fetch error."""
        logging.error(f"Failed to fetch swap status: {error}")
        QMessageBox.critical(self, "Error", f"Failed to fetch swap status: {error}")
        self.status_display.setText("Error fetching swap status.")

    def view_swaps(self):
        """Load and display saved swaps."""
        self.swaps_list.clear()
        swap_files = os.listdir(SWAP_LOG_DIR)
        
        if not swap_files:
            self.status_display.setText("❌ No saved swaps found.")
            return
        
        for file_name in swap_files:
            swap_id = file_name.replace(".json", "")
            self.swaps_list.addItem(swap_id)

    def on_swap_clicked(self, item):
        """Handle click event on a swap in the list."""
        swap_id = item.text()
        self.swap_id_input.setText(swap_id)
        self.check_swap_status()

    def delete_swap(self):
        """Delete a selected swap."""
        selected_swap = self.swaps_list.currentItem()
        if not selected_swap:
            QMessageBox.warning(self, "Error", "No swap selected!")
            return

        swap_id = selected_swap.text()
        swap_file = os.path.join(SWAP_LOG_DIR, f"{swap_id}.json")
        if os.path.exists(swap_file):
            os.remove(swap_file)
            QMessageBox.information(self, "Success", f"Swap {swap_id} deleted successfully!")
            self.view_swaps()
        else:
            QMessageBox.warning(self, "Error", f"Swap {swap_id} not found!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XMRGlobalGUI()
    window.show()
    sys.exit(app.exec())
