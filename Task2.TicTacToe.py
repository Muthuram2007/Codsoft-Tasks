"""
CodSoft AI Internship - Task 2: Tic-Tac-Toe AI (GUI Version)
Unbeatable AI using Minimax with Alpha-Beta Pruning
Run: python task2_tictactoe_ai.py
Dependencies: None (tkinter ships with Python)
"""

import tkinter as tk
from tkinter import font as tkfont
import math

# ---------------- Game Logic ----------------
HUMAN = "X"
AI = "O"
EMPTY = ""

WIN_COMBOS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # cols
    (0, 4, 8), (2, 4, 6)               # diagonals
]

def check_winner(board):
    for a, b, c in WIN_COMBOS:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None

def is_full(board):
    return all(cell != EMPTY for cell in board)

def available_moves(board):
    return [i for i, cell in enumerate(board) if cell == EMPTY]

def minimax(board, depth, alpha, beta, is_maximizing):
    winner, _ = check_winner(board)
    if winner == AI:
        return 10 - depth
    if winner == HUMAN:
        return depth - 10
    if is_full(board):
        return 0

    if is_maximizing:
        best_score = -math.inf
        for move in available_moves(board):
            board[move] = AI
            score = minimax(board, depth + 1, alpha, beta, False)
            board[move] = EMPTY
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = math.inf
        for move in available_moves(board):
            board[move] = HUMAN
            score = minimax(board, depth + 1, alpha, beta, True)
            board[move] = EMPTY
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score

def best_move(board):
    best_score = -math.inf
    move_choice = None
    for move in available_moves(board):
        board[move] = AI
        score = minimax(board, 0, -math.inf, math.inf, False)
        board[move] = EMPTY
        if score > best_score:
            best_score = score
            move_choice = move
    return move_choice

# ---------------- GUI ----------------
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        root.title("Unbeatable Tic-Tac-Toe AI — CodSoft Task 2")
        root.geometry("460x600")
        root.configure(bg="#0F172A")
        root.resizable(False, False)

        title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        status_font = tkfont.Font(family="Segoe UI", size=12)
        cell_font = tkfont.Font(family="Segoe UI", size=36, weight="bold")

        self.board = [EMPTY] * 9
        self.game_over = False

        # Header
        header = tk.Frame(root, bg="#1E293B", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="❌⭕  Tic-Tac-Toe AI", font=title_font, bg="#1E293B", fg="#38BDF8").pack(side="left", padx=20, pady=15)
        tk.Label(header, text="CodSoft AI • Task 2", font=("Segoe UI", 9), bg="#1E293B", fg="#94A3B8").pack(side="right", padx=20)

        # Status label
        self.status_var = tk.StringVar(value="Your turn — you're X")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=status_font,
                                      bg="#0F172A", fg="#E2E8F0", pady=12)
        self.status_label.pack()

        # Board grid
        board_frame = tk.Frame(root, bg="#0F172A")
        board_frame.pack(pady=10)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(board_frame, text="", font=cell_font, width=3, height=1,
                             bg="#1E293B", fg="#38BDF8", activebackground="#334155",
                             relief="flat", command=lambda i=i: self.human_move(i))
            btn.grid(row=i // 3, column=i % 3, padx=6, pady=6, ipadx=10, ipady=10)
            self.buttons.append(btn)

        # Controls
        control_frame = tk.Frame(root, bg="#0F172A")
        control_frame.pack(pady=15)

        reset_btn = tk.Button(control_frame, text="🔄 New Game", font=("Segoe UI", 10, "bold"),
                               bg="#38BDF8", fg="#0F172A", relief="flat", activebackground="#0EA5E9",
                               cursor="hand2", command=self.reset_game, padx=15, pady=6)
        reset_btn.pack(side="left", padx=6)

        self.score_var = tk.StringVar(value="You: 0   AI: 0   Draws: 0")
        self.wins = {"human": 0, "ai": 0, "draw": 0}
        tk.Label(root, textvariable=self.score_var, font=("Segoe UI", 10), bg="#0F172A", fg="#94A3B8").pack(pady=5)

    def human_move(self, i):
        if self.game_over or self.board[i] != EMPTY:
            return
        self.board[i] = HUMAN
        self.buttons[i].config(text=HUMAN, fg="#38BDF8")
        winner, combo = check_winner(self.board)
        if winner or is_full(self.board):
            self.end_game(winner, combo)
            return
        self.status_var.set("AI is thinking...")
        self.root.update_idletasks()
        self.root.after(400, self.ai_move)

    def ai_move(self):
        if self.game_over:
            return
        move = best_move(self.board)
        if move is not None:
            self.board[move] = AI
            self.buttons[move].config(text=AI, fg="#F472B6")
        winner, combo = check_winner(self.board)
        if winner or is_full(self.board):
            self.end_game(winner, combo)
            return
        self.status_var.set("Your turn — you're X")

    def end_game(self, winner, combo):
        self.game_over = True
        if winner == HUMAN:
            self.status_var.set("🎉 You win! (impossible... but nice!)")
            self.wins["human"] += 1
        elif winner == AI:
            self.status_var.set("🤖 AI wins! Better luck next time.")
            self.wins["ai"] += 1
        else:
            self.status_var.set("🤝 It's a draw!")
            self.wins["draw"] += 1

        if combo:
            for idx in combo:
                self.buttons[idx].config(bg="#334155")

        self.score_var.set(f"You: {self.wins['human']}   AI: {self.wins['ai']}   Draws: {self.wins['draw']}")

    def reset_game(self):
        self.board = [EMPTY] * 9
        self.game_over = False
        self.status_var.set("Your turn — you're X")
        for btn in self.buttons:
            btn.config(text="", bg="#1E293B")


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
