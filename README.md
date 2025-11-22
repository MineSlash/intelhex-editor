# Intel HEX Editor (Python)

A lightweight and easy-to-use Intel HEX parser and editor written in pure Python.  
Supports reading, modifying, and saving `.hex` firmware files with full extended address support.

## ✨ Features

- Full Intel HEX file parsing
- Checksum validation
- Supports Intel HEX record types:
  - `00` – Data Record
  - `01` – End of File
  - `04` – Extended Linear Address
  - `05` – Start Linear Address
- In-memory firmware editing
- Reading arbitrary memory ranges
- Writing and saving modified HEX files
- Automatically handles:
  - Extended addressing
  - 32-byte data chunking
  - Address alignment

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/MineSlash/intelhex-editor.git
cd intelhex-editor
```

No external dependencies are required.

---

## 🔧 Usage Example

```python
from intelhex_editor import HexEditor

hex_editor = HexEditor('Sample.hex')

print("Start address:", hex_editor.start_address)
print("Length:", hex_editor.length)

# Read 16 bytes
data = hex_editor.read('0x803000A0', 0x10)
print("Read:", data)

# Write new data and save as a separate HEX file
hex_editor.write(
    address='0x803000A0',
    data='B0C1F0C1B0C1C1CADEADBEEF1EE7FEE7',
    output='Sample_modified.hex'
)
```

---

## 📂 Project Structure

```
intelhex-editor/
│
├─ intelhex_editor.py       # Main implementation
├─ Sample.hex               # Example HEX file (optional)
├─ LICENSE                  # MIT License
└─ README.md
```

---

## 🧠 How It Works

### Parsing
The `IntelHexFile` class reads the HEX file line by line:
- Validates checksums  
- Decodes record types  
- Handles extended linear addressing (`0x04`)  
- Stores all bytes in a sparse memory map (`dict[int, int]`)

### Memory Editing
The `HexEditor` wrapper provides:
- `read(address, length)`
- `write(address, data)`
- Automatic detection of the start address
- Saving modified output back to `.hex`

### Writing Output
The saved Intel HEX output includes:
- `:02000004xxxxCC` — Extended Linear Address records  
- `:20aaaa00[...]CC` — 32-byte data records  
- `:00000001FF` — End-of-file record  

---

## 📝 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for details.

---

## 🤝 Contributing

Pull requests, enhancements, and bug reports are welcome.

---

## ⭐ Support

If you find this project useful, please consider giving it a star on GitHub! ⭐
