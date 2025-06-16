import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from emoji import emojize
from playsound import playsound
from auth import login_user, signup_user
from protocol_utils import send_message, recv_message

HOST = '127.0.0.1'
PORT = 12345

client = None
username = ""

def start_chat():
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
        return

    window = tk.Tk()
    window.title(f"Secure Chat - {username}")
    window.geometry("600x500")
    window.configure(bg="#1e1e2e")

    top_frame = tk.Frame(window, bg="#1e1e2e")
    top_frame.pack(pady=5, fill=tk.X)
    tk.Label(top_frame, text=f"\U0001F464 {username}", fg="white", bg="#1e1e2e", font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
    tk.Button(top_frame, text="Create Group", command=lambda: messagebox.showinfo("Info", "Group feature coming soon")).pack(side=tk.LEFT, padx=5)
    tk.Button(top_frame, text="Close Chat", command=lambda: window.destroy()).pack(side=tk.RIGHT, padx=5)

    chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, height=20, width=70, bg="#2c2c3a", fg="white")
    chat_area.pack(padx=10, pady=5)
    chat_area.config(state='disabled')

    typing_label = tk.Label(window, text="", fg="lightgreen", bg="#1e1e2e")
    typing_label.pack()

    bottom_frame = tk.Frame(window, bg="#1e1e2e")
    bottom_frame.pack(pady=5, fill=tk.X)

    entry_field = tk.Entry(bottom_frame, width=50)
    entry_field.pack(side=tk.LEFT, padx=(10, 5), pady=5)

    def send_gui_message(event=None):
        msg = entry_field.get().strip()
        if msg:
            try:
                send_message(client, f"{username}: {msg}")
                entry_field.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def choose_emoji():
        emoji_win = tk.Toplevel(window)
        emoji_win.title("Choose Emoji")
        emoji_list = ['😊', '😂', '❤️', '🔥', '👍', '🙌', '🎉', '😎', '🥳', '💬']
        for em in emoji_list:
            btn = tk.Button(emoji_win, text=em, command=lambda e=em: entry_field.insert(tk.END, e))
            btn.pack(side=tk.LEFT, padx=2)

    def toggle_theme():
        bg = "#ffffff" if window.cget("bg") == "#1e1e2e" else "#1e1e2e"
        fg = "#000000" if bg == "#ffffff" else "#ffffff"
        window.configure(bg=bg)
        chat_area.configure(bg=bg, fg=fg)
        bottom_frame.configure(bg=bg)
        top_frame.configure(bg=bg)
        typing_label.configure(bg=bg, fg=fg)

    send_button = tk.Button(bottom_frame, text="Send", command=send_gui_message)
    send_button.pack(side=tk.LEFT, padx=5)

    emoji_button = tk.Button(bottom_frame, text="😊", command=choose_emoji)
    emoji_button.pack(side=tk.LEFT)

    theme_button = tk.Button(bottom_frame, text="🌗", command=toggle_theme)
    theme_button.pack(side=tk.LEFT, padx=5)

    window.bind('<Return>', send_gui_message)

    def receive_messages():
        while True:
            try:
                decrypted = recv_message(client)
                if not decrypted:
                    break
                if "typing..." in decrypted:
                    typing_label.config(text=decrypted)
                    window.after(1000, lambda: typing_label.config(text=""))
                else:
                    chat_area.config(state='normal')
                    chat_area.insert(tk.END, decrypted + "\n")
                    chat_area.config(state='disabled')
                    chat_area.see(tk.END)
                    #playsound("notification.mp3", block=False)
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def notify_typing(event=None):
        try:
            send_message(client, f"{username} typing...")
        except:
            pass

    entry_field.bind('<Key>', notify_typing)
    threading.Thread(target=receive_messages, daemon=True).start()
    window.mainloop()

def login_window():
    def attempt_login():
        global username
        if login_user(username_entry.get(), password_entry.get()):
            username = username_entry.get()
            login_win.destroy()
            start_chat()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

    def open_signup():
        login_win.destroy()
        signup_window()

    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("300x200")

    tk.Label(login_win, text="Username").pack()
    username_entry = tk.Entry(login_win)
    username_entry.pack()

    tk.Label(login_win, text="Password").pack()
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack()

    tk.Button(login_win, text="Login", command=attempt_login).pack(pady=5)
    tk.Button(login_win, text="Signup", command=open_signup).pack()
    login_win.mainloop()

def signup_window():
    def attempt_signup():
        if signup_user(username_entry.get(), password_entry.get()):
            signup_win.destroy()
            login_window()
        else:
            messagebox.showerror("Signup Failed", "Username may already exist!")

    signup_win = tk.Tk()
    signup_win.title("Signup")
    signup_win.geometry("300x200")

    tk.Label(signup_win, text="Choose Username").pack()
    username_entry = tk.Entry(signup_win)
    username_entry.pack()

    tk.Label(signup_win, text="Choose Password").pack()
    password_entry = tk.Entry(signup_win, show="*")
    password_entry.pack()

    tk.Button(signup_win, text="Signup", command=attempt_signup).pack()
    signup_win.mainloop()

if __name__ == "__main__":
    print("Starting GUI chat client...")
    login_window()