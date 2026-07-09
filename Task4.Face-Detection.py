"""
CodSoft AI Internship - Task 5: Face Detection & Recognition AI (GUI Version)
Detection : Haar Cascade classifier (pre-trained, ships with OpenCV)
Recognition: LBPH (Local Binary Patterns Histograms) face recognizer —
             a lightweight, classic technique you train live on a few
             photos of each person (a simpler cousin of Siamese/ArcFace
             embedding-based recognition, but runs instantly with no GPU).

Run: python task5_face_recognition_ai.py

Dependencies (install first):
    pip install opencv-contrib-python pillow numpy

Note: opencv-contrib-python (not plain opencv-python) is required because
the LBPH recognizer lives in the "contrib" face module (cv2.face).
"""

import tkinter as tk
from tkinter import font as tkfont, filedialog, messagebox, simpledialog
import threading
import sys
import os
import pickle

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageTk
except ImportError as e:
    tk_root = tk.Tk()
    tk_root.withdraw()
    messagebox.showerror(
        "Missing dependency",
        "Required packages are not installed.\n\n"
        "Run this in your terminal:\n"
        "pip install opencv-contrib-python pillow numpy\n\n"
        f"Details: {e}"
    )
    sys.exit(1)

FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
DB_FILE = "face_db.pkl"  # stores trained face samples + labels between runs


def detect_faces(gray_frame):
    """Pre-trained Haar Cascade: returns list of (x, y, w, h) face boxes."""
    return FACE_CASCADE.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))


class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        root.title("Face Detection & Recognition AI — CodSoft Task 5")
        root.geometry("620x740")
        root.configure(bg="#071A21")
        root.resizable(False, False)

        title_font = tkfont.Font(family="Segoe UI", size=18, weight="bold")
        status_font = tkfont.Font(family="Segoe UI", size=11)

        self.cap = None
        self.webcam_running = False
        self.tk_image = None
        self.mode = None  # "detect" or "recognize"

        # face_samples: {name: [gray face crops...]}, loaded from disk if present
        self.face_samples = {}
        self.recognizer = None
        self.label_map = {}  # int label -> name
        self.load_db()

        # Header
        header = tk.Frame(root, bg="#0E3A4A", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="🙂  Face Detection & Recognition", font=title_font, bg="#0E3A4A", fg="#4CE0D2").pack(side="left", padx=15, pady=15)
        tk.Label(header, text="CodSoft AI • Task 5", font=("Segoe UI", 9), bg="#0E3A4A", fg="#8FCBD9").pack(side="right", padx=20)

        # Preview area
        preview_frame = tk.Frame(root, bg="#0E2A35", width=580, height=400)
        preview_frame.pack(padx=20, pady=15)
        preview_frame.pack_propagate(False)
        self.preview_label = tk.Label(preview_frame, text="No feed yet\n\nChoose an option below",
                                       bg="#0E2A35", fg="#4C7A8A", font=status_font, justify="center")
        self.preview_label.pack(expand=True)

        # Status bar
        self.status_var = tk.StringVar(value=f"Ready. {len(self.face_samples)} people registered.")
        tk.Label(root, textvariable=self.status_var, font=status_font, bg="#071A21", fg="#8FCBD9").pack(pady=(0, 10))

        # --- Detection controls ---
        section1 = tk.Label(root, text="Face Detection (Haar Cascade)", font=("Segoe UI", 11, "bold"),
                             bg="#071A21", fg="#4CE0D2")
        section1.pack(anchor="w", padx=20)
        row1 = tk.Frame(root, bg="#071A21")
        row1.pack(fill="x", padx=20, pady=(5, 15))
        self.mk_button(row1, "📁 Detect in Image", self.detect_in_image).pack(side="left", padx=(0, 8))
        self.mk_button(row1, "🎥 Detect via Webcam", self.start_detect_webcam).pack(side="left", padx=8)
        self.mk_button(row1, "⏹ Stop Webcam", self.stop_webcam, bg="#4C1F2B", fg="#FF8FA3").pack(side="left", padx=8)

        # --- Recognition controls ---
        section2 = tk.Label(root, text="Face Recognition (LBPH)", font=("Segoe UI", 11, "bold"),
                             bg="#071A21", fg="#4CE0D2")
        section2.pack(anchor="w", padx=20)
        row2 = tk.Frame(root, bg="#071A21")
        row2.pack(fill="x", padx=20, pady=(5, 5))
        self.mk_button(row2, "➕ Register Face (Webcam)", self.register_face).pack(side="left", padx=(0, 8))
        self.mk_button(row2, "🔍 Recognize via Webcam", self.start_recognize_webcam).pack(side="left", padx=8)

        row3 = tk.Frame(root, bg="#071A21")
        row3.pack(fill="x", padx=20, pady=(5, 10))
        self.mk_button(row3, "🗑 Clear All Registered Faces", self.clear_db, bg="#4C1F2B", fg="#FF8FA3").pack(side="left")

        # Registered people list
        tk.Label(root, text="Registered people:", font=("Segoe UI", 10, "bold"),
                 bg="#071A21", fg="#8FCBD9").pack(anchor="w", padx=20, pady=(10, 0))
        self.people_var = tk.StringVar()
        tk.Label(root, textvariable=self.people_var, font=status_font, bg="#071A21",
                 fg="#4CE0D2", wraplength=560, justify="left").pack(anchor="w", padx=20, pady=(2, 10))
        self.refresh_people_label()

    def mk_button(self, parent, text, command, bg="#1A6E7E", fg="#FFFFFF"):
        return tk.Button(parent, text=text, font=("Segoe UI", 9, "bold"), bg=bg, fg=fg,
                          relief="flat", activebackground="#155A68", cursor="hand2",
                          command=command, padx=10, pady=6)

    # ---------------- Persistence ----------------
    def load_db(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "rb") as f:
                    self.face_samples = pickle.load(f)
            except Exception:
                self.face_samples = {}

    def save_db(self):
        with open(DB_FILE, "wb") as f:
            pickle.dump(self.face_samples, f)

    def refresh_people_label(self):
        if self.face_samples:
            self.people_var.set(", ".join(f"{name} ({len(s)} samples)" for name, s in self.face_samples.items()))
        else:
            self.people_var.set("(none yet — use 'Register Face' to add someone)")

    def clear_db(self):
        if messagebox.askyesno("Confirm", "Remove all registered faces?"):
            self.face_samples = {}
            self.recognizer = None
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            self.refresh_people_label()
            self.status_var.set("Cleared all registered faces.")

    # ---------------- Image detection ----------------
    def detect_in_image(self):
        path = filedialog.askopenfilename(title="Select an image",
                                           filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            self.status_var.set("Could not read that image file.")
            return
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (76, 224, 210), 3)
        self.status_var.set(f"Detected {len(faces)} face(s) in image.")
        self.show_frame(img)

    # ---------------- Webcam: detection only ----------------
    def start_detect_webcam(self):
        self.mode = "detect"
        self._start_webcam()

    def start_recognize_webcam(self):
        if not self.face_samples:
            messagebox.showinfo("No data", "Register at least one person's face first.")
            return
        self.train_recognizer()
        self.mode = "recognize"
        self._start_webcam()

    def _start_webcam(self):
        if self.webcam_running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_var.set("Could not access webcam.")
            return
        self.webcam_running = True
        self.status_var.set("Webcam running — click 'Stop Webcam' to end.")
        self._webcam_loop()

    def stop_webcam(self):
        self.webcam_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.status_var.set("Webcam stopped.")

    def _webcam_loop(self):
        if not self.webcam_running or self.cap is None:
            return
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)
            for (x, y, w, h) in faces:
                label_text = "Face"
                color = (76, 224, 210)
                if self.mode == "recognize" and self.recognizer is not None:
                    face_crop = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
                    label_id, confidence = self.recognizer.predict(face_crop)
                    # Lower LBPH confidence = better match
                    if confidence < 75:
                        label_text = f"{self.label_map.get(label_id, '?')} ({confidence:.0f})"
                        color = (76, 224, 120)
                    else:
                        label_text = "Unknown"
                        color = (255, 143, 163)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, color, 2)
            self.show_frame(frame)
        self.root.after(30, self._webcam_loop)

    # ---------------- Registration ----------------
    def register_face(self):
        name = simpledialog.askstring("Register Face", "Enter this person's name:")
        if not name:
            return
        name = name.strip()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.status_var.set("Could not access webcam.")
            return

        self.status_var.set(f"Capturing samples for {name}... look at the camera.")
        self.root.update_idletasks()

        samples = []
        attempts = 0
        while len(samples) < 20 and attempts < 200:
            ret, frame = cap.read()
            attempts += 1
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)
            if len(faces) == 1:
                x, y, w, h = faces[0]
                face_crop = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
                samples.append(face_crop)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (76, 224, 210), 3)
            self.show_frame(frame)
            self.root.update()

        cap.release()

        if not samples:
            self.status_var.set("Couldn't capture a clear face. Try again with better lighting.")
            return

        self.face_samples.setdefault(name, []).extend(samples)
        self.save_db()
        self.refresh_people_label()
        self.recognizer = None  # force retrain next time
        self.status_var.set(f"Registered {len(samples)} samples for {name}.")

    def train_recognizer(self):
        images, labels = [], []
        self.label_map = {}
        for idx, (name, samples) in enumerate(self.face_samples.items()):
            self.label_map[idx] = name
            for face in samples:
                images.append(face)
                labels.append(idx)

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.train(images, np.array(labels))

    # ---------------- Display helper ----------------
    def show_frame(self, bgr_frame):
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img.thumbnail((560, 380))
        self.tk_image = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.tk_image, text="")


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()