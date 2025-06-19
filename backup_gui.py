import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import schedule
import time
from datetime import datetime
from backup_utils import (
    compress_and_encrypt_folder,
    upload_to_drive_stream,
    log_backup,
    list_backups,
    restore_backup
)
from dotenv import load_dotenv

load_dotenv("backup.env")

class BackupApp:
    def __init__(self, master):
        self.master = master
        master.title("AutoBackupPro Cloud")
        master.geometry("600x450")
        master.resizable(False, False)
        master.configure(bg="#2e2e2e")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#2e2e2e", foreground="#ffffff", fieldbackground="#3a3a3a", font=('Arial', 10))
        style.configure("TButton", padding=6, relief="flat")
        style.configure("TEntry", fieldbackground="#3a3a3a")
        style.configure("TLabel", background="#2e2e2e", foreground="#ffffff")
        style.configure("Horizontal.TProgressbar", troughcolor="#3a3a3a", background="#4caf50", thickness=20)

        self.folder = tk.StringVar()

        folder_frame = ttk.Frame(master, padding="10")
        folder_frame.pack(fill="x")
        ttk.Label(folder_frame, text="Folder to Backup:").pack(side=tk.LEFT)
        ttk.Entry(folder_frame, textvariable=self.folder, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)

        schedule_frame = ttk.LabelFrame(master, text="Backup Schedule", padding="10")
        schedule_frame.pack(padx=10, pady=10, fill="x")
        self.schedule_var = tk.StringVar(value="once")
        ttk.Radiobutton(schedule_frame, text="Backup Once Now", variable=self.schedule_var, value="once").pack(anchor="w")
        ttk.Radiobutton(schedule_frame, text="Daily (22:00)", variable=self.schedule_var, value="daily").pack(anchor="w")
        ttk.Radiobutton(schedule_frame, text="Weekly (Sunday 22:00)", variable=self.schedule_var, value="weekly").pack(anchor="w")

        btn_frame = ttk.Frame(master, padding="5")
        btn_frame.pack()
        ttk.Button(btn_frame, text="Start Backup", command=self.start_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop Backup", command=self.stop_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Run Backup Now", command=self.run_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Restore Backup", command=self.restore_prompt).pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(master, orient="horizontal", mode="determinate", length=550)
        self.progress.pack(padx=10, pady=5)

        self.log = tk.Text(master, height=10, width=72, bg="#1e1e1e", fg="#ffffff")
        self.log.pack(padx=10, pady=10)

        self.running = False

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder.set(folder)

    def start_backup(self):
        if not self.folder.get():
            messagebox.showwarning("Warning", "Please select a folder to backup.")
            return
        self.running = True
        self.log_msg("[INFO] Backup scheduler started.")
        if self.schedule_var.get() == "once":
            self.run_backup()
        elif self.schedule_var.get() == "daily":
            schedule.every().day.at("22:00").do(self.run_backup)
        elif self.schedule_var.get() == "weekly":
            schedule.every().sunday.at("22:00").do(self.run_backup)
        if self.schedule_var.get() != "once":
            threading.Thread(target=self.run_schedule, daemon=True).start()

    def stop_backup(self):
        self.running = False
        schedule.clear()
        self.log_msg("[INFO] Backup scheduler stopped.")

    def run_schedule(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def run_backup(self):
        self.progress["value"] = 0
        self.log_msg("[INFO] Running backup...")
        threading.Thread(target=self._backup_process, daemon=True).start()

    def _backup_process(self):
        encrypted_data = compress_and_encrypt_folder(self.folder.get())
        self.progress["value"] = 50
        self.master.update_idletasks()

        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
        link = upload_to_drive_stream(encrypted_data, filename)

        self.progress["value"] = 100
        self.log_msg(f"[INFO] Uploaded. Link: {link}")
        log_backup(filename, link)
        self.log_msg("[INFO] Backup logged.")

    def restore_prompt(self):
        backups = list_backups()
        if not backups:
            messagebox.showinfo("Restore", "No backups found.")
            return

        sel = tk.Toplevel(self.master)
        sel.title("Select Backup to Restore")
        sel.configure(bg="#2e2e2e")
        sel.geometry("400x300")
        lb = tk.Listbox(sel, bg="#1e1e1e", fg="#ffffff")
        lb.pack(fill="both", expand=True, padx=10, pady=10)

        for i, (title, id_) in enumerate(backups):
            lb.insert(i, title)

        def do_restore():
            sel_index = lb.curselection()
            if sel_index:
                file_id = backups[sel_index[0]][1]
                dest = filedialog.askdirectory(title="Select destination folder")
                if dest:
                    self.progress["value"] = 0
                    self.log_msg("[INFO] Starting restore process...")
                    threading.Thread(target=self._restore_process, args=(file_id, dest), daemon=True).start()
            sel.destroy()

        ttk.Button(sel, text="Restore Selected", command=do_restore).pack(pady=5)

    def _restore_process(self, file_id, dest):
        restore_backup(file_id, dest, progress_callback=self.update_progress)
        self.log_msg("[INFO] Backup restored successfully.")

    def update_progress(self, value):
        self.progress["value"] = value
        self.master.update_idletasks()

    def log_msg(self, msg):
        self.log.insert(tk.END, f"{msg}\n")
        self.log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
