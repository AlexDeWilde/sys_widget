import tkinter as tk
import threading
import psutil
import subprocess
import urllib.request
import json

class SysWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("System Stats Widget")
        self.overrideredirect(True) # Frameless window
        self.attributes("-topmost", True) # Always on top
        self.configure(bg="black")
        
        # Use Consolas so words and symbols render nicely
        self.font = ("Consolas", 14, "bold")
        self.fg_color = "#00BFFF" # Bright Blue / Deep Sky Blue
        
        # UI Elements
        self.container = tk.Frame(self, bg="black", padx=10, pady=5)
        self.container.pack()

        self.lbl_stats = tk.Label(self.container, text="Loading Stats...", bg="black", fg=self.fg_color, font=self.font)
        self.lbl_stats.pack(side=tk.LEFT)
        
        # Allow moving window by dragging
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)
        
        # Context menu for closing
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Close", command=self.destroy)
        self.bind("<Button-3>", self.show_menu)

        self.update_stats_loop()
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def fetch_stats(self):
        # Fallbacks
        gpu_3d_str = "--"
        gpu_temp_str = "--"
        vram_pct_str = "--"
        
        # 1. GPU Temp, 3D Load and VRAM using nvidia-smi
        try:
            # CREATE_NO_WINDOW prevents the console window from popping up on Windows
            creationflags = 0
            if hasattr(subprocess, 'CREATE_NO_WINDOW'):
                creationflags = subprocess.CREATE_NO_WINDOW
                
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
                encoding="utf-8", creationflags=creationflags
            ).strip()
            
            parts = output.split(",")
            if len(parts) == 4:
                gpu_3d = int(parts[0].strip())
                gpu_temp = int(parts[1].strip())
                mem_used = int(parts[2].strip())
                mem_total = int(parts[3].strip())
                vram_pct = int((mem_used / mem_total) * 100)
                
                gpu_3d_str = f"{gpu_3d:02d}"
                gpu_temp_str = f"{gpu_temp:02d}"
                vram_pct_str = f"{vram_pct:02d}"
        except Exception:
            pass
            
        # 2. RAM using psutil
        try:
            ram_pct = int(psutil.virtual_memory().percent)
            ram_pct_str = f"{ram_pct:02d}"
        except Exception:
            ram_pct_str = "--"
            
        # 3. Ollama Status
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/ps", method="GET")
            with urllib.request.urlopen(req, timeout=0.5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    models = data.get("models", [])
                    if models:
                        # Assuming the first model is the active one
                        ollama_status = models[0].get("name", "unknown")
                    else:
                        ollama_status = "OFF"
                else:
                    ollama_status = "OFF"
        except Exception:
            # If connection fails or times out, assume Ollama is not running or no models loaded
            ollama_status = "OFF"
            
        # Format: 3D: xx% | TMP: xxC | VRAM: xx% | RAM: yy% | Ollama: [model]/OFF
        text = f"3D: {gpu_3d_str}% | TMP: {gpu_temp_str}C | VRAM: {vram_pct_str}% | RAM: {ram_pct_str}% | Ollama: {ollama_status}"
        
        # Update UI in main thread
        self.after(0, lambda: self.lbl_stats.config(text=text))
        
        # Schedule next update in 1 second
        self.after(1000, self.update_stats_loop)

    def update_stats_loop(self):
        # Run fetching in a thread so the UI doesn't freeze during subprocess/http calls
        threading.Thread(target=self.fetch_stats, daemon=True).start()

if __name__ == "__main__":
    app = SysWidget()
    app.mainloop()
