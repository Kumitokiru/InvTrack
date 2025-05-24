import sys
import random
import tkinter as tk
from tkinter import messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ────────────────────────────────────────────────────────────────────────────────
# INVENTORY SIMULATOR (formerly model.py)
# ────────────────────────────────────────────────────────────────────────────────

class InventorySimulator:
    """
    InventorySimulator models a simple restocking system:
      - starting_inventory: initial stock level (int)
      - avg_daily_demand: average demand per day (int)
      - reorder_point: when inventory ≤ this, place a new order (int)
      - delivery_delay: days between order placement and arrival (int)
      - restock_quantity: units added when order arrives (int)
      - sim_length: total days to simulate (int)
    """
    def __init__(self, starting_inventory, avg_daily_demand, reorder_point,
                 delivery_delay, restock_quantity, sim_length):
        self.starting_inventory = starting_inventory
        self.avg_daily_demand = avg_daily_demand
        self.reorder_point = reorder_point
        self.delivery_delay = delivery_delay
        self.restock_quantity = restock_quantity
        self.sim_length = sim_length

    def run(self):
        inventory = self.starting_inventory
        pending_order = None
        history = []
        arrivals = []
        stockouts = 0
        orders_made = 0

        for day in range(self.sim_length):
            arrived = False

            # 1) Check if a pending order has arrived this day
            if pending_order is not None:
                pending_order -= 1
                if pending_order <= 0:
                    inventory += self.restock_quantity
                    pending_order = None
                    arrived = True

            # 2) Generate daily demand (Gaussian around avg_daily_demand)
            demand = max(0, int(random.gauss(
                self.avg_daily_demand,
                self.avg_daily_demand * 0.1
            )))

            # 3) Fulfill demand (count stockouts if demand > inventory)
            if demand > inventory:
                stockouts += 1
                inventory = 0
            else:
                inventory -= demand

            # 4) Place a new order if needed
            if inventory <= self.reorder_point and pending_order is None:
                pending_order = self.delivery_delay
                orders_made += 1

            # 5) Record end-of-day inventory and arrival
            history.append(inventory)
            arrivals.append(arrived)

        avg_inventory = sum(history) / len(history) if history else 0
        stats = {
            'stockouts': stockouts,
            'orders_made': orders_made,
            'avg_inventory': avg_inventory
        }
        return history, arrivals, stats


# ────────────────────────────────────────────────────────────────────────────────
# TKINTER GUI + ANIMATION
# ────────────────────────────────────────────────────────────────────────────────

BG_BLUE      = "#00ADEF"
PANEL_BROWN  = "#C2A17F"
INPUT_BG     = "#C2A17F"
INPUT_BORDER = "#A68569"
BUTTON_BG    = "#FF6F61"
BUTTON_HOVER = "#FF766D"
TEXT_BLACK   = "#212121"

BOX_NORMAL   = "#4fc3f7"
BOX_LOW      = "#ffca28"
BOX_CRITICAL = "#ef5350"
TRUCK_COLOR  = "#616161"

TRUCK_WIDTH    = 30
TRUCK_HEIGHT   = 20
TRUCK_Y        = 100
ANIM_STEP      = 5
ANIM_PAUSE     = 500
FRAME_INTERVAL = 500


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("InvTrack - Inventory Restocking Simulator")
        self.configure(bg=BG_BLUE)
        self.minsize(1100, 750)

        # Simulation data
        self.history = []
        self.arrivals = []
        self.stats = {}
        self.day = 0
        self.animating = False

        # Truck animation state
        self.truck_animating = False
        self.truck_direction = 1
        self.truck_x = -TRUCK_WIDTH

        # Build UI
        self._create_input_form()
        self._create_run_button()
        self._create_bottom_panels()
        self._create_animation_canvas()

    def _create_input_form(self):
        frame = tk.Frame(self, bg=BG_BLUE)
        frame.pack(padx=30, pady=(20, 0), fill=tk.X)

        labels = [
            ("starting_inventory", "Starting Inventory", 100),
            ("avg_daily_demand",    "Avg Daily Demand", 10),
            ("reorder_point",       "Reorder Point", 10),
            ("delivery_delay",      "Delivery Delay (Days)", 2),
            ("restock_quantity",    "Restock Quantity", 20),
            ("sim_length",          "Simulation Length (Days)", 30)
        ]
        self.inputs = {}

        for i, (key, text, default) in enumerate(labels):
            row, col = divmod(i, 3)
            lbl = tk.Label(frame, text=text, bg=BG_BLUE,
                           fg=TEXT_BLACK, font=("Segoe UI", 10))
            lbl.grid(row=row, column=col*2, sticky="w", padx=5, pady=5)

            entry = tk.Entry(frame, bg=INPUT_BG, fg=TEXT_BLACK,
                             bd=1, relief="solid", justify="center",
                             font=("Segoe UI", 10))
            entry.insert(0, str(default))
            entry.config(highlightthickness=1,
                         highlightbackground=INPUT_BORDER,
                         highlightcolor=INPUT_BORDER)
            entry.grid(row=row, column=col*2+1,
                       sticky="we", padx=5, pady=5)
            self.inputs[key] = entry

        for c in range(6):
            frame.columnconfigure(c, weight=1)

    def _create_run_button(self):
        frame = tk.Frame(self, bg=BG_BLUE)
        frame.pack(fill=tk.X, padx=30, pady=(10, 20))
        self.run_button = tk.Button(frame, text="Run Simulation",
                                    bg=BUTTON_BG, fg="white",
                                    font=("Segoe UI",10,"bold"),
                                    relief="flat", activebackground=BUTTON_HOVER,
                                    command=self._on_run_clicked)
        self.run_button.pack(pady=5)
        self.run_button.bind("<Enter>",
                             lambda e: self.run_button.config(bg=BUTTON_HOVER))
        self.run_button.bind("<Leave>",
                             lambda e: self.run_button.config(bg=BUTTON_BG))

    def _create_bottom_panels(self):
        bf = tk.Frame(self, bg=BG_BLUE)
        bf.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0,30))

        # Chart (left)
        lc = tk.Frame(bf, bg=PANEL_BROWN)
        lc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        lc.grid_rowconfigure(1, weight=1)
        lc.grid_columnconfigure(0, weight=1)

        tk.Label(lc, text="Inventory Level Over Time",
                 bg=PANEL_BROWN, fg=TEXT_BLACK,
                 font=("Segoe UI",12,"bold")).grid(
            row=0, column=0, sticky="w", padx=15, pady=(15,5))

        self.figure = Figure(figsize=(5,4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=lc)
        self.chart_canvas.get_tk_widget().grid(
            row=1, column=0, sticky="nsew", padx=15, pady=(0,15))

        # Stats + Animation (right)
        rc = tk.Frame(bf, bg=BG_BLUE)
        rc.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Stats
        sf = tk.Frame(rc, bg=PANEL_BROWN, height=300)
        sf.pack(fill=tk.X, pady=(0,10))
        sf.pack_propagate(False)
        tk.Label(sf, text="Statistics", bg=PANEL_BROWN,
                 fg=TEXT_BLACK, font=("Segoe UI",15,"bold")
        ).pack(anchor="nw", padx=190, pady=(15,5))
        self.stats_text = tk.Text(sf, height=5, bg=PANEL_BROWN,
                                  fg=TEXT_BLACK, font=("Segoe UI",15,"bold"),
                                  bd=0, highlightthickness=0)
        self.stats_text.pack(fill=tk.BOTH, expand=True,
                             padx=15, pady=(0,15))
        self.stats_text.config(state="disabled", wrap="word")

        # Animation
        af_outer = tk.Frame(rc, bg=BG_BLUE, height=300)
        af_outer.pack(fill=tk.X, pady=(0,20))
        af_outer.pack_propagate(False)

        ac = tk.Frame(af_outer, bg=PANEL_BROWN)
        ac.pack(fill=tk.BOTH, expand=True)
        ac.grid_rowconfigure(1, weight=1)
        ac.grid_columnconfigure(0, weight=1)

        tk.Label(ac, text="Activity View", bg=PANEL_BROWN,
                 fg=TEXT_BLACK, font=("Segoe UI",20,"bold")
        ).grid(row=0, column=0, pady=(15,5))

        self.anim_canvas = tk.Canvas(ac, bg=PANEL_BROWN,
                                     highlightthickness=0)
        self.anim_canvas.grid(row=1, column=0, sticky="nsew",
                              padx=15, pady=(0,15))

    def _create_animation_canvas(self):
        self.anim_canvas.delete("all")
        self.day = 0
        self.animating = False
        self.truck_animating = False
        self.truck_direction = 1
        self.truck_x = -TRUCK_WIDTH

    def _on_run_clicked(self):
        if self.animating:
            self.animating = False
            self.after_cancel(self.after_id)

        try:
            params = {k:int(v.get()) for k,v in self.inputs.items()}
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Please enter valid integers.")
            return

        sim = InventorySimulator(**params)
        self.history, self.arrivals, self.stats = sim.run()

        # Update chart
        self.ax.clear()
        self.ax.plot(self.history, color="#005F99")
        self.ax.set_title("Inventory Level Over Time")
        self.ax.set_xlabel("Day")
        self.ax.set_ylabel("Inventory")
        self.chart_canvas.draw()

        # Update stats
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(
            tk.END,
            f"\nStockouts:     {self.stats['stockouts']}\n\n"
            f"Orders Made:   {self.stats['orders_made']}\n\n"
            f"Avg Inventory: {self.stats['avg_inventory']:.2f}"
        )
        self.stats_text.config(state="disabled")

        # Animate
        self._create_animation_canvas()
        self.animating = True
        self._animate_step()

    def _animate_step(self):
        if not self.animating or self.day >= len(self.history):
            self.animating = False
            return

        # Clear previous
        self.anim_canvas.delete("boxes")
        self.anim_canvas.delete("truck")

        inv = self.history[self.day]
        arrived = self.arrivals[self.day]
        rp = int(self.inputs["reorder_point"].get())
        rq = int(self.inputs["restock_quantity"].get())

        display_inv = inv + rq if arrived else inv

        # Draw boxes
        for i in range(display_inv // 5):
            x = 10 + (i % 20)*12
            y = 130 - (i//20)*12
            if display_inv > rp:
                c = BOX_NORMAL
            elif display_inv <= rp*0.5:
                c = BOX_CRITICAL
            else:
                c = BOX_LOW
            self.anim_canvas.create_rectangle(
                x, y, x+10, y+10, fill=c, outline="black", tags="boxes"
            )

        # Truck
        if arrived and not self.truck_animating:
            self.truck_animating = True
            self.truck_direction = 1
            self.truck_x = -TRUCK_WIDTH

        if self.truck_animating:
            self.truck_x += ANIM_STEP * self.truck_direction
            self.anim_canvas.create_rectangle(
                self.truck_x, TRUCK_Y,
                self.truck_x+TRUCK_WIDTH, TRUCK_Y+TRUCK_HEIGHT,
                fill=TRUCK_COLOR, outline="black", tags="truck"
            )
            if self.truck_direction == 1 and self.truck_x >= 100:
                self.truck_direction = 0
                self.after(ANIM_PAUSE,
                           lambda: setattr(self, "truck_direction", -1))
            elif self.truck_direction == -1 and self.truck_x < -TRUCK_WIDTH:
                self.truck_animating = False

        self.day += 1
        self.after_id = self.after(FRAME_INTERVAL, self._animate_step)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
