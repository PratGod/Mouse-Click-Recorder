import tkinter as tk
from tkinter import messagebox, Menu, simpledialog
import pyautogui
import time
import threading
import mouse
import keyboard

# just a simple auto clicking program to cheat in games basically is like u log(record) mouse x and y coordinates and shoot(run) the exact logs on the type of mouse click u choose single or double, its pretty cool my first .py project that includes gui had to search alot

class ClickRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Click Recorder")
        self.root.attributes('-topmost', True)
        self.clicks = []
        self.running = False  # bool as a button for playback like pause/run
        self.overlays = []  # stores the over-lay windows thing

        # single and double click, dont really think i will add right click as wlel cus theres no need no one uses right click to play games 
        self.click_type = tk.StringVar(value="single")
        tk.Label(root, text="Select Click Type:").pack()
        tk.Radiobutton(root, text="Single Click", variable=self.click_type, value="single").pack()
        tk.Radiobutton(root, text="Double Click", variable=self.click_type, value="double").pack()

        # the buttons
        self.log_button = tk.Button(root, text="Log Mouse Position", command=self.start_logging)
        self.log_button.pack()

        self.show_button = tk.Button(root, text="Show Coordinates", command=self.show_highlights)
        self.show_button.pack()

        self.hide_button = tk.Button(root, text="Hide Coordinates", command=self.hide_highlights)
        self.hide_button.pack()

        self.clear_button = tk.Button(root, text="Clear Table", command=self.clear_table)
        self.clear_button.pack()

        # Delay
        tk.Label(root, text="Delay (ms) before sending click:").pack()
        self.delay_entry = tk.Entry(root)
        self.delay_entry.pack()
        self.delay_entry.insert(0, "1000")

        # Click lists 
        self.click_listbox = tk.Listbox(root, width=50)
        self.click_listbox.pack()
        self.click_listbox.bind("<Button-3>", self.show_context_menu)

        # Context menu, default 0
        self.context_menu = Menu(root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)

        # Play & Stop buttons to shoot the recorded logs or coordinates 
        self.play_button = tk.Button(root, text="Play Clicks (Tab)", command=self.play_clicks)
        self.play_button.pack()

        self.stop_button = tk.Button(root, text="Stop (Shift)", command=self.stop_playback)
        self.stop_button.pack()

        # key shortcuts or hotkeys tab to run and shift to stop incase the recorded log list is huge u can just stop/run it using these hotkeys 
        keyboard.add_hotkey("tab", self.play_clicks)
        keyboard.add_hotkey("shift", self.stop_playback)

        pyautogui.PAUSE = 0  # found this shit to remove built-in pyautogui delays, interesting stuff from stackflow love it

    def start_logging(self):
        self.log_button.config(text="Click the location")
        thread = threading.Thread(target=self.wait_for_click, daemon=True)
        thread.start()

    def wait_for_click(self):
        mouse.wait(button='left')
        x, y = pyautogui.position()
        self.root.after(0, lambda: self.log_position(x, y))

    def log_position(self, x, y):
        self.log_button.config(text="Log Mouse Position")
        try:
            delay = int(self.delay_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid delay input. Enter a number.")
            return

        click_type = self.click_type.get()
        self.clicks.append((x, y, click_type, delay))
        self.click_listbox.insert(tk.END, f"{click_type.capitalize()} Click at ({x}, {y}) after {delay}ms")

    def clear_table(self):
        self.clicks.clear()
        self.click_listbox.delete(0, tk.END)
        self.hide_highlights() 

    def show_context_menu(self, event):
        try:
            self.click_listbox.selection_clear(0, tk.END)
            self.click_listbox.selection_set(self.click_listbox.nearest(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except Exception:
            pass

    def delete_selected(self):
        try:
            selected_index = self.click_listbox.curselection()[0]
            del self.clicks[selected_index]
            self.click_listbox.delete(selected_index)
        except IndexError:
            pass

    def edit_selected(self):
        try:
            selected_index = self.click_listbox.curselection()[0]
            old_x, old_y, old_type, old_delay = self.clicks[selected_index]
            new_delay = simpledialog.askinteger("Edit Delay", "Enter new delay (ms):", initialvalue=old_delay)
            if new_delay is not None:
                self.clicks[selected_index] = (old_x, old_y, old_type, new_delay)
                self.click_listbox.delete(selected_index)
                self.click_listbox.insert(selected_index, f"{old_type.capitalize()} Click at ({old_x}, {old_y}) after {new_delay}ms")
        except IndexError:
            pass

    def play_clicks(self):
        if not self.clicks:
            messagebox.showwarning("Warning", "No clicks recorded!")
            return

        self.running = True

        def run_clicks():
            for i, (x, y, click_type, delay) in enumerate(self.clicks):
                if not self.running:  # Stop playback if interrupted
                    break

                self.click_listbox.selection_clear(0, tk.END)
                self.click_listbox.selection_set(i)
                self.click_listbox.activate(i)

                time.sleep(delay / 1000)  # Wait before sending the click

                if click_type == "single":
                    pyautogui.click(x, y)
                elif click_type == "double":
                    pyautogui.doubleClick(x, y)

            self.click_listbox.selection_clear(0, tk.END)
            self.running = False  # Ensure flag resets after playback

        threading.Thread(target=run_clicks, daemon=True).start()

    def stop_playback(self):
        self.running = False
        print("Playback stopped.")

    def show_highlights(self):
        """ function to Show transparent highlights over recorded click positionss """
        self.hide_highlights()  # Remove previous highlights

        for idx, (x, y, _, _) in enumerate(self.clicks):
            overlay = tk.Toplevel(self.root)
            overlay.overrideredirect(True)  # No window decorations
            overlay.geometry(f"30x30+{x-15}+{y-15}")  # Small circle size
            overlay.wm_attributes("-topmost", True)
            overlay.wm_attributes("-alpha", 0.5)  # Semi-transparent

            canvas = tk.Canvas(overlay, width=30, height=30, bg="red", highlightthickness=0)
            canvas.pack()
            canvas.create_oval(5, 5, 25, 25, fill="yellow")  # Draw circle
            canvas.create_text(15, 15, text=str(idx+1), font=("Arial", 12, "bold"), fill="black")  # Numbering

            self.overlays.append(overlay)

# function to remove highlight overlays 
    def hide_highlights(self):
        for overlay in self.overlays:
            overlay.destroy()
        self.overlays.clear()

# calling the functions
if __name__ == "__main__":
    root = tk.Tk()
    ClickRecorder(root)
    root.mainloop()
