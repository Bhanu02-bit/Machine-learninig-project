import tkinter as tk
from tkinter import messagebox


class DLSBatteryController:
    """Simple DLS controller for electric-bike battery monitoring."""

    LOW_BATTERY = 20
    STOP_BATTERY = 5

    def __init__(self, battery_level):
        self.battery_level = battery_level
        self.running = False

    def decrease_battery(self):
        if self.battery_level > 0:
            self.battery_level -= 1
        return self.battery_level

    def is_low_battery(self):
        return self.battery_level <= self.LOW_BATTERY


class ElectricBikeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DLS Electric Bike Battery")
        self.root.geometry("450x500")
        self.root.configure(bg="#eef3f1")

        self.controller = DLSBatteryController(100)
        self.timer_id = None
        self.low_notification_shown = False

        self.battery_input = tk.StringVar(value="100")
        self.battery_text = tk.StringVar(value="100%")
        self.status_text = tk.StringVar(value="Ready to ride")

        tk.Label(
            root,
            text="DLS ELECTRIC BIKE",
            font=("Segoe UI", 24, "bold"),
            bg="#123c3a",
            fg="white",
            pady=20
        ).pack(fill="x")

        tk.Label(
            root,
            text="Starting battery percentage",
            font=("Segoe UI", 11, "bold"),
            bg="#eef3f1",
            fg="#123c3a"
        ).pack(pady=(25, 5))

        tk.Entry(
            root,
            textvariable=self.battery_input,
            font=("Segoe UI", 16),
            width=10,
            justify="center"
        ).pack()

        self.battery_canvas = tk.Canvas(
            root,
            width=220,
            height=260,
            bg="#eef3f1",
            highlightthickness=0
        )
        self.battery_canvas.pack(pady=20)

        tk.Label(
            root,
            textvariable=self.battery_text,
            font=("Segoe UI", 30, "bold"),
            bg="#eef3f1",
            fg="#123c3a"
        ).pack()

        tk.Label(
            root,
            textvariable=self.status_text,
            font=("Segoe UI", 12, "bold"),
            bg="#eef3f1",
            fg="#41625d"
        ).pack(pady=8)

        buttons = tk.Frame(root, bg="#eef3f1")
        buttons.pack(pady=15)

        tk.Button(
            buttons,
            text="Start Ride",
            command=self.start_ride,
            bg="#123c3a",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=15
        ).pack(side="left", padx=5)

        tk.Button(
            buttons,
            text="Reset",
            command=self.reset,
            font=("Segoe UI", 11),
            padx=15
        ).pack(side="left", padx=5)

        self.draw_battery()

    def start_ride(self):
        try:
            battery = int(self.battery_input.get())

            if not 0 <= battery <= 100:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid battery",
                "Enter a whole number between 0 and 100."
            )
            return

        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        self.controller = DLSBatteryController(battery)
        self.controller.running = battery > self.controller.STOP_BATTERY
        self.low_notification_shown = battery <= self.controller.LOW_BATTERY

        self.update_display()
        if battery <= self.controller.LOW_BATTERY:
            messagebox.showwarning(
                "Low battery",
                "Battery is low. Keep charging your bike."
            )
        if battery <= self.controller.STOP_BATTERY:
            self.status_text.set("Battery reached 5% - ride stopped. Keep charging.")
        else:
            self.timer_id = self.root.after(1000, self.tick)

    def tick(self):
        if not self.controller.running:
            return

        self.controller.decrease_battery()
        self.update_display()

        if self.controller.battery_level <= self.controller.STOP_BATTERY:
            self.controller.battery_level = self.controller.STOP_BATTERY
            self.controller.running = False
            self.status_text.set("Battery reached 5% - ride stopped. Keep charging.")
            messagebox.showwarning(
                "Battery stopped",
                "Battery reached 5%. Keep charging your bike."
            )
            return

        if (self.controller.battery_level <= self.controller.LOW_BATTERY
                and not self.low_notification_shown):
            self.low_notification_shown = True
            messagebox.showwarning(
                "Low battery",
                "Battery reached 20%. Keep charging your bike."
            )

        self.timer_id = self.root.after(1000, self.tick)

    def update_display(self):
        level = self.controller.battery_level
        self.battery_text.set(f"{level}%")

        if self.controller.is_low_battery():
            self.status_text.set("LOW BATTERY - Please charge your bike")
        else:
            self.status_text.set("Riding... battery decreases 1% per second")

        self.draw_battery()

    def draw_battery(self):
        self.battery_canvas.delete("all")

        level = self.controller.battery_level
        left, top, right, bottom = 55, 25, 165, 225

        color = "#e05252" if level <= 20 else "#39aeb0"

        self.battery_canvas.create_rectangle(
            left, top, right, bottom,
            outline="#123c3a",
            width=4
        )

        self.battery_canvas.create_rectangle(
            85, 10, 135, 25,
            fill="#123c3a",
            outline=""
        )

        fill_height = (bottom - top) * level / 100
        fill_top = bottom - fill_height

        if level > 0:
            self.battery_canvas.create_rectangle(
                left + 5,
                fill_top,
                right - 5,
                bottom - 5,
                fill=color,
                outline=""
            )

    def reset(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.controller = DLSBatteryController(100)
        self.low_notification_shown = False
        self.battery_input.set("100")
        self.battery_text.set("100%")
        self.status_text.set("Ready to ride")
        self.draw_battery()


if __name__ == "__main__":
    root = tk.Tk()
    app = ElectricBikeGUI(root)
    root.mainloop()