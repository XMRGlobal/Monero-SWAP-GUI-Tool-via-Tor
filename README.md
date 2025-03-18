# XMRGlobal Monero Swap Tool via Tor (GUI Version)

A **privacy-focused** Monero swap tool that interacts with the **XMRGlobal API** over Tor.

## Features
- Fetch live **exchange rates**.
- Create **anonymous swaps**.
- Check **swap status**.
- Works via **Tor onion addresses**.
- **Graphical User Interface (GUI) using PyQt6**.
- **CAPTCHA protection** for swap creation & status checks.
- **Delete individual swaps** from history.

## Installation

### **1. Install Dependencies**
This tool requires **Python 3.8+** and **PyQt6**.

```bash
pip install PyQt6 requests
```

For **Debian-based systems** (like Whonix or Tails):
```bash
sudo apt install python3-pyqt6
```

### **2. Run the Tool**
After installing dependencies, launch the GUI:
```bash
python swap.py
```

## Usage

### **1. Fetch Exchange Rates**
- Select the **from** and **to** coins.
- Enter the **amount**.
- Click **Fetch Exchange Rate**.

### **2. Create a Swap**
- Enter the **amount**.
- Provide a **receiving address** and a **refund address**.
- Solve the **CAPTCHA**.
- Click **Create Swap**.
- You will receive a **Swap ID** and deposit details.

### **3. Check Swap Status**
- Enter a **Swap ID**.
- Solve the **CAPTCHA**.
- Click **Check Swap Status**.

### **4. Delete a Swap**
- Enter a **Swap ID**.
- Click **Delete Swap**.
- The swap is removed from local history.

## Security & Privacy
- **Tor-Only Communication**: All API calls use `.onion` addresses.
- **No Logs, No Tracking**.
- **PGP Support (Planned for future updates)**.

## Troubleshooting
If you encounter issues, ensure:
- You are connected to **Tor**.
- The dependencies (`PyQt6`, `requests`) are installed.
- The `.onion` addresses are reachable.

## Contributing
Pull requests are welcome! Submit issues or suggestions for improvements.

## License
This project is **open-source** and available under the MIT License.

---
🔗 **XMRGlobal Website**: [https://xmrglobal.io](https://xmrglobal.io)
