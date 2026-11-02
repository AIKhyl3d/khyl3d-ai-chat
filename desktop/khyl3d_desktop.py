"""
Khyl3d AI CHAT Script — Windows desktop companion.
This client talks only to your deployed backend; users do not enter API keys.
Set KHYL3D_SERVER_URL to your deployed service URL before packaging.
"""
import json
import os
import threading
import tkinter as tk
from tkinter import messagebox
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DEFAULT_SERVER = os.getenv("KHYL3D_SERVER_URL", "https://YOUR-SERVICE.onrender.com").rstrip("/")
APP_NAME = "Khyl3d AI CHAT Script"

class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("780x620")
        root.minsize(580, 440)
        top = tk.Frame(root, bg="#14213d", padx=16, pady=14)
        top.pack(fill="x")
        tk.Label(top, text=APP_NAME, bg="#14213d", fg="white",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(top, text="Secure online AI assistant", bg="#14213d", fg="#dce6f5").pack(anchor="w")
        self.chat = tk.Text(root, wrap="word", state="disabled", padx=12, pady=12, font=("Segoe UI", 10))
        self.chat.pack(fill="both", expand=True, padx=12, pady=12)
        self.chat.tag_configure("label", font=("Segoe UI", 10, "bold"), foreground="#176b4a")
        row = tk.Frame(root, padx=12, pady=10)
        row.pack(fill="x")
        self.input = tk.Text(row, height=3, wrap="word", font=("Segoe UI", 10))
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<Control-Return>", self.send_event)
        self.send_btn = tk.Button(row, text="Send", command=self.send, padx=18, pady=8)
        self.send_btn.pack(side="left", padx=(8, 0))
        self.status = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status, anchor="w", padx=12, pady=5).pack(fill="x")
        self.add("Khyl3d AI", "Welcome! Ask a question. Your API key is managed by the service owner.")
    def add(self, who, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", who + ":\n", "label")
        self.chat.insert("end", text + "\n\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")
    def send_event(self, _):
        self.send()
        return "break"
    def send(self):
        msg = self.input.get("1.0", "end").strip()
        if not msg: return
        if "YOUR-SERVICE" in DEFAULT_SERVER:
            messagebox.showwarning(APP_NAME, "The app owner must set the deployed server URL in this desktop client first.")
            return
        self.input.delete("1.0", "end")
        self.add("You", msg)
        self.send_btn.configure(state="disabled")
        self.status.set("Connecting…")
        threading.Thread(target=self.request, args=(msg,), daemon=True).start()
    def request(self, msg):
        try:
            req = Request(DEFAULT_SERVER + "/api/chat",
                          data=json.dumps({"message": msg}).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(req, timeout=120) as response:
                data = json.loads(response.read().decode())
            self.root.after(0, self.done, data.get("answer", "No answer returned."), None)
        except HTTPError as e:
            try: detail = json.loads(e.read().decode()).get("detail", str(e))
            except Exception: detail = str(e)
            self.root.after(0, self.done, None, detail)
        except (URLError, TimeoutError) as e:
            self.root.after(0, self.done, None, "Could not connect. Check your internet connection and server URL.")
        except Exception:
            self.root.after(0, self.done, None, "Something went wrong. Please try again.")
    def done(self, answer, error):
        self.add("Notice" if error else "Khyl3d AI", error or answer)
        self.send_btn.configure(state="normal")
        self.status.set("Ready")
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
if __name__ == "__main__": main()
