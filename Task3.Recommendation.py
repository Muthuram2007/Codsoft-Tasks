"""
CodSoft AI Internship - Task 4: Recommendation System (GUI Version)
Implements BOTH:
  1) Content-Based Filtering  -> recommends movies similar to one you like,
     based on genre overlap (cosine similarity of genre vectors).
  2) Collaborative Filtering  -> recommends movies for a user based on what
     similar users (by rating patterns) enjoyed (user-based CF).

Run: python task4_recommendation_system.py
Dependencies: None (tkinter ships with Python; uses only the standard library)
"""

import tkinter as tk
from tkinter import font as tkfont, ttk
import math

# ---------------- Sample Dataset ----------------
# A small built-in movie catalog with genres, and a user-item ratings matrix.
# (In a real system these would come from a database like MovieLens.)

MOVIES = {
    1:  {"title": "The Matrix",            "genres": {"Sci-Fi", "Action"}},
    2:  {"title": "Inception",              "genres": {"Sci-Fi", "Thriller"}},
    3:  {"title": "Interstellar",           "genres": {"Sci-Fi", "Drama"}},
    4:  {"title": "The Dark Knight",        "genres": {"Action", "Crime", "Drama"}},
    5:  {"title": "John Wick",              "genres": {"Action", "Thriller"}},
    6:  {"title": "The Notebook",           "genres": {"Romance", "Drama"}},
    7:  {"title": "La La Land",             "genres": {"Romance", "Musical"}},
    8:  {"title": "Titanic",                "genres": {"Romance", "Drama"}},
    9:  {"title": "The Hangover",           "genres": {"Comedy"}},
    10: {"title": "Superbad",               "genres": {"Comedy"}},
    11: {"title": "Get Out",                "genres": {"Horror", "Thriller"}},
    12: {"title": "A Quiet Place",          "genres": {"Horror", "Sci-Fi"}},
    13: {"title": "The Conjuring",          "genres": {"Horror"}},
    14: {"title": "Coco",                   "genres": {"Animation", "Family"}},
    15: {"title": "Toy Story",              "genres": {"Animation", "Family", "Comedy"}},
}

# user -> {movie_id: rating (1-5)}
RATINGS = {
    "Alice":   {1: 5, 2: 5, 3: 4, 4: 4, 9: 2},
    "Bob":     {1: 4, 4: 5, 5: 5, 9: 1, 10: 2},
    "Charlie": {6: 5, 7: 4, 8: 5, 2: 2},
    "Diana":   {9: 5, 10: 5, 15: 4, 6: 3},
    "Ethan":   {11: 5, 12: 4, 13: 5, 2: 3},
    "Farah":   {14: 5, 15: 5, 9: 3, 10: 4},
    "You":     {},  # the active user in the GUI — starts with no ratings
}

ALL_GENRES = sorted({g for m in MOVIES.values() for g in m["genres"]})


# ---------------- Content-Based Filtering ----------------
def genre_vector(genres):
    return [1 if g in genres else 0 for g in ALL_GENRES]


def cosine_similarity(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def content_based_recommend(movie_id, top_n=5):
    """Recommend movies with genre profiles similar to the given movie."""
    target_vec = genre_vector(MOVIES[movie_id]["genres"])
    scores = []
    for mid, info in MOVIES.items():
        if mid == movie_id:
            continue
        sim = cosine_similarity(target_vec, genre_vector(info["genres"]))
        if sim > 0:
            scores.append((mid, sim))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]


# ---------------- Collaborative Filtering (user-based) ----------------
def user_similarity(user_a, user_b):
    """Cosine similarity between two users based on movies they both rated."""
    ratings_a, ratings_b = RATINGS[user_a], RATINGS[user_b]
    common = set(ratings_a) & set(ratings_b)
    if not common:
        return 0.0
    v1 = [ratings_a[m] for m in common]
    v2 = [ratings_b[m] for m in common]
    return cosine_similarity(v1, v2)


def collaborative_recommend(user, top_n=5):
    """Recommend movies the target user hasn't rated, weighted by how much
    similar users liked them."""
    similarities = {
        other: user_similarity(user, other)
        for other in RATINGS if other != user
    }
    already_rated = set(RATINGS[user])

    scores = {}
    for other, sim in similarities.items():
        if sim <= 0:
            continue
        for mid, rating in RATINGS[other].items():
            if mid in already_rated:
                continue
            scores.setdefault(mid, [0.0, 0.0])
            scores[mid][0] += sim * rating   # weighted rating sum
            scores[mid][1] += sim            # total weight

    predictions = [
        (mid, total / weight) for mid, (total, weight) in scores.items() if weight > 0
    ]
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:top_n]


# ---------------- GUI ----------------
class RecommenderApp:
    def __init__(self, root):
        self.root = root
        root.title("Recommendation System AI — CodSoft Task 4")
        root.geometry("560x680")
        root.configure(bg="#1A1423")
        root.resizable(False, False)

        title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        label_font = tkfont.Font(family="Segoe UI", size=11)
        section_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")

        # ttk styling to match dark theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#2E2144", background="#2E2144",
                         foreground="#F4E9FF", arrowcolor="#F4E9FF")
        style.configure("TRadiobutton", background="#1A1423", foreground="#F4E9FF", font=label_font)

        # Header
        header = tk.Frame(root, bg="#2E2144", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="🎬  Recommendation AI", font=title_font, bg="#2E2144", fg="#FFD23F").pack(side="left", padx=20, pady=15)
        tk.Label(header, text="CodSoft AI • Task 4", font=("Segoe UI", 9), bg="#2E2144", fg="#C9B8E8").pack(side="right", padx=20)

        # Mode selection
        mode_frame = tk.Frame(root, bg="#1A1423")
        mode_frame.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(mode_frame, text="Choose a recommendation method:", font=section_font,
                 bg="#1A1423", fg="#F4E9FF").pack(anchor="w")

        self.mode_var = tk.StringVar(value="content")
        radio_row = tk.Frame(mode_frame, bg="#1A1423")
        radio_row.pack(anchor="w", pady=8)
        ttk.Radiobutton(radio_row, text="Content-Based (by movie you like)", variable=self.mode_var,
                         value="content", command=self.update_mode).pack(side="left", padx=(0, 20))
        ttk.Radiobutton(radio_row, text="Collaborative (by similar users)", variable=self.mode_var,
                         value="collab", command=self.update_mode).pack(side="left")

        # Selection area (changes based on mode)
        self.select_frame = tk.Frame(root, bg="#2E2144")
        self.select_frame.pack(fill="x", padx=20, pady=15)

        self.select_label = tk.Label(self.select_frame, text="", font=label_font,
                                      bg="#2E2144", fg="#F4E9FF")
        self.select_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.combo_var = tk.StringVar()
        self.combo = ttk.Combobox(self.select_frame, textvariable=self.combo_var,
                                   state="readonly", font=label_font, width=40)
        self.combo.pack(padx=15, pady=(0, 15))

        get_btn = tk.Button(root, text="✨ Get Recommendations", font=("Segoe UI", 10, "bold"),
                             bg="#FFD23F", fg="#1A1423", relief="flat", activebackground="#F0C020",
                             cursor="hand2", command=self.get_recommendations, padx=15, pady=8)
        get_btn.pack(pady=5)

        # Results area
        results_label = tk.Label(root, text="Recommended for you:", font=section_font,
                                  bg="#1A1423", fg="#F4E9FF")
        results_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.results_frame = tk.Frame(root, bg="#1A1423")
        self.results_frame.pack(fill="both", expand=True, padx=20)

        self.update_mode()

    def update_mode(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if self.mode_var.get() == "content":
            self.select_label.config(text="Pick a movie you like:")
            self.combo["values"] = [f"{mid} — {info['title']}" for mid, info in MOVIES.items()]
        else:
            self.select_label.config(text="Pick a user:")
            self.combo["values"] = list(RATINGS.keys())
        self.combo.current(0)

    def get_recommendations(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()
        selection = self.combo_var.get()
        if not selection:
            return

        if mode == "content":
            movie_id = int(selection.split(" — ")[0])
            results = content_based_recommend(movie_id)
            if not results:
                self.add_result_row("No similar movies found.", "")
            for mid, score in results:
                genres = ", ".join(sorted(MOVIES[mid]["genres"]))
                self.add_result_row(MOVIES[mid]["title"], f"{genres}  •  match {score:.0%}")
        else:
            user = selection
            results = collaborative_recommend(user)
            if not results:
                self.add_result_row("Not enough data yet.", "Rate more movies or pick another user.")
            for mid, predicted in results:
                genres = ", ".join(sorted(MOVIES[mid]["genres"]))
                self.add_result_row(MOVIES[mid]["title"], f"{genres}  •  predicted rating {predicted:.1f}/5")

    def add_result_row(self, title, subtitle):
        row = tk.Frame(self.results_frame, bg="#2E2144")
        row.pack(fill="x", pady=4)
        tk.Label(row, text=title, font=("Segoe UI", 11, "bold"), bg="#2E2144", fg="#FFD23F",
                 anchor="w", padx=12, pady=8).pack(fill="x")
        if subtitle:
            tk.Label(row, text=subtitle, font=("Segoe UI", 9), bg="#2E2144", fg="#C9B8E8",
                     anchor="w", padx=12, pady=(0, 8)).pack(fill="x")


if __name__ == "__main__":
    root = tk.Tk()
    app = RecommenderApp(root)
    root.mainloop()