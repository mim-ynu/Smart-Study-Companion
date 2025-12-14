main.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import pyttsx3  # pip install pyttsx3
import random
import json
import os

# TTS Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Data files
VOCAB_FILE = "vocabulary.json"
if not os.path.exists(VOCAB_FILE):
    with open(VOCAB_FILE, "w") as f:
        json.dump([], f)

# Main App
class StudyCompanion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Study Companion")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.timer_frame = ttk.Frame(notebook)
        self.tts_frame = ttk.Frame(notebook)
        self.mcq_frame = ttk.Frame(notebook)
        self.vocab_frame = ttk.Frame(notebook)

        notebook.add(self.timer_frame, text="Pomodoro Timer")
        notebook.add(self.tts_frame, text="Text-to-Speech")
        notebook.add(self.mcq_frame, text="MCQ Generator")
        notebook.add(self.vocab_frame, text="Vocabulary Builder")

        self.setup_timer()
        self.setup_tts()
        self.setup_mcq()
        self.setup_vocab()

    # 1. Pomodoro Timer
    def setup_timer(self):
        self.work_time = 25 * 60
        self.break_time = 5 * 60
        self.long_break = 15 * 60
        self.sessions = 0
        self.remaining = self.work_time
        self.running = False

        tk.Label(self.timer_frame, text="Pomodoro Timer", font=("Helvetica", 20)).pack(pady=20)

        self.timer_label = tk.Label(self.timer_frame, text="25:00", font=("Helvetica", 48), bg="red", fg="white")
        self.timer_label.pack(pady=20)

        btn_frame = tk.Frame(self.timer_frame)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Start", command=self.start_timer).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Reset", command=self.reset_timer).grid(row=0, column=1, padx=10)

        self.checkmarks = tk.Label(self.timer_frame, text="", font=("Helvetica", 20))
        self.checkmarks.pack()

    def start_timer(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.countdown).start()

    def countdown(self):
        while self.remaining > 0 and self.running:
            mins, secs = divmod(self.remaining, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            self.remaining -= 1

        if self.remaining == 0:
            self.sessions += 1
            if self.sessions % 4 == 0:
                messagebox.showinfo("Long Break", "Take a long break!")
                self.remaining = self.long_break
            else:
                messagebox.showinfo("Break", "Take a short break!")
                self.remaining = self.break_time
            self.checkmarks.config(text="✓" * self.sessions)
            engine.say("Time's up!")
            engine.runAndWait()
            self.running = False

    def reset_timer(self):
        self.running = False
        self.remaining = self.work_time
        self.timer_label.config(text="25:00")

    # 2. Text-to-Speech
    def setup_tts(self):
        tk.Label(self.tts_frame, text="Text-to-Speech Reader", font=("Helvetica", 20)).pack(pady=20)
        self.tts_text = tk.Text(self.tts_frame, height=10)
        self.tts_text.pack(pady=10, fill="both", expand=True)
        tk.Button(self.tts_frame, text="Speak", command=self.speak_text).pack(pady=10)

    def speak_text(self):
        text = self.tts_text.get("1.0", tk.END).strip()
        if text:
            threading.Thread(target=lambda: (engine.say(text), engine.runAndWait())).start()

    # 3. MCQ Generator
    def setup_mcq(self):
        tk.Label(self.mcq_frame, text="MCQ Generator", font=("Helvetica", 20)).pack(pady=20)
        tk.Label(self.mcq_frame, text="Paste notes/text:").pack()
        self.notes_text = tk.Text(self.mcq_frame, height=10)
        self.notes_text.pack(pady=10, fill="both", expand=True)
        tk.Button(self.mcq_frame, text="Generate 5 MCQs", command=self.generate_mcq).pack(pady=10)
        self.mcq_display = tk.Text(self.mcq_frame, height=15)
        self.mcq_display.pack(pady=10, fill="both", expand=True)

    def generate_mcq(self):
        notes = self.notes_text.get("1.0", tk.END).strip()
        if not notes:
            return
        sentences = [s.strip() for s in notes.split('.') if s.strip()]
        mcqs = []
        for sent in random.sample(sentences, min(5, len(sentences))):
            options = [sent, "Wrong 1", "Wrong 2", "Wrong 3"]
            random.shuffle(options)
            correct = options.index(sent)
            mcqs.append(f"Q: {sent}?\nA) {options[0]} B) {options[1]} C) {options[2]} D) {options[3]}\nCorrect: {chr(65 + correct)}")
        self.mcq_display.delete("1.0", tk.END)
        self.mcq_display.insert(tk.END, "\n\n".join(mcqs))
        engine.say("MCQs generated!")

    # 4. Vocabulary Builder
    def setup_vocab(self):
        tk.Label(self.vocab_frame, text="Vocabulary Builder", font=("Helvetica", 20)).pack(pady=20)
        tk.Label(self.vocab_frame, text="Word:").pack()
        self.word_entry = tk.Entry(self.vocab_frame)
        self.word_entry.pack()
        tk.Label(self.vocab_frame, text="Meaning:").pack()
        self.mean_entry = tk.Entry(self.vocab_frame)
        self.mean_entry.pack()
        tk.Button(self.vocab_frame, text="Add Word", command=self.add_word).pack(pady=10)
        tk.Button(self.vocab_frame, text="Review Flashcards", command=self.review_vocab).pack(pady=10)
        self.flash_label = tk.Label(self.vocab_frame, text="", font=("Helvetica", 24), wraplength=700)
        self.flash_label.pack(pady=30)

    def add_word(self):
        word = self.word_entry.get().strip()
        meaning = self.mean_entry.get().strip()
        if word and meaning:
            with open(VOCAB_FILE, "r") as f:
                vocab = json.load(f)
            vocab.append({"word": word, "meaning": meaning})
            with open(VOCAB_FILE, "w") as f:
                json.dump(vocab, f)
            messagebox.showinfo("Success", f"{word} added!")
            self.word_entry.delete(0, tk.END)
            self.mean_entry.delete(0, tk.END)
            engine.say(f"Added {word}")

    def review_vocab(self):
        with open(VOCAB_FILE) as f:
            vocab = json.load(f)
        if not vocab:
            messagebox.showwarning("Empty", "Add words first!")
            return
        card = random.choice(vocab)
        self.flash_label.config(text=f"Word: {card['word']}\n\nClick for meaning")
        def show_meaning():
            self.flash_label.config(text=f"Word: {card['word']}\nMeaning: {card['meaning']}")
            engine.say(f"{card['word']} means {card['meaning']}")
        tk.Button(self.vocab_frame, text="Show Meaning", command=show_meaning).pack()
        tk.Button(self.vocab_frame, text="Next", command=self.review_vocab).pack()

if __name__ == "__main__":
    app = StudyCompanion()
    app.mainloop()
