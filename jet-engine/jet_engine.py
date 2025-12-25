import tkinter as tk
from tkinter import messagebox
import subprocess
import ctypes
import sys
import os
import threading
import time
import re

# Configuración Visual (Cyberpunk Minimalista)
COLOR_BG = "#0a0a0a"       # Negro profundo
COLOR_ACCENT = "#00e5ff"   # Cyan Neon
COLOR_DANGER = "#ff2a00"   # Rojo Lava
FONT_MAIN = ("Segoe UI", 12)
FONT_HEADER = ("Segoe UI", 16, "bold")

class JetEngineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JET ENGINE v4.0")
        self.root.geometry("350x250")
        self.root.configure(bg=COLOR_BG)
        self.root.overrideredirect(True) # Sin bordes
        self.root.attributes('-topmost', True) # Siempre visible
        self.root.attributes('-alpha', 0.95)

        self.is_turbo = False
        self.original_power_plan = None
        
        # Centrar ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - 175
        y = (screen_height // 2) - 125
        self.root.geometry(f"+{x}+{y}")

        # --- UI CLASICA ---
        
        # Header (Barra de arrastre)
        self.header_frame = tk.Frame(self.root, bg="#1a1a1a", height=30)
        self.header_frame.pack(fill="x")
        self.header_frame.bind("<Button-1>", self.start_move)
        self.header_frame.bind("<B1-Motion>", self.do_move)
        
        lbl_title = tk.Label(self.header_frame, text="JET ENGINE // SYSTEM OPTIMIZER", font=("Consolas", 10), fg="white", bg="#1a1a1a")
        lbl_title.pack(side="left", padx=10)
        lbl_title.bind("<Button-1>", self.start_move)
        lbl_title.bind("<B1-Motion>", self.do_move)

        btn_close = tk.Label(self.header_frame, text="X", font=("Arial", 10, "bold"), fg="white", bg="#1a1a1a", cursor="hand2")
        btn_close.pack(side="right", padx=10)
        btn_close.bind("<Button-1>", self.safe_exit)

        # Boton Minimizar [ _ ]
        btn_min = tk.Label(self.header_frame, text="_", font=("Arial", 10, "bold"), fg="white", bg="#1a1a1a", cursor="hand2")
        btn_min.pack(side="right", padx=5)
        btn_min.bind("<Button-1>", self.toggle_minimize)

        # Cuerpo Principal
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.lbl_status = tk.Label(self.main_frame, text="SYSTEM: STANDBY", font=FONT_HEADER, fg="white", bg=COLOR_BG)
        self.lbl_status.pack(pady=10)

        self.btn_toggle = tk.Button(self.main_frame, text="ENGAGE TURBO", font=("Segoe UI", 14, "bold"),
                                   bg=COLOR_ACCENT, fg="black", activebackground="white",
                                   command=self.toggle_mode, bd=0, width=20, height=2, cursor="hand2")
        self.btn_toggle.pack(pady=20)
        
        self.lbl_info = tk.Label(self.main_frame, text="Kills Explorer.exe\nStops Background Services\nHigh Performance Power Plan", 
                                font=("Consolas", 8), fg="#666666", bg=COLOR_BG)
        self.lbl_info.pack(pady=5)
        
        # Mini Widget (Oculto al inicio)
        self.mini_widget = None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def safe_exit(self, event=None):
        if self.is_turbo:
            self.deactivate_turbo()
        self.root.destroy()
        sys.exit()

    def run_cmd(self, cmd):
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def toggle_mode(self):
        if not self.is_turbo:
            self.activate_turbo()
        else:
            self.deactivate_turbo()

    def toggle_minimize(self, event=None):
        self.root.withdraw() # Ocultar ventana principal
        self.show_mini_widget()

    def show_mini_widget(self):
        self.mini_widget = tk.Toplevel(self.root)
        self.mini_widget.title("Mini Jet")
        self.mini_widget.geometry("60x60+50+50") # Pequeño cuadrado
        self.mini_widget.configure(bg=COLOR_ACCENT if not self.is_turbo else COLOR_DANGER)
        self.mini_widget.overrideredirect(True)
        self.mini_widget.attributes('-topmost', True)
        self.mini_widget.attributes('-alpha', 0.8)
        
        # Texto central
        lbl = tk.Label(self.mini_widget, text="JET", font=("Impact", 12), 
                      bg=COLOR_ACCENT if not self.is_turbo else COLOR_DANGER,
                      fg="black" if not self.is_turbo else "white")
        lbl.pack(expand=True)
        
        # Eventos del Mini Widget
        lbl.bind("<Button-1>", self.min_start_move)
        lbl.bind("<B1-Motion>", self.min_do_move)
        lbl.bind("<Double-Button-1>", self.restore_main) # Doble click restaura
        
        self.mini_widget_x = 0
        self.mini_widget_y = 0

    def min_start_move(self, event):
        self.mini_widget_x = event.x
        self.mini_widget_y = event.y

    def min_do_move(self, event):
        deltax = event.x - self.mini_widget_x
        deltay = event.y - self.mini_widget_y
        x = self.mini_widget.winfo_x() + deltax
        y = self.mini_widget.winfo_y() + deltay
        self.mini_widget.geometry(f"+{x}+{y}")

    def restore_main(self, event=None):
        if self.mini_widget:
            self.mini_widget.destroy()
        self.root.deiconify() # Mostrar ventana principal

    def activate_turbo(self):
        # 1. Guardar plan de energia actual
        try:
            output = subprocess.check_output("powercfg /getactivescheme", shell=True).decode()
            match = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', output)
            if match:
                self.original_power_plan = match.group(0)
        except:
            pass
            
        # 2. Buscar el MEJOR plan disponible
        target_plan = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" # Default High Perf
        try:
            list_output = subprocess.check_output("powercfg /list", shell=True).decode()
            ultimate_match = re.search(r'([0-9a-fA-F\-]{36})\s+\(.*\b(Ultimate|ChrisTitus)\b.*\)', list_output, re.IGNORECASE)
            if ultimate_match:
                target_plan = ultimate_match.group(1)
            
            self.run_cmd(f"powercfg /setactive {target_plan}")
        except:
            self.run_cmd(f"powercfg /setactive {target_plan}")
 
        # 3. Detener Servicios
        services_to_kill = ["WSearch", "SysMain", "DiagTrack", "Spooler", "Themes", "TabletInputService"]
        for service in services_to_kill:
            self.run_cmd(f"net stop {service}")

        # 4. Optimizaciones de Kernel
        try: ctypes.windll.winmm.timeBeginPeriod(1)
        except: pass
        self.run_cmd("ipconfig /flushdns")

        # 5. Focus Assist & Reg Tweaks v4.0
        try:
            key = r"Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"
            self.run_cmd('reg add "HKCU\\' + key + '" /v "NOC_GLOBAL_SETTING_TOASTS_ENABLED_DWORD" /t REG_DWORD /d 0 /f')
            nk = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            self.run_cmd(f'reg add "{nk}" /v "NetworkThrottlingIndex" /t REG_DWORD /d 0xFFFFFFFF /f')
            self.run_cmd(f'reg add "{nk}" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f')
        except: pass

        # 6. Matar Explorer
        self.run_cmd("taskkill /f /im explorer.exe")
        
        # 7. Auto-Boost Prioridad + RAM Trim (Async)
        threading.Thread(target=self.delayed_boost, daemon=True).start()

        # UI Update
        self.is_turbo = True
        self.lbl_status.config(text="⚡ GOD MODE ACTIVE", fg=COLOR_DANGER)
        self.btn_toggle.config(text="DISENGAGE", bg=COLOR_DANGER, fg="white")
        self.lbl_info.config(text="CPU Priority: HIGH | RAM: Optimized | Net: Unprobed")
        
    def delayed_boost(self):
        # RAM Trim
        hogs = ["chrome", "discord", "spotify", "msedge", "steamwebhelper", "firefox"]
        self.run_cmd("powershell -Command \"Get-Process " + ", ".join(hogs) + " -ErrorAction SilentlyContinue | ForEach-Object { $_.MinWorkingSet = [System.IntPtr]::Zero }\"")
        
        # Priority Boost
        time.sleep(5)
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            proc = ctypes.windll.kernel32.OpenProcess(0x0200, False, pid)
            if proc:
                ctypes.windll.kernel32.SetPriorityClass(proc, 0x00000080) # HIGH
                ctypes.windll.kernel32.CloseHandle(proc)
        except: pass

    def deactivate_turbo(self):
        # Restaurar todo
        os.system("start explorer.exe")
        try: ctypes.windll.winmm.timeEndPeriod(1)
        except: pass
        for s in ["WSearch", "SysMain", "Spooler", "Themes", "TabletInputService"]: self.run_cmd(f"net start {s}")
        
        try:
             self.run_cmd(r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" /v "NOC_GLOBAL_SETTING_TOASTS_ENABLED_DWORD" /t REG_DWORD /d 1 /f')
             nk = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
             self.run_cmd(f'reg add "{nk}" /v "NetworkThrottlingIndex" /t REG_DWORD /d 10 /f')
             self.run_cmd(f'reg add "{nk}" /v "SystemResponsiveness" /t REG_DWORD /d 20 /f')
        except: pass

        if self.original_power_plan:
            self.run_cmd(f"powercfg /setactive {self.original_power_plan}")

        # UI Update
        self.is_turbo = False
        self.lbl_status.config(text="SYSTEM: STANDBY", fg="white")
        self.btn_toggle.config(text="ENGAGE TURBO", bg=COLOR_ACCENT, fg="black")
        self.lbl_info.config(text="Kills Explorer.exe\nStops Background Services\nHigh Performance Power Plan")
        
        # Reset visual
        self.root.configure(bg=COLOR_BG)
        self.main_frame.configure(bg=COLOR_BG)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if is_admin():
        root = tk.Tk()
        app = JetEngineApp(root)
        root.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
