import tkinter as tk
from tkinter import ttk
import time

class ProgressTracker:
    def __init__(self, parent_frame: tk.Frame, total_records: int):
        self.progress_frame = tk.Frame(parent_frame)
        self.progress_frame.pack(side="bottom", fill=tk.BOTH)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.progress_bar.pack(padx=10, pady=10)
        
        self.time_label = tk.Label(
            self.progress_frame,
            text="Estimated Time: Calculating...",
            bg='white'
        )
        self.time_label.pack(padx=10, pady=5)
        
        self.start_time = time.time()
        self.progress_bar["maximum"] = total_records
        
    def update(self, current_index: int, total_records: int):
        self.progress_bar["value"] = current_index
        elapsed_time = time.time() - self.start_time
        avg_time_per_record = elapsed_time / current_index
        remaining_records = total_records - current_index
        est_time_remaining = avg_time_per_record * remaining_records
        
        minutes, seconds = divmod(est_time_remaining, 60)
        self.time_label.config(
            text=f"Estimated Time: {int(minutes)}m {int(seconds)}s remaining"
        )
        self.progress_frame.update_idletasks()
    
    def destroy(self):
        self.progress_frame.destroy()
