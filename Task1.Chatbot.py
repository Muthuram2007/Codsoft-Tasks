"""
CodSoft AI Internship - Task 1: Rule-Based Chatbot (GUI Version)
Run: python task1_chatbot_gui.py
Dependencies: None (tkinter ships with Python)
"""

import tkinter as tk
from tkinter import font as tkfont
import re
from datetime import datetime

# ---------------- Chatbot Logic ----------------
rules = [
    (r'hello|hi\b|hey', 'Hello! How can I help you today?'),
    (r'how are you', "I'm doing great, thanks for asking! How about you?"),
    (r'what is your name|who are you', "I'm RuleBot, your AI assistant built for CodSoft!"),
    (r'what is ai|what is artificial intelligence', 'AI is the simulation of human intelligence by machines, especially computer systems.'),
    (r'bye|goodbye|exit|quit', 'Goodbye! Have a great day! \U0001F44B'),
    (r'help', 'I can answer questions about AI, greet you, tell jokes, or just chat!'),
    (r'what can you do', 'I can answer basic questions using predefined rules and pattern matching!'),
    (r'who made you|who created you', 'I was built as part of a CodSoft AI internship task.'),
    (r'time', f"I don't track real time, but it's around {datetime.now().strftime('%I:%M %p')} on your system."),
    (r'date', f"Today's date on your system is {datetime.now().strftime('%B %d, %Y')}."),
    (r'joke', 'Why did the AI break up with the computer? Too many missing connections! \U0001F602'),
    (r'thank', "You're very welcome!"),
    (r'codsoft', 'CodSoft runs awesome internship programs for students like you!'),
]

def get_response(user_input):
    txt = user_input.lower().strip()
    for pattern, response in rules:
        if re.search(pattern, txt):
            return response
    return "I'm not sure about that. Try asking something else, like 'what is AI' or 'tell me a joke'!"

# ---------------- GUI ----------------
class ChatbotApp:
    def __init__(self, root):
        self.root = root
        root.title("RuleBot — CodSoft AI Task 1")
        root.geometry("520x650")
        root.configure(bg="#F3F0FF")
        root.resizable(False, False)

        title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        chat_font = tkfont.Font(family="Segoe UI", size=11)

        # Header
        header = tk.Frame(root, bg="#7C3AED", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="🌿  RuleBot", font=title_font, bg="#7C3AED", fg="#FFFFFF").pack(side="left", padx=20, pady=15)
        tk.Label(header, text="CodSoft AI • Task 1", font=("Segoe UI", 9), bg="#7C3AED", fg="#E9D8FD").pack(side="right", padx=20)

        # Chat area
        chat_frame = tk.Frame(root, bg="#F3F0FF")
        chat_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.canvas = tk.Canvas(chat_frame, bg="#F3F0FF", highlightthickness=0)
        scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=self.canvas.yview)
        self.msg_frame = tk.Frame(self.canvas, bg="#F3F0FF")

        self.msg_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.msg_frame, anchor="nw", width=470)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.chat_font = chat_font
        self.add_bubble("RuleBot", "Hi! I'm RuleBot \U0001F44B Ask me anything — try 'hello', 'what is AI', or 'joke'.", bot=True)

        # Input area
        input_frame = tk.Frame(root, bg="#EDE9FE", height=70)
        input_frame.pack(fill="x", side="bottom")
        input_frame.pack_propagate(False)

        self.entry = tk.Entry(input_frame, font=("Segoe UI", 12), bg="#FFFFFF", fg="#3B0764",
                               insertbackground="#3B0764", relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=18, ipady=8)
        self.entry.bind("<Return>", lambda e: self.send())
        self.entry.focus()

        send_btn = tk.Button(input_frame, text="Send ➤", font=("Segoe UI", 10, "bold"), bg="#10B981",
                              fg="#FFFFFF", relief="flat", activebackground="#059669", cursor="hand2",
                              command=self.send, padx=15)
        send_btn.pack(side="right", padx=(0, 15), pady=18, ipady=6)

    def add_bubble(self, sender, text, bot=False):
        row = tk.Frame(self.msg_frame, bg="#F3F0FF")
        row.pack(fill="x", pady=6, anchor="w" if bot else "e")

        bubble_color = "#FFFFFF" if bot else "#10B981"
        text_color = "#3B0764" if bot else "#FFFFFF"

        bubble = tk.Label(row, text=text, wraplength=320, justify="left", font=self.chat_font,
                           bg=bubble_color, fg=text_color, padx=12, pady=8,
                           highlightbackground="#C4B5FD", highlightthickness=1 if bot else 0)
        bubble.pack(side="left" if bot else "right", padx=10)

        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def send(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.add_bubble("You", user_text, bot=False)
        self.entry.delete(0, tk.END)

        reply = get_response(user_text)
        self.root.after(300, lambda: self.add_bubble("RuleBot", reply, bot=True))

        if re.search(r'bye|goodbye|exit|quit', user_text.lower()):
            self.root.after(1500, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()