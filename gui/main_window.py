"""
Main GUI Window - Tkinter based.
NO BUSINESS LOGIC - only display and user input routing.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.controller import AppController, ControllerEvent

class MainWindow:
    """Main application window."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sora Automation Tool v1.0")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Controller
        self.controller = AppController()
        self.controller.add_listener(self._on_event)
        
        # Build UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_panes()
        self._create_status_bar()
        
        # Initial refresh
        self._refresh_all()
        
        # Cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Job...", command=self._show_add_job_dialog)
        file_menu.add_command(label="Add Account...", command=self._show_add_account_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        
        # Engine menu
        engine_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Engine", menu=engine_menu)
        engine_menu.add_command(label="Start", command=self._cmd_start)
        engine_menu.add_command(label="Pause", command=self._cmd_pause)
        engine_menu.add_command(label="Stop", command=self._cmd_stop)
        engine_menu.add_separator()
        engine_menu.add_command(label="⚠️ KILL SWITCH", command=self._cmd_kill_switch)

    def _create_toolbar(self):
        """Create toolbar with controls."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Control buttons
        self.btn_start = ttk.Button(toolbar, text="▶ Start", command=self._cmd_start)
        self.btn_start.pack(side=tk.LEFT, padx=2)
        
        self.btn_pause = ttk.Button(toolbar, text="⏸ Pause", command=self._cmd_pause)
        self.btn_pause.pack(side=tk.LEFT, padx=2)
        
        self.btn_stop = ttk.Button(toolbar, text="⏹ Stop", command=self._cmd_stop)
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Kill switch (red button)
        self.btn_kill = ttk.Button(toolbar, text="🔴 KILL SWITCH", command=self._cmd_kill_switch)
        self.btn_kill.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Config toggles
        self.var_real_api = tk.BooleanVar(value=False)
        self.chk_real_api = ttk.Checkbutton(
            toolbar, text="Real API", variable=self.var_real_api,
            command=self._toggle_real_api
        )
        self.chk_real_api.pack(side=tk.LEFT, padx=5)
        
        self.var_shadow = tk.BooleanVar(value=True)
        self.chk_shadow = ttk.Checkbutton(
            toolbar, text="Shadow Mode", variable=self.var_shadow,
            command=self._toggle_shadow_mode
        )
        self.chk_shadow.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Quick add
        ttk.Button(toolbar, text="+ Job", command=self._show_add_job_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="+ Account", command=self._show_add_account_dialog).pack(side=tk.LEFT, padx=2)

    def _create_main_panes(self):
        """Create main content area with panes."""
        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top pane: Jobs + Accounts
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=3)
        
        top_paned = ttk.PanedWindow(top_frame, orient=tk.HORIZONTAL)
        top_paned.pack(fill=tk.BOTH, expand=True)
        
        # Jobs panel
        jobs_frame = ttk.LabelFrame(top_paned, text="Job Queue")
        top_paned.add(jobs_frame, weight=3)
        self._create_jobs_tree(jobs_frame)
        
        # Accounts panel
        accounts_frame = ttk.LabelFrame(top_paned, text="Accounts")
        top_paned.add(accounts_frame, weight=1)
        self._create_accounts_tree(accounts_frame)
        
        # Bottom pane: Logs
        log_frame = ttk.LabelFrame(paned, text="Logs")
        paned.add(log_frame, weight=1)
        self._create_log_panel(log_frame)

    def _create_jobs_tree(self, parent):
        """Create job queue treeview."""
        columns = ("id", "status", "prompt", "retry", "account", "next_retry")
        self.jobs_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
        self.jobs_tree.heading("id", text="Job ID")
        self.jobs_tree.heading("status", text="Status")
        self.jobs_tree.heading("prompt", text="Prompt")
        self.jobs_tree.heading("retry", text="Retry")
        self.jobs_tree.heading("account", text="Account")
        self.jobs_tree.heading("next_retry", text="Next Retry")
        
        self.jobs_tree.column("id", width=80)
        self.jobs_tree.column("status", width=120)
        self.jobs_tree.column("prompt", width=200)
        self.jobs_tree.column("retry", width=50)
        self.jobs_tree.column("account", width=100)
        self.jobs_tree.column("next_retry", width=80)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.jobs_tree.yview)
        self.jobs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.jobs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_accounts_tree(self, parent):
        """Create accounts treeview."""
        columns = ("id", "status", "quota", "cooldown")
        self.accounts_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
        self.accounts_tree.heading("id", text="Account")
        self.accounts_tree.heading("status", text="Status")
        self.accounts_tree.heading("quota", text="Quota")
        self.accounts_tree.heading("cooldown", text="Cooldown")
        
        self.accounts_tree.column("id", width=100)
        self.accounts_tree.column("status", width=80)
        self.accounts_tree.column("quota", width=60)
        self.accounts_tree.column("cooldown", width=70)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.accounts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_log_panel(self, parent):
        """Create log output panel."""
        self.log_text = scrolledtext.ScrolledText(parent, height=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    # ===== Event Handlers =====
    def _on_event(self, event: ControllerEvent):
        """Handle events from Controller (called from background thread)."""
        # Schedule UI update on main thread
        self.root.after(0, lambda: self._handle_event(event))

    def _handle_event(self, event: ControllerEvent):
        """Process event on main thread."""
        if event.event_type == "jobs_updated":
            self._refresh_jobs()
        elif event.event_type == "accounts_updated":
            self._refresh_accounts()
        elif event.event_type == "log":
            self._append_log(event.data)
        elif event.event_type == "state_changed":
            self._refresh_status()

    def _refresh_all(self):
        """Refresh all views."""
        self._refresh_jobs()
        self._refresh_accounts()
        self._refresh_config()
        self._refresh_status()

    def _refresh_jobs(self):
        """Refresh job queue view."""
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)
        for job in self.controller.get_jobs():
            self.jobs_tree.insert("", tk.END, values=(
                job["id"], job["status"], job["prompt"],
                job["retry_count"], job["account"], job["next_retry"]
            ))

    def _refresh_accounts(self):
        """Refresh accounts view."""
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
        for acc in self.controller.get_accounts():
            self.accounts_tree.insert("", tk.END, values=(
                acc["id"], acc["status"], acc["quota"], acc["cooldown"]
            ))

    def _refresh_config(self):
        """Refresh config toggles."""
        cfg = self.controller.get_config_state()
        self.var_real_api.set(cfg["use_real_api"])
        self.var_shadow.set(cfg["shadow_mode"])

    def _refresh_status(self):
        """Refresh status bar."""
        cfg = self.controller.get_config_state()
        state = cfg["engine_state"].upper()
        api_mode = "REAL API" if cfg["use_real_api"] else "MOCK"
        shadow = " (Shadow)" if cfg["shadow_mode"] and cfg["use_real_api"] else ""
        self.status_bar.config(text=f"Engine: {state} | Mode: {api_mode}{shadow}")

    def _append_log(self, message: str):
        """Append message to log panel."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ===== Commands =====
    def _cmd_start(self):
        self.controller.start()
        self._refresh_status()

    def _cmd_pause(self):
        self.controller.pause()
        self._refresh_status()

    def _cmd_stop(self):
        self.controller.stop()
        self._refresh_status()

    def _cmd_kill_switch(self):
        if messagebox.askyesno("Kill Switch", "⚠️ This will STOP all operations and DISABLE real API.\n\nContinue?"):
            self.controller.activate_kill_switch()
            self._refresh_config()
            self._refresh_status()

    def _toggle_real_api(self):
        self.controller.set_use_real_api(self.var_real_api.get())
        self._refresh_status()

    def _toggle_shadow_mode(self):
        self.controller.set_shadow_mode(self.var_shadow.get())
        self._refresh_status()

    def _show_add_job_dialog(self):
        """Show dialog to add new job."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Job")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Prompt:").pack(pady=5)
        prompt_entry = ttk.Entry(dialog, width=50)
        prompt_entry.pack(pady=5)
        prompt_entry.focus()
        
        def submit():
            prompt = prompt_entry.get().strip()
            if prompt:
                self.controller.add_job(prompt)
                dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=submit).pack(pady=10)
        prompt_entry.bind("<Return>", lambda e: submit())

    def _show_add_account_dialog(self):
        """Show dialog to add new account."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Account")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Account ID:").pack(pady=5)
        id_entry = ttk.Entry(dialog, width=50)
        id_entry.pack(pady=5)
        id_entry.focus()
        
        def submit():
            acc_id = id_entry.get().strip()
            if acc_id:
                self.controller.add_account(acc_id)
                dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=submit).pack(pady=10)
        id_entry.bind("<Return>", lambda e: submit())

    def _on_close(self):
        """Handle window close."""
        self.controller.stop()
        self.root.destroy()

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
