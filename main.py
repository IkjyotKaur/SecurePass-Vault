import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import hashlib
import os
import time
from cryptography.fernet import Fernet


# ==========================================
# 1. MULTI-CIPHER ENGINE
# ==========================================
class CipherEngine:
    @staticmethod
    def caesar(text, key, mode='enc'):
        try:
            shift = int(key) if mode == 'enc' else -int(key)
            res = ""
            for char in text:
                if char.isalpha():
                    start = ord('A') if char.isupper() else ord('a')
                    res += chr((ord(char) - start + shift) % 26 + start)
                else:
                    res += char
            return res
        except:
            return "Error"

    @staticmethod
    def affine(text, key_str, mode='enc'):
        try:
            a, b = map(int, key_str.split(','))
            m = 26

            def mod_inverse(a, m):
                for x in range(1, m):
                    if (((a % m) * (x % m)) % m == 1):
                        return x
                return 1

            res = ""
            if mode == 'enc':
                for char in text:
                    if char.isalpha():
                        s = ord('A') if char.isupper() else ord('a')
                        res += chr((a * (ord(char) - s) + b) % m + s)
                    else:
                        res += char
            else:
                a_inv = mod_inverse(a, m)
                for char in text:
                    if char.isalpha():
                        s = ord('A') if char.isupper() else ord('a')
                        res += chr((a_inv * (ord(char) - s - b)) % m + s)
                    else:
                        res += char
            return res
        except:
            return "Error"

    @staticmethod
    def rc4(data, key):
        try:
            if not key:
                return "Error"
            s = list(range(256))
            j = 0
            out = []

            for i in range(256):
                j = (j + s[i] + ord(key[i % len(key)])) % 256
                s[i], s[j] = s[j], s[i]

            i = j = 0
            for char in data:
                i = (i + 1) % 256
                j = (j + s[i]) % 256
                s[i], s[j] = s[j], s[i]
                out.append(chr(ord(char) ^ s[(s[i] + s[j]) % 256]))
            return "".join(out)
        except:
            return "Error"


# ==========================================
# 2. SECUREPASS VAULT APPLICATION
# ==========================================
class SecureVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecurePass Vault")
        self.root.geometry("1280x820")
        self.root.minsize(1200, 780)
        self.root.configure(bg="#0f172a")

        self.currentuser = None
        self.datafile = ""
        self.authfile = "vaultauth.bin"
        self.temppassword = ""
        self.currentpage = "home"
        self.lastlogininfo = "Current session"

        self.showloginpasswordvar = tk.BooleanVar(value=False)
        self.showaddpasswordvar = tk.BooleanVar(value=False)

        self.signinusernamevar = tk.StringVar()
        self.signinpasswordvar = tk.StringVar()

        self.signupusernamevar = tk.StringVar()
        self.signuppasswordvar = tk.StringVar()
        self.signupconfirmvar = tk.StringVar()

        self.addsitevar = tk.StringVar()
        self.addaccountvar = tk.StringVar()
        self.addpasswordvar = tk.StringVar()
        self.searchvar = tk.StringVar()

        self.visiblepasswordrows = {}

        self.colors = {
            "bg": "#0f172a",
            "card": "#1e293b",
            "card2": "#243447",
            "card3": "#2b3c52",
            "accentblue": "#38bdf8",
            "accentpurple": "#8b5cf6",
            "success": "#22c55e",
            "danger": "#ef4444",
            "warning": "#f59e0b",
            "text": "#e2e8f0",
            "muted": "#94a3b8",
            "footer": "#64748b",
            "entrybg": "#162133",
            "border": "#334155"
        }

        self.primary_button_width = 18
        self.primary_button_font = ("Segoe UI", 11, "bold")
        self.primary_button_padx = 18
        self.primary_button_pady = 10

        if not os.path.exists("vault.key"):
            with open("vault.key", "wb") as f:
                f.write(Fernet.generate_key())

        with open("vault.key", "rb") as f:
            self.fernet = Fernet(f.read())

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.appshell = tk.Frame(self.root, bg=self.colors["bg"])
        self.appshell.grid(row=0, column=0, sticky="nsew")
        self.appshell.grid_rowconfigure(0, weight=1)
        self.appshell.grid_columnconfigure(0, weight=1)

        self.maincontainer = tk.Frame(self.appshell, bg=self.colors["bg"])
        self.maincontainer.grid(row=0, column=0, sticky="nsew")

        self.footer = tk.Label(
            self.appshell,
            text="Designed & Developed by Ikjyot Kaur",
            bg=self.colors["bg"],
            fg=self.colors["footer"],
            font=("Segoe UI", 9)
        )
        self.footer.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.notificationhost = tk.Frame(self.root, bg=self.colors["bg"])
        self.notificationhost.place(relx=1.0, y=18, anchor="ne")

        self.showhomescreen()

    # ==========================================
    # COMMON UI HELPERS
    # ==========================================
    def clearscreen(self):
        for widget in self.maincontainer.winfo_children():
            widget.destroy()

    def notify(self, message, level="success"):
        color = self.colors["success"] if level == "success" else self.colors["danger"] if level == "error" else self.colors["accentpurple"]
        icon = "✅" if level == "success" else "❌" if level == "error" else "🔔"

        box = tk.Frame(
            self.notificationhost,
            bg=self.colors["card"],
            highlightbackground=color,
            highlightthickness=2
        )
        box.pack(anchor="e", padx=10, pady=5)

        tk.Label(
            box,
            text=f"{icon}  {message}",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=10
        ).pack()

        self.root.after(2400, box.destroy)

    def createcard(self, parent, width=None, height=None, border=None):
        card = tk.Frame(
            parent,
            bg=self.colors["card"],
            highlightbackground=border if border else self.colors["border"],
            highlightthickness=1,
            bd=0
        )
        if width and height:
            card.configure(width=width, height=height)
            card.pack_propagate(False)
        return card

    def addhovereffect(self, widget, normalbg, hoverbg):
        widget.bind("<Enter>", lambda e: widget.configure(bg=hoverbg))
        widget.bind("<Leave>", lambda e: widget.configure(bg=normalbg))

    def createtitle(self, parent, title, subtitle=None):
        tk.Label(
            parent,
            text=title,
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI", 24, "bold")
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                parent,
                text=subtitle,
                bg=self.colors["bg"],
                fg=self.colors["muted"],
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(4, 12))

    def createentry(self, parent, textvariable=None, show=None):
        entry = tk.Entry(
            parent,
            textvariable=textvariable,
            bg=self.colors["entrybg"],
            fg=self.colors["text"],
            insertbackground=self.colors["accentblue"],
            relief="flat",
            font=("Segoe UI", 11),
            show=show
        )
        return entry

    def createbutton(self, parent, text, command, colorkey="accentblue", fg="#07131f", width=None):
        bg = self.colors[colorkey]
        hovermap = {
            "accentblue": "#0ea5e9",
            "accentpurple": "#7c3aed",
            "success": "#16a34a",
            "danger": "#dc2626"
        }
        hover = hovermap.get(colorkey, bg)

        btn = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=self.primary_button_font,
            padx=self.primary_button_padx,
            pady=self.primary_button_pady,
            cursor="hand2",
            width=width if width is not None else self.primary_button_width,
            anchor="center",
            relief="flat",
            bd=0
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def createsmallactionbutton(self, parent, text, command, colorkey="accentblue", width=10):
        bg = self.colors[colorkey]
        hovermap = {
            "accentblue": "#0ea5e9",
            "accentpurple": "#7c3aed",
            "success": "#16a34a",
            "danger": "#dc2626",
            "warning": "#d97706"
        }
        hover = hovermap.get(colorkey, bg)

        btn = tk.Label(
            parent,
            text=text,
            bg=bg,
            fg="white" if colorkey in ["danger", "warning"] else "#07131f",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=6,
            cursor="hand2",
            width=width
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def createnavbutton(self, parent, text, icon, pagekey):
        active = self.currentpage == pagekey
        bg = self.colors["card3"] if active else self.colors["card"]
        fg = self.colors["accentblue"] if active else self.colors["text"]
        border = self.colors["accentblue"] if active else self.colors["border"]

        btn = tk.Label(
            parent,
            text=f"  {icon}  {text}",
            bg=bg,
            fg=fg,
            anchor="w",
            font=("Segoe UI", 11, "bold" if active else "normal"),
            padx=14,
            pady=11,
            cursor="hand2",
            highlightbackground=border,
            highlightthickness=1
        )
        btn.bind("<Button-1>", lambda e: self.showdashboard(pagekey))
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.colors["card3"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def make_scrollable_page(self, parent):
        wrapper = tk.Frame(parent, bg=self.colors["bg"])
        wrapper.grid(row=0, column=1, sticky="nsew", padx=(18, 18), pady=16)
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            wrapper,
            bg=self.colors["bg"],
            highlightthickness=0,
            bd=0
        )
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        content = tk.Frame(canvas, bg=self.colors["bg"])
        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfigure(window_id, width=event.width)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        content.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return wrapper, canvas, content, scrollbar

    # ==========================================
    # HOME SCREEN
    # ==========================================
    def showhomescreen(self):
        self.currentpage = "home"
        self.clearscreen()

        wrapper = tk.Frame(self.maincontainer, bg=self.colors["bg"])
        wrapper.pack(fill="both", expand=True, padx=34, pady=30)
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_columnconfigure(1, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        left = tk.Frame(wrapper, bg=self.colors["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        right = tk.Frame(wrapper, bg=self.colors["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(18, 0))

        tk.Label(
            left,
            text="🛡 SecurePass Vault",
            bg=self.colors["bg"],
            fg=self.colors["accentblue"],
            font=("Segoe UI", 30, "bold")
        ).pack(anchor="w", pady=(100, 12))

        tk.Label(
            left,
            text="Secure. Simple. Reliable.",
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=2)

        tk.Label(
            left,
            text="A premium cyber-security inspired password manager for secure credential storage and retrieval.",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 11),
            justify="left"
        ).pack(anchor="w", pady=(10, 24))

        banner = self.createcard(left, width=520, height=210, border=self.colors["accentpurple"])
        banner.pack(anchor="w", pady=8)

        tk.Label(
            banner,
            text="🔐  SecurePass Protection Layer",
            bg=self.colors["card"],
            fg=self.colors["accentpurple"],
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 8))

        tk.Label(
            banner,
            text="• Multi-user registration and login\n"
                 "• Separate vault for every user\n"
                 "• Fernet, Caesar, Affine and RC4 encryption\n"
                 "• Secure clipboard copy and password retrieval\n"
                 "• Modern desktop interface for project demonstration",
            bg=self.colors["card"],
            fg=self.colors["text"],
            justify="left",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=18, pady=8)

        authcard = self.createcard(right, width=440, height=320, border=self.colors["accentblue"])
        authcard.pack(expand=True)
        authcard.pack_propagate(False)

        tk.Label(
            authcard,
            text="Welcome",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(34, 8))

        tk.Label(
            authcard,
            text="Choose an option to continue",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 11)
        ).pack(pady=(0, 20))

        self.createbutton(authcard, "Sign In", self.showsigninscreen).pack(pady=10)
        self.createbutton(authcard, "Sign Up", self.showsignupscreen, "accentpurple").pack(pady=10)

        tk.Label(
            authcard,
            text="Built for a clean college-project presentation and viva.",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(pady=(20, 0))

    # ==========================================
    # SIGN IN SCREEN
    # ==========================================
    def showsigninscreen(self):
        self.currentpage = "signin"
        self.clearscreen()

        body = tk.Frame(self.maincontainer, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=30, pady=30)

        card = self.createcard(body, width=500, height=430, border=self.colors["accentblue"])
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        tk.Label(card, text="Sign In", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 22, "bold")).pack(pady=(24, 8))

        tk.Label(card, text="Access your secure vault", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack()

        form = tk.Frame(card, bg=self.colors["card"])
        form.pack(fill="both", expand=True, padx=24, pady=18)

        tk.Label(form, text="Username", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 5))
        self.uentry = self.createentry(form, self.signinusernamevar)
        self.uentry.pack(fill="x", ipady=10, pady=(0, 12))

        tk.Label(form, text="Password", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 5))
        self.pentry = self.createentry(form, self.signinpasswordvar, show=None if self.showloginpasswordvar.get() else "*")
        self.pentry.pack(fill="x", ipady=10, pady=(0, 10))

        tk.Checkbutton(
            form,
            text="Show Password",
            variable=self.showloginpasswordvar,
            command=self.showsigninscreen,
            bg=self.colors["card"],
            fg=self.colors["text"],
            activebackground=self.colors["card"],
            activeforeground=self.colors["accentblue"],
            selectcolor=self.colors["entrybg"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 12))

        btnrow = tk.Frame(form, bg=self.colors["card"])
        btnrow.pack(fill="x", pady=(6, 10))

        self.createbutton(btnrow, "Login", self.dologin, "success").pack(side="left", padx=(0, 10))
        self.createbutton(btnrow, "Back to Home", self.showhomescreen, "accentpurple").pack(side="left")

        self.loginmsg = tk.Label(form, text="", bg=self.colors["card"], fg=self.colors["danger"], font=("Segoe UI", 10))
        self.loginmsg.pack(anchor="w", pady=10)

    # ==========================================
    # SIGN UP SCREEN
    # ==========================================
    def showsignupscreen(self):
        self.currentpage = "signup"
        self.clearscreen()

        if self.root.winfo_width() < 1200 or self.root.winfo_height() < 780:
            self.root.geometry("1200x780")

        body = tk.Frame(self.maincontainer, bg=self.colors["bg"])
        body.pack(fill="both", expand=True, padx=30, pady=30)

        card = self.createcard(body, width=540, height=460, border=self.colors["accentpurple"])
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        tk.Label(
            card,
            text="Create Account",
            bg=self.colors["card"],
            fg=self.colors["text"],
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(24, 10))

        form = tk.Frame(card, bg=self.colors["card"])
        form.pack(fill="both", expand=True, padx=28, pady=(8, 24))

        tk.Label(
            form,
            text="Username",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(6, 4))

        self.uentry = self.createentry(form, self.signupusernamevar)
        self.uentry.pack(fill="x", ipady=10, pady=(0, 14))

        tk.Label(
            form,
            text="Password",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 4))

        self.pentry = self.createentry(form, self.signuppasswordvar, show="*")
        self.pentry.pack(fill="x", ipady=10, pady=(0, 14))

        tk.Label(
            form,
            text="Confirm Password",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 4))

        self.confirmentry = self.createentry(form, self.signupconfirmvar, show="*")
        self.confirmentry.pack(fill="x", ipady=10, pady=(0, 20))

        btnsection = tk.Frame(form, bg=self.colors["card"])
        btnsection.pack(fill="x", pady=(6, 0))

        self.createbutton(btnsection, "Create Account", self.doreg, "accentblue").pack(anchor="w", pady=(0, 14))
        self.createbutton(btnsection, "Back to Home", self.showhomescreen, "accentpurple").pack(anchor="w")

        self.loginmsg = tk.Label(
            form,
            text="",
            bg=self.colors["card"],
            fg=self.colors["danger"],
            font=("Segoe UI", 10)
        )
        self.loginmsg.pack(anchor="w", pady=(16, 0))

    # ==========================================
    # AUTH FUNCTIONS
    # ==========================================
    def dologin(self):
        if not os.path.exists(self.authfile):
            self.loginmsg.config(text="Create an account first!")
            self.notify("Create an account first!", "error")
            return

        u = self.uentry.get().strip()
        p = self.pentry.get().strip()

        if not u or not p:
            self.loginmsg.config(text="Fill all fields!")
            self.notify("Please fill all fields", "error")
            return

        enteredhash = hashlib.sha256(p.encode()).hexdigest()

        with open(self.authfile, "r") as f:
            for line in f:
                if "," in line:
                    username, passwordhash = line.strip().split(",", 1)
                    if username == u and passwordhash == enteredhash:
                        self.currentuser = u
                        if not os.path.exists("vaults"):
                            os.makedirs("vaults")
                        self.datafile = os.path.join("vaults", f"{u}_vault.txt")
                        self.temppassword = ""
                        self.visiblepasswordrows = {}
                        self.lastlogininfo = time.strftime("%d-%m-%Y %I:%M %p")
                        self.notify("Login successful", "success")
                        self.showdashboard("dashboard")
                        return

        self.loginmsg.config(text="Invalid Credentials!")
        self.notify("Invalid credentials", "error")

    def doreg(self):
        u = self.uentry.get().strip()
        p = self.pentry.get().strip()
        c = self.confirmentry.get().strip()

        if not u or not p or not c:
            self.loginmsg.config(text="Fill all fields!")
            self.notify("Please fill all fields", "error")
            return

        if p != c:
            self.loginmsg.config(text="Passwords do not match!")
            self.notify("Passwords do not match", "error")
            return

        if os.path.exists(self.authfile):
            with open(self.authfile, "r") as f:
                for line in f:
                    if "," in line:
                        username, _ = line.strip().split(",", 1)
                        if username == u:
                            self.loginmsg.config(text="Username already exists!")
                            self.notify("Username already exists", "error")
                            return

        with open(self.authfile, "a") as f:
            f.write(f"{u},{hashlib.sha256(p.encode()).hexdigest()}\n")

        messagebox.showinfo("Registration Successful", "Account created successfully. Redirecting to Sign In page.")
        self.notify("Account created successfully", "success")
        self.signupusernamevar.set("")
        self.signuppasswordvar.set("")
        self.signupconfirmvar.set("")
        self.showsigninscreen()

    # ==========================================
    # DASHBOARD
    # ==========================================
    def showdashboard(self, page="dashboard"):
        self.currentpage = page
        self.clearscreen()

        shell = tk.Frame(self.maincontainer, bg=self.colors["bg"])
        shell.pack(fill="both", expand=True)
        shell.grid_rowconfigure(0, weight=1)
        shell.grid_columnconfigure(0, weight=0)
        shell.grid_columnconfigure(1, weight=1)

        sidebar = tk.Frame(shell, bg=self.colors["card"], width=230, highlightbackground=self.colors["border"], highlightthickness=1)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(7, weight=1)

        self.buildsidebar(sidebar)

        _, _, content, _ = self.make_scrollable_page(shell)

        if page == "dashboard":
            self.builddashboardhome(content)
        elif page == "add":
            self.buildaddpasswordpage(content)
        elif page == "retrieve":
            self.buildretrievepage(content)
        elif page == "settings":
            self.buildsettingspage(content)
        elif page == "about":
            self.buildaboutpage(content)
        elif page == "logout":
            self.logout()

    def buildsidebar(self, parent):
        tk.Label(parent, text="🔐 SecurePass", bg=self.colors["card"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 4))

        tk.Label(parent, text="Vault Navigation", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 9)).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 18))

        navarea = tk.Frame(parent, bg=self.colors["card"])
        navarea.grid(row=2, column=0, sticky="new", padx=12)

        self.createnavbutton(navarea, "Dashboard", "🏠", "dashboard").pack(fill="x", pady=5)
        self.createnavbutton(navarea, "Add Password", "➕", "add").pack(fill="x", pady=5)
        self.createnavbutton(navarea, "Retrieve Password", "🔍", "retrieve").pack(fill="x", pady=5)
        self.createnavbutton(navarea, "Settings", "⚙", "settings").pack(fill="x", pady=5)
        self.createnavbutton(navarea, "About", "ℹ", "about").pack(fill="x", pady=5)

        logoutwrap = tk.Frame(parent, bg=self.colors["card"])
        logoutwrap.grid(row=8, column=0, sticky="sw", padx=12, pady=16)

        logoutbtn = self.createbutton(logoutwrap, "Logout", self.logout, "danger", fg="white")
        logoutbtn.pack(anchor="sw")

    def builddashboardhome(self, parent):
        headerrow = tk.Frame(parent, bg=self.colors["bg"])
        headerrow.pack(fill="x", pady=(0, 16))
        headerrow.grid_columnconfigure(0, weight=1)
        headerrow.grid_columnconfigure(1, weight=0)

        leftheader = tk.Frame(headerrow, bg=self.colors["bg"])
        leftheader.grid(row=0, column=0, sticky="w")

        tk.Label(
            leftheader,
            text="Welcome,",
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        tk.Label(
            leftheader,
            text=f" {self.currentuser}",
            bg=self.colors["bg"],
            fg=self.colors["accentblue"],
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        tk.Label(
            headerrow,
            text=f"Last Login: {self.lastlogininfo}",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10)
        ).grid(row=0, column=1, sticky="e", padx=(16, 0), pady=(8, 0))

        stats = tk.Frame(parent, bg=self.colors["bg"])
        stats.pack(fill="x", pady=(6, 14))
        for col in range(4):
            stats.grid_columnconfigure(col, weight=1)

        cardsdata = [
            ("Logged In User", self.currentuser if self.currentuser else "-", self.colors["accentblue"]),
            ("Vault Status", "Secure", self.colors["success"]),
            ("Total Passwords Stored", str(self.gettotalpasswords()), self.colors["accentpurple"]),
            ("Encryption Status", "Active", self.colors["accentblue"]),
        ]

        for i, (title, value, accent) in enumerate(cardsdata):
            card = tk.Frame(stats, bg=self.colors["card"], height=128, highlightbackground=accent, highlightthickness=2)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            card.grid_propagate(False)

            tk.Label(card, text=title, bg=self.colors["card"], fg=self.colors["muted"],
                     font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(18, 8))
            tk.Label(card, text=value, bg=self.colors["card"], fg=self.colors["text"],
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18)
            self.addhovereffect(card, self.colors["card"], self.colors["card3"])

        leftcard = self.createcard(parent, border=self.colors["accentpurple"])
        leftcard.pack(fill="x", pady=(2, 12))

        tk.Label(leftcard, text="📌 Last Saved Website", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(16, 6))

        lastsite = self.getlastsavedwebsite()
        tk.Label(leftcard, text=lastsite if lastsite else "No entries yet", bg=self.colors["card"],
                 fg=self.colors["accentpurple"], font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=18, pady=(0, 6))

        tk.Label(leftcard, text="This reflects the most recently stored website in your vault.",
                 bg=self.colors["card"], fg=self.colors["muted"], font=("Segoe UI", 10),
                 justify="left").pack(anchor="w", padx=18, pady=(0, 18))

        self.buildsavedcredentialspanel(parent)

    def buildsavedcredentialspanel(self, parent):
        panel = self.createcard(parent, border=self.colors["accentblue"])
        panel.pack(fill="both", expand=True, pady=(2, 16))

        tk.Label(panel, text="Saved Websites & Credentials", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(16, 4))

        tk.Label(panel, text="Manage your stored entries securely. Passwords remain hidden by default.",
                 bg=self.colors["card"], fg=self.colors["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 12))

        header = tk.Frame(panel, bg=self.colors["card3"])
        header.pack(fill="x", padx=18, pady=(0, 6))
        header.grid_columnconfigure(0, weight=2)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=1)
        header.grid_columnconfigure(3, weight=3)

        tk.Label(header, text="Website Name", bg=self.colors["card3"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tk.Label(header, text="Username/Email", bg=self.colors["card3"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=10, pady=10)
        tk.Label(header, text="Password", bg=self.colors["card3"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w", padx=10, pady=10)
        tk.Label(header, text="Actions", bg=self.colors["card3"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=3, sticky="w", padx=10, pady=10)

        container = tk.Frame(panel, bg=self.colors["card"])
        container.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        canvas = tk.Canvas(container, bg=self.colors["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollframe = tk.Frame(canvas, bg=self.colors["card"])

        scrollframe.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=scrollframe, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def resize_inner_width(event):
            canvas.itemconfigure(window_id, width=event.width)

        canvas.bind("<Configure>", resize_inner_width)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        entries = self.loadsavedentries()
        if not entries:
            empty = tk.Label(scrollframe, text="No saved entries found for this user.",
                             bg=self.colors["card"], fg=self.colors["muted"], font=("Segoe UI", 11))
            empty.pack(anchor="w", pady=10)
            return

        for idx, entry in enumerate(entries):
            self.buildsavedrow(scrollframe, entry, idx)

    def buildsavedrow(self, parent, entry, idx):
        row = tk.Frame(parent, bg=self.colors["entrybg"], highlightbackground=self.colors["border"], highlightthickness=1)
        row.pack(fill="x", pady=4)
        row.grid_columnconfigure(0, weight=2)
        row.grid_columnconfigure(1, weight=2)
        row.grid_columnconfigure(2, weight=1)
        row.grid_columnconfigure(3, weight=3)

        site = entry["site"]
        account = entry["account"]
        keyid = f"{site}|{account}|{idx}"

        tk.Label(row, text=site, bg=self.colors["entrybg"], fg=self.colors["text"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=12)
        tk.Label(row, text=account if account else "-", bg=self.colors["entrybg"], fg=self.colors["text"],
                 font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", padx=10, pady=12)

        visible = self.visiblepasswordrows.get(keyid, False)
        passwordtext = self.decryptentry(entry) if visible else "••••••••••"
        passlabel = tk.Label(row, text=passwordtext, bg=self.colors["entrybg"],
                             fg=self.colors["warning"] if visible else self.colors["text"],
                             font=("Consolas", 10, "bold"))
        passlabel.grid(row=0, column=2, sticky="w", padx=10, pady=12)

        actions = tk.Frame(row, bg=self.colors["entrybg"])
        actions.grid(row=0, column=3, sticky="w", padx=10, pady=8)

        self.createsmallactionbutton(
            actions,
            "Hide Password" if visible else "Show Password",
            lambda e=entry, i=idx: self.togglesavedpassword(e, i),
            "accentpurple",
            width=13
        ).pack(side="left", padx=(0, 6))

        self.createsmallactionbutton(
            actions,
            "Copy Password",
            lambda e=entry: self.copyentrypassword(e),
            "success",
            width=12
        ).pack(side="left", padx=6)

        self.createsmallactionbutton(
            actions,
            "Edit Entry",
            lambda e=entry: self.editentrypopup(e),
            "accentblue",
            width=10
        ).pack(side="left", padx=6)

        self.createsmallactionbutton(
            actions,
            "Delete Entry",
            lambda e=entry: self.deleteentry(e),
            "danger",
            width=11
        ).pack(side="left", padx=6)

    def togglesavedpassword(self, entry, idx):
        keyid = f"{entry['site']}|{entry['account']}|{idx}"
        current = self.visiblepasswordrows.get(keyid, False)
        self.visiblepasswordrows[keyid] = not current
        self.showdashboard("dashboard")

    def buildaddpasswordpage(self, parent):
        self.createtitle(parent, "Add Password", "Store a new encrypted password safely inside your personal vault.")
        card = self.createcard(parent, border=self.colors["accentblue"])
        card.pack(fill="x", pady=8)

        tk.Label(card, text="Add Password", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(card, text="All saved entries remain linked to the currently logged-in user vault.",
                 bg=self.colors["card"], fg=self.colors["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 10))

        form = tk.Frame(card, bg=self.colors["card"])
        form.pack(fill="x", padx=18, pady=16)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        tk.Label(form, text="Website/App Name", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6)
        self.sitein = self.createentry(form, self.addsitevar)
        self.sitein.grid(row=1, column=0, sticky="ew", ipady=10, padx=(0, 12), pady=(0, 12))

        tk.Label(form, text="Username/Email", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", pady=6)
        self.accountin = self.createentry(form, self.addaccountvar)
        self.accountin.grid(row=1, column=1, sticky="ew", ipady=10, pady=(0, 12))

        tk.Label(form, text="Password", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=6)
        self.passin = self.createentry(form, self.addpasswordvar, show=None if self.showaddpasswordvar.get() else "*")
        self.passin.grid(row=3, column=0, sticky="ew", ipady=10, padx=(0, 12), pady=(0, 12))

        tk.Label(form, text="Encryption Type", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", pady=6)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Vault.TCombobox",
            fieldbackground=self.colors["entrybg"],
            background=self.colors["entrybg"],
            foreground=self.colors["text"]
        )

        self.algocb = ttk.Combobox(form, values=["Fernet", "Caesar", "Affine", "RC4"], state="readonly", width=30, style="Vault.TCombobox")
        self.algocb.current(0)
        self.algocb.grid(row=3, column=1, sticky="ew", pady=(0, 12))

        tk.Checkbutton(
            card,
            text="Show Password",
            variable=self.showaddpasswordvar,
            command=lambda: self.showdashboard("add"),
            bg=self.colors["card"],
            fg=self.colors["text"],
            activebackground=self.colors["card"],
            activeforeground=self.colors["accentblue"],
            selectcolor=self.colors["entrybg"],
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=18, pady=(0, 12))

        self.createbutton(card, "Save Password", self.savedata, "success").pack(anchor="w", padx=18, pady=(0, 18))

    def buildretrievepage(self, parent):
        self.createtitle(parent, "Retrieve Password", "Search saved credentials from your personal vault.")
        card = self.createcard(parent, border=self.colors["accentpurple"])
        card.pack(fill="x", pady=8)

        tk.Label(card, text="Retrieve Saved Password", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(card, text="Search by website/app name and securely reveal or copy stored password.",
                 bg=self.colors["card"], fg=self.colors["muted"], font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 12))

        body = tk.Frame(card, bg=self.colors["card"])
        body.pack(fill="x", padx=18, pady=16)

        tk.Label(body, text="Enter Website/App Name", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w")
        self.searchin = self.createentry(body, self.searchvar)
        self.searchin.pack(fill="x", ipady=10, pady=(6, 12))

        self.createbutton(body, "Search Password", self.retrievedata, "accentblue").pack(anchor="w", pady=(0, 12))

        resultcard = tk.Frame(body, bg=self.colors["entrybg"], highlightbackground=self.colors["border"], highlightthickness=1)
        resultcard.pack(fill="x", pady=4)

        tk.Label(resultcard, text="Retrieved Password", bg=self.colors["entrybg"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=(12, 4))
        self.displaylbl = tk.Label(resultcard, text="", font=("Consolas", 16, "bold"),
                                   bg=self.colors["entrybg"], fg=self.colors["text"], pady=8)
        self.displaylbl.pack(anchor="w", padx=14)

        btnrow = tk.Frame(body, bg=self.colors["card"])
        btnrow.pack(anchor="w", pady=14)

        self.createbutton(btnrow, "Show 3s", self.revealtemp, "accentpurple").pack(side="left", padx=(0, 10))
        self.createbutton(btnrow, "Copy Securely", self.copysecurely, "success").pack(side="left")

    def buildsettingspage(self, parent):
        self.createtitle(parent, "Settings", "Manage application behavior and user session details.")
        card = self.createcard(parent, border=self.colors["accentblue"])
        card.pack(fill="x", pady=8)

        tk.Label(card, text="Session Settings", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(card, text=f"Logged in as: {self.currentuser}", bg=self.colors["card"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18)

        info = (
            "• Separate vault maintained for every registered user\n"
            "• Clipboard is automatically cleared after secure copy\n"
            "• Supports Fernet, Caesar, Affine and RC4 encryption modes\n"
            "• Logout clears the current session and temporary password data"
        )
        tk.Label(card, text=info, bg=self.colors["card"], fg=self.colors["muted"],
                 justify="left", font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(12, 18))

    def buildaboutpage(self, parent):
        self.createtitle(parent, "About", "Application details and project information.")
        card = self.createcard(parent, border=self.colors["accentpurple"])
        card.pack(fill="x", pady=8)

        tk.Label(card, text="SecurePass Vault", bg=self.colors["card"], fg=self.colors["text"],
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            card,
            text="A secure multi-user password management system with multiple encryption algorithms for protecting sensitive credentials.",
            bg=self.colors["card"],
            fg=self.colors["muted"],
            justify="left",
            font=("Segoe UI", 11),
            wraplength=800
        ).pack(anchor="w", padx=18, pady=(0, 12))
        tk.Label(card, text="Developer: Ikjyot Kaur", bg=self.colors["card"], fg=self.colors["accentblue"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18, pady=(0, 18))

    # ==========================================
    # DATA FUNCTIONS
    # ==========================================
    def loadsavedentries(self):
        entries = []
        if not self.datafile or not os.path.exists(self.datafile):
            return entries

        with open(self.datafile, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split("|")]
                if len(parts) == 5:
                    site, account, algo, enc, k = parts
                    entries.append({"site": site, "account": account, "algo": algo, "enc": enc, "key": k})
                elif len(parts) == 4:
                    site, algo, enc, k = parts
                    entries.append({"site": site, "account": "", "algo": algo, "enc": enc, "key": k})
        return entries

    def decryptentry(self, entry):
        try:
            if entry["algo"] == "Fernet":
                return self.fernet.decrypt(entry["enc"].encode()).decode()
            elif entry["algo"] == "Caesar":
                return CipherEngine.caesar(entry["enc"], entry["key"], "dec")
            elif entry["algo"] == "Affine":
                return CipherEngine.affine(entry["enc"], entry["key"], "dec")
            elif entry["algo"] == "RC4":
                return CipherEngine.rc4(entry["enc"], entry["key"])
        except:
            return "Decryption Error"
        return ""

    def writeentries(self, entries):
        with open(self.datafile, "w") as f:
            for entry in entries:
                f.write(f"{entry['site']}|{entry['account']}|{entry['algo']}|{entry['enc']}|{entry['key']}\n")

    def copyentrypassword(self, entry):
        password = self.decryptentry(entry)
        if password == "Decryption Error":
            self.notify("Could not decrypt this password", "error")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(password)
        self.notify("Password copied securely. Clipboard clears in 10s.", "success")
        self.root.after(10000, lambda: self.root.clipboard_clear())

    def editentrypopup(self, entry):
        popup = tk.Toplevel(self.root)
        popup.title("Edit Entry")
        popup.geometry("480x360")
        popup.configure(bg=self.colors["bg"])
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(popup, text="Edit Saved Entry", bg=self.colors["bg"], fg=self.colors["text"],
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(18, 10))

        form = self.createcard(popup, border=self.colors["accentblue"])
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        sitevar = tk.StringVar(value=entry["site"])
        accountvar = tk.StringVar(value=entry["account"])
        passwordvar = tk.StringVar(value=self.decryptentry(entry))
        algovar = tk.StringVar(value=entry["algo"])

        tk.Label(form, text="Website/App Name", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(16, 4))
        siteentry = self.createentry(form, sitevar)
        siteentry.pack(fill="x", padx=18, ipady=8, pady=(0, 10))

        tk.Label(form, text="Username/Email", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 4))
        accentry = self.createentry(form, accountvar)
        accentry.pack(fill="x", padx=18, ipady=8, pady=(0, 10))

        tk.Label(form, text="Password", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 4))
        pwdentry = self.createentry(form, passwordvar)
        pwdentry.pack(fill="x", padx=18, ipady=8, pady=(0, 10))

        tk.Label(form, text="Encryption Type", bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 4))
        combo = ttk.Combobox(form, values=["Fernet", "Caesar", "Affine", "RC4"], state="readonly", textvariable=algovar)
        combo.pack(fill="x", padx=18, pady=(0, 14))
        combo.set(entry["algo"])

        btns = tk.Frame(form, bg=self.colors["card"])
        btns.pack(anchor="w", padx=18, pady=(0, 18))

        def saveedit():
            newsite = sitevar.get().strip().lower()
            newaccount = accountvar.get().strip()
            newpassword = passwordvar.get()
            newalgo = combo.get()

            if not newsite or not newpassword:
                self.notify("Website and password are required", "error")
                return

            k = "NA"
            if newalgo == "Caesar":
                k = simpledialog.askinteger("Key", "Shift 1-25", parent=popup)
                if k is None:
                    return
                enc = CipherEngine.caesar(newpassword, k, "enc")
            elif newalgo == "Affine":
                k = simpledialog.askstring("Key", "Enter a,b e.g. 5,8", parent=popup)
                if not k:
                    return
                enc = CipherEngine.affine(newpassword, k, "enc")
            elif newalgo == "RC4":
                k = simpledialog.askstring("Key", "Secret Key", parent=popup)
                if not k:
                    return
                enc = CipherEngine.rc4(newpassword, k)
            else:
                enc = self.fernet.encrypt(newpassword.encode()).decode()

            entries = self.loadsavedentries()
            for i, e in enumerate(entries):
                if e["site"] == entry["site"] and e["account"] == entry["account"] and e["enc"] == entry["enc"]:
                    entries[i] = {
                        "site": newsite,
                        "account": newaccount,
                        "algo": newalgo,
                        "enc": enc,
                        "key": str(k)
                    }
                    break

            self.writeentries(entries)
            popup.destroy()
            self.notify("Entry updated successfully", "success")
            self.showdashboard("dashboard")

        self.createbutton(btns, "Save Changes", saveedit, "success").pack(side="left", padx=(0, 10))
        self.createbutton(btns, "Cancel", popup.destroy, "accentpurple").pack(side="left")

    def deleteentry(self, entry):
        answer = messagebox.askokcancel("Delete Entry", f"Delete saved entry for {entry['site']}?")
        if not answer:
            return

        entries = self.loadsavedentries()
        filtered = []
        removed = False

        for e in entries:
            if not removed and e["site"] == entry["site"] and e["account"] == entry["account"] and e["enc"] == entry["enc"]:
                removed = True
                continue
            filtered.append(e)

        self.writeentries(filtered)
        self.notify("Entry deleted successfully", "success")
        self.showdashboard("dashboard")

    def savedata(self):
        site = self.sitein.get().strip().lower()
        account = self.accountin.get().strip()
        pwd = self.passin.get()
        algo = self.algocb.get()

        if not site or not pwd:
            self.notify("Website and password are required", "error")
            messagebox.showerror("Missing Data", "Please enter website/app name and password.")
            return

        k = "NA"
        enc = ""
        if algo == "Caesar":
            k = simpledialog.askinteger("Key", "Shift 1-25")
            if k is None:
                return
            enc = CipherEngine.caesar(pwd, k, "enc")
        elif algo == "Affine":
            k = simpledialog.askstring("Key", "Enter a,b e.g. 5,8")
            if not k:
                return
            enc = CipherEngine.affine(pwd, k, "enc")
        elif algo == "RC4":
            k = simpledialog.askstring("Key", "Secret Key")
            if not k:
                return
            enc = CipherEngine.rc4(pwd, k)
        else:
            enc = self.fernet.encrypt(pwd.encode()).decode()

        if enc == "Error":
            self.notify("Encryption failed. Check your key.", "error")
            messagebox.showerror("Encryption Error", "Invalid encryption key or encryption failure.")
            return

        lines = []
        if os.path.exists(self.datafile):
            with open(self.datafile, "r") as f:
                lines = f.readlines()

        with open(self.datafile, "w") as f:
            for line in lines:
                parts = [p.strip() for p in line.strip().split("|")]
                if len(parts) > 1 and parts[0].lower() != site:
                    f.write(line)
            f.write(f"{site}|{account}|{algo}|{enc}|{k}\n")

        self.notify(f"Entry saved for {site}", "success")
        messagebox.showinfo("Success", f"Password entry for {site} saved successfully.")
        self.addsitevar.set("")
        self.addaccountvar.set("")
        self.addpasswordvar.set("")
        self.showdashboard("dashboard")

    def retrievedata(self):
        query = self.searchin.get().strip().lower()
        self.temppassword = ""

        if not os.path.exists(self.datafile) or not query:
            self.notify("Enter a website/app name to search", "error")
            return

        with open(self.datafile, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 5:
                    site, account, algo, enc, k = parts
                elif len(parts) == 4:
                    site, algo, enc, k = parts
                    account = ""
                else:
                    continue

                if site.lower() == query:
                    try:
                        if algo == "Fernet":
                            self.temppassword = self.fernet.decrypt(enc.encode()).decode()
                        elif algo == "Caesar":
                            self.temppassword = CipherEngine.caesar(enc, k, "dec")
                        elif algo == "Affine":
                            self.temppassword = CipherEngine.affine(enc, k, "dec")
                        elif algo == "RC4":
                            self.temppassword = CipherEngine.rc4(enc, k)

                        self.displaylbl.config(text="", fg=self.colors["text"])
                        self.notify(f"Retrieved password for {site}", "success")
                        return
                    except:
                        self.notify("Could not decrypt this entry", "error")
                        messagebox.showerror("Decryption Error", "Unable to decrypt saved password.")
                        return

        self.notify("Website not found in vault", "error")
        messagebox.showinfo("Not Found", "Website/App not found in your vault.")

    def revealtemp(self):
        if not self.temppassword:
            self.notify("No password retrieved yet", "error")
            return
        self.displaylbl.config(text=self.temppassword, fg=self.colors["warning"])
        self.root.after(3000, lambda: self.displaylbl.config(text="", fg=self.colors["text"]))

    def copysecurely(self):
        if not self.temppassword:
            self.notify("No password retrieved yet", "error")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.temppassword)
        self.notify("Password copied securely. Clipboard clears in 10s.", "success")
        self.root.after(10000, lambda: self.root.clipboard_clear())

    def logout(self):
        self.currentuser = None
        self.temppassword = ""
        self.datafile = ""
        self.visiblepasswordrows = {}
        self.searchvar.set("")
        self.addsitevar.set("")
        self.addaccountvar.set("")
        self.addpasswordvar.set("")
        self.signinpasswordvar.set("")
        self.notify("Logged out successfully", "success")
        self.showhomescreen()

    def gettotalpasswords(self):
        if not self.datafile or not os.path.exists(self.datafile):
            return 0
        with open(self.datafile, "r") as f:
            return len([line for line in f if line.strip()])

    def getlastsavedwebsite(self):
        if not self.datafile or not os.path.exists(self.datafile):
            return ""
        with open(self.datafile, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return ""
        parts = lines[-1].split("|")
        return parts[0] if parts else ""


if __name__ == "__main__":
    root = tk.Tk()
    app = SecureVaultApp(root)
    root.mainloop()
