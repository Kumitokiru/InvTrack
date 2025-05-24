# InvTrack — Inventory Restocking Simulator

InvTrack is a desktop application (built in Python 3.13) that simulates a single-item inventory system with reorder policies. It features:

- **Interactive parameter inputs** (starting inventory, daily demand, reorder point, delivery delay, restock quantity, simulation length)  
- **Matplotlib chart** of inventory level over time  
- **Statistics panel** (stockouts, orders made, average inventory)  
- **Animated “Activity View”** (color-coded boxes + truck arrival animation)  
- **Tkinter GUI** for maximum compatibility and minimal footprint  
- **Single-file EXE** packaging via PyInstaller (with custom icon)  

---

## 📋 Requirements

- Python 3.10+ (3.13 recommended)  
- Windows 10/11 (tested)  
- Packages (in `requirements.txt`):
matplotlib==3.7.2
numpy==1.25.0
pyinstaller==6.11.1

*(plus built-ins: `tkinter`, `random`, etc.)*

Install via:

```terminal
pip install -r requirements.txt
```

🔧 Installation & Running from Source
1. Go to the directory where you want to clone the repository and then right click on that directory and click terminal
```terminal
git clone https://github.com/Kumitokiru/InvTrack.git
```

Your folder structure inside your chosen directory where you clone the repository should look like this:


```terminal
InvTrack/
├── assets/
│   └── IV.ico            # Custom icon for EXE
├── build/                # (PyInstaller build folder)
├── dist/                 # (PyInstaller output folder)
├── main.py               # Tkinter GUI + simulation controller
├── model.py              # InventorySimulator class (discrete-event logic)
├── requirements.txt      # pip dependencies
├── main.spec             # (optional) PyInstaller spec file
└── README.md             # This file
```

2. Install dependencies
```terminal
pip install -r requirements.txt
```

3. Launch the app
```terminal
python main.py
```

or 

Go to dist folder, look for InvTrack.exe and open it


🧪 Simulation Model
Initialization: inventory = starting_inventory, no pending order

Each day (0 … sim_length−1):

If an order was placed delivery_delay days ago, receive restock_quantity.

Sample daily demand ∼ N(avg_daily_demand, 0.1·avg_daily_demand) → round & floor at ≥ 0.

If demand > inventory → stockout, inventory = 0; else inventory –= demand.

If inventory ≤ reorder_point and no pending order → place new order (delay countdown).

Metrics returned:

history (inventory/day)

arrivals (boolean list marking restock days)

stats = { stockouts, orders_made, avg_inventory }
