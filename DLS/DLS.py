import random
import tkinter as tk
from tkinter import messagebox, ttk


class DLSController:
	"""A tiny neural controller trained with gradient descent."""

	def __init__(self):
		random.seed(7)
		self.weights = [random.uniform(-1, 1) for _ in range(2)]
		self.bias = 0.0
		self.train()

	def train(self):
		examples = []
		for current in range(0, 101, 5):
			for target in range(10, 101, 5):
				error = max(0, target - current) / 100
				desired_power = min(1, error * 1.35)
				examples.append(([target / 100, current / 100], desired_power))

		for _ in range(900):
			for features, expected in examples:
				prediction = self.predict(features)
				difference = prediction - expected
				self.weights[0] -= 0.08 * difference * features[0]
				self.weights[1] -= 0.08 * difference * features[1]
				self.bias -= 0.08 * difference

	def predict(self, features):
		value = self.bias + sum(weight * feature for weight, feature in zip(self.weights, features))
		return max(0.0, min(1.0, value))

	def valve_power(self, target, current):
		return self.predict([target / 100, current / 100])


class ElectricBikeApp:
	MIN_BATTERY = 0
	MAX_BATTERY = 100
	LOW_BATTERY = 20

	def __init__(self, root):
		self.root = root
		self.root.title("DLS Electric Bike Battery")
		self.root.geometry("560x650")
		self.root.minsize(480, 590)
		self.root.configure(bg="#eef3f1")

		self.controller = DLSController()
		self.battery_level = 100
		self.running = False
		self.after_id = None

		self.battery_value = tk.StringVar(value="100")
		self.level_text = tk.StringVar(value="100%")
		self.status_text = tk.StringVar(value="Ready to ride")
		self.power_text = tk.StringVar(value="DLS motor power: 0%")

		self.build_ui()
		self.draw_tank()

	def build_ui(self):
		header = tk.Frame(self.root, bg="#123c3a", height=112)
		header.pack(fill="x")
		header.pack_propagate(False)
		tk.Label(header, text="DLS ELECTRIC BIKE", font=("Segoe UI", 24, "bold"),
				 fg="#f5fbf8", bg="#123c3a").pack(anchor="w", padx=32, pady=(24, 0))
		tk.Label(header, text="Battery discharge monitor", font=("Segoe UI", 10),
				 fg="#a9d7c8", bg="#123c3a").pack(anchor="w", padx=34)

		controls = tk.Frame(self.root, bg="#eef3f1")
		controls.pack(fill="x", padx=32, pady=(24, 8))
		tk.Label(controls, text="STARTING BATTERY", font=("Segoe UI", 9, "bold"),
				 fg="#41625d", bg="#eef3f1").pack(anchor="w")
		row = tk.Frame(controls, bg="#eef3f1")
		row.pack(fill="x", pady=(5, 0))
		self.battery_entry = ttk.Entry(row, textvariable=self.battery_value, width=10, font=("Segoe UI", 15))
		self.battery_entry.pack(side="left", ipady=5)
		tk.Label(row, text="%  (0 - 100)", font=("Segoe UI", 11),
				 fg="#41625d", bg="#eef3f1").pack(side="left", padx=10)
		tk.Button(row, text="Start ride", command=self.start_ride).pack(side="right", ipady=3)

		self.canvas = tk.Canvas(self.root, width=300, height=310, bg="#eef3f1", highlightthickness=0)
		self.canvas.pack(pady=(4, 0))

		tk.Label(self.root, textvariable=self.level_text, font=("Segoe UI", 28, "bold"),
				 fg="#123c3a", bg="#eef3f1").pack()
		tk.Label(self.root, textvariable=self.status_text, font=("Segoe UI", 11),
				 fg="#41625d", bg="#eef3f1").pack(pady=(2, 0))

		info = tk.Frame(self.root, bg="#dce9e4")
		info.pack(fill="x", padx=32, pady=20)
		tk.Label(info, textvariable=self.power_text, font=("Segoe UI", 10, "bold"),
				 fg="#123c3a", bg="#dce9e4").pack(anchor="w", padx=16, pady=(12, 2))
		tk.Label(info, text="The DLS model reduces valve power as the water approaches the target.",
				 font=("Segoe UI", 9), fg="#41625d", bg="#dce9e4", wraplength=460,
				 justify="left").pack(anchor="w", padx=16, pady=(0, 12))

		ttk.Button(self.root, text="Reset tank", command=self.reset).pack(pady=(0, 12))

	def draw_tank(self):
		self.canvas.delete("all")
		left, top, right, bottom = 72, 20, 228, 275
		self.canvas.create_rectangle(left, top, right, bottom, outline="#123c3a", width=4)
		self.canvas.create_rectangle(left - 8, top - 8, right + 8, top, fill="#123c3a", outline="")

		fill_height = (bottom - top) * self.battery_level / self.MAX_BATTERY
		water_top = bottom - fill_height
		if fill_height > 0:
			self.canvas.create_rectangle(left + 4, water_top, right - 4, bottom - 4,
										 fill="#f0b429" if self.battery_level <= self.LOW_BATTERY else "#39aeb0", outline="")
			self.canvas.create_arc(left + 4, water_top - 7, right - 4, water_top + 7,
								   start=0, extent=180, fill="#f6cc66" if self.battery_level <= self.LOW_BATTERY else "#5ac9c3", outline="")

		for battery in (100, 75, 50, 25, 0):
			y = bottom - (bottom - top) * battery / self.MAX_BATTERY
			self.canvas.create_line(right + 10, y, right + 18, y, fill="#41625d", width=2)
			self.canvas.create_text(right + 43, y, text=f"{battery}%", fill="#41625d",
									font=("Segoe UI", 9))

	def start_ride(self):
		try:
			battery = int(self.battery_value.get())
		except ValueError:
			messagebox.showerror("Invalid battery", "Enter a whole number from 0 to 100.")
			return
		if not self.MIN_BATTERY <= battery <= self.MAX_BATTERY:
			messagebox.showerror("Invalid battery", "Battery must be between 0% and 100%.")
			return
		self.battery_level = battery
		self.running = True
		if self.battery_level <= self.LOW_BATTERY:
			self.status_text.set("LOW BATTERY - charge your bike")
		else:
			self.status_text.set("Riding... battery drains 1% per second")
		self.draw_tank()
		self.after_id = self.root.after(1000, self.tick)

	def tick(self):
		if not self.running:
			return
		if self.battery_level <= 0:
			self.battery_level = 0
			self.running = False
			self.status_text.set("Battery empty - ride stopped")
			self.power_text.set("DLS motor power: 0%")
		else:
			self.battery_level -= 1
			if self.battery_level <= self.LOW_BATTERY:
				self.status_text.set("LOW BATTERY - charge your bike")
				self.power_text.set("DLS motor power: reduced")
			else:
				self.power_text.set("DLS motor power: normal")
			self.level_text.set(f"{self.battery_level}%")
			self.after_id = self.root.after(1000, self.tick)
		self.draw_tank()

	def reset(self):
		self.running = False
		if self.after_id:
			self.root.after_cancel(self.after_id)
			self.after_id = None
		self.battery_level = 100
		self.battery_value.set("100")
		self.status_text.set("Ready to ride")
		self.power_text.set("DLS motor power: 0%")
		self.level_text.set("100%")
		self.draw_tank()


if __name__ == "__main__":
	app_root = tk.Tk()
	ElectricBikeApp(app_root)
	app_root.mainloop()
