"""
NAME: SIDDHARTH YADAV
ROLL NO: 2511CS04

MY Project Title: Monte Carlo Tree Search (MCTS) — Tic-Tac-Toe with GUI

How to We, Run: p.py
"""

import math
import random
import tkinter as tk
from tkinter import messagebox
import threading


#  GAME LOGIC 


WINNING_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], #rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], #columns
    [0, 4, 8], [2, 4, 6],            #diagonals        
]

def check_winner(board, player):
    return any(all(board[i] == player for i in line) for line in WINNING_LINES)

def get_winning_line(board, player):
    for line in WINNING_LINES:
        if all(board[i] == player for i in line):
            return line
    return None

def is_draw(board):
    return all(cell is not None for cell in board)

def get_empty_cells(board):
    return [i for i, cell in enumerate(board) if cell is None]

def is_terminal(board):
    return check_winner(board, 'X') or check_winner(board, 'O') or is_draw(board)

def get_result(board):
    if check_winner(board, 'X'): return 'X'
    if check_winner(board, 'O'): return 'O'
    return None

def other_player(player):
    return 'O' if player == 'X' else 'X'


#  MCTS ALGORITHM


class MCTSNode:
    def __init__(self, state, player, move=None, parent=None):
        self.state   = state[:]
        self.player  = player
        self.move    = move
        self.parent  = parent
        self.children = []
        self.wins    = 0
        self.visits  = 0
        self.untried = get_empty_cells(state)

    def is_fully_expanded(self):
        return len(self.untried) == 0

    def ucb1(self, c=math.sqrt(2)):
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child_ucb1(self):
        return max(self.children, key=lambda n: n.ucb1())

    def most_visited_child(self):
        return max(self.children, key=lambda n: n.visits)


def selection(root):
    node = root
    while not is_terminal(node.state) and node.is_fully_expanded():
        node = node.best_child_ucb1()
    return node

def expansion(node):
    if is_terminal(node.state) or not node.untried:
        return node
    move = random.choice(node.untried)
    node.untried.remove(move)
    new_state = node.state[:]
    new_state[move] = node.player
    child = MCTSNode(new_state, other_player(node.player), move, node)
    node.children.append(child)
    return child

def simulation(node):
    state = node.state[:]
    current = node.player
    while not is_terminal(state):
        move = random.choice(get_empty_cells(state))
        state[move] = current
        current = other_player(current)
    return get_result(state)

def backpropagation(node, result, ai_player):
    while node is not None:
        node.visits += 1
        if result == ai_player:
            node.wins += 1
        node = node.parent

def mcts(board, ai_player, iterations=500):
    root = MCTSNode(board, ai_player)
    for _ in range(iterations):
        sel  = selection(root)
        exp  = expansion(sel)
        res  = simulation(exp)
        backpropagation(exp, res, ai_player)
    best = root.most_visited_child()
    # Return move scores for heat map
    scores = {c.move: c.visits for c in root.children}
    return best.move, scores


#  GUI APPLICATION


# Color palette
BG         = "#0f0f1a"
PANEL_BG   = "#1a1a2e"
CELL_BG    = "#16213e"
CELL_HOVER = "#1f2f50"
X_COLOR    = "#ff0000"   
O_COLOR    = "#06d6a0"   
ACCENT     = "#f8c12a"
TEXT_COLOR = "#e8e8f0"
MUTED      = "#6060a0"
GREEN      = "#06d6a0"
WIN_COLOR  = "#f8c12a"

DIFFICULTY = {"Easy": 100, "Medium": 500, "Hard": 2000}

class MCTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MCTS Tic-Tac-Toe  |  Siddharth Yadav  |  2511CS04")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board        = [None] * 9
        self.game_over    = False
        self.ai_player    = 'O'
        self.human_player = 'X'
        self.difficulty   = tk.StringVar(value="Medium")
        self.scores_var   = [0] * 9
        self.show_heat    = tk.BooleanVar(value=False)
        self.stats        = {"iterations": 0, "best_wr": 0.0, "ai_wins": 0, "human_wins": 0, "draws": 0}

        self._build_ui()
        self.update_status("My turn!  WE are X", ACCENT)

    # HERE WE BUILD UI 

    def _build_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=BG, pady=10)
        title_frame.pack(fill="x", padx=20)

        tk.Label(title_frame, text="MONTE CARLO TREE SEARCH",
                 font=("Courier", 18, "bold"), bg=BG, fg=ACCENT).pack()
        tk.Label(title_frame, text="Tic-Tac-Toe AI  ·  Siddharth Yadav  ·  Roll: 2511CS04",
                 font=("Courier", 9), bg=BG, fg=MUTED).pack()

        # Main 3-column layout
        main = tk.Frame(self.root, bg=BG)
        main.pack(padx=15, pady=5)

        self._build_left_panel(main)
        self._build_center(main)
        self._build_right_panel(main)

    def _build_left_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG, bd=0, relief="flat",
                         width=200, padx=12, pady=12)
        frame.grid(row=0, column=0, sticky="ns", padx=(0,10))
        frame.grid_propagate(False)

        tk.Label(frame, text="◉  MCTS PHASES",
                 font=("Courier", 9, "bold"), bg=PANEL_BG, fg=ACCENT).pack(anchor="w", pady=(0,10))

        self.phase_labels = {}
        phases = [
            ("sel",  "1. SELECTION",       "UCB1 tree traversal",     "#f8c12a"),
            ("exp",  "2. EXPANSION",        "Add new child node",      "#ff4d6d"),
            ("sim",  "3. SIMULATION",       "Random rollout",          "#4cc9f0"),
            ("back", "4. BACKPROPAGATION",  "Update win/visit counts", "#06d6a0"),
        ]
        for key, title, desc, color in phases:
            box = tk.Frame(frame, bg=CELL_BG, pady=6, padx=8, bd=0)
            box.pack(fill="x", pady=3)
            tk.Label(box, text=title, font=("Courier", 8, "bold"),
                     bg=CELL_BG, fg=color).pack(anchor="w")
            tk.Label(box, text=desc, font=("Courier", 7),
                     bg=CELL_BG, fg=MUTED, wraplength=160, justify="left").pack(anchor="w")
            self.phase_labels[key] = box

        # HERE WE :UCB1 formula box
        tk.Label(frame, text="◉  UCB1 FORMULA",
                 font=("Courier", 9, "bold"), bg=PANEL_BG, fg=GREEN).pack(anchor="w", pady=(18,6))
        formula_box = tk.Frame(frame, bg=CELL_BG, pady=8, padx=8)
        formula_box.pack(fill="x")
        tk.Label(formula_box, text="w/n + C·√(ln N / n)",
                 font=("Courier", 10, "bold"), bg=CELL_BG, fg=GREEN).pack()
        tk.Label(formula_box,
                 text="w=wins  n=visits\nN=parent visits  C=√2",
                 font=("Courier", 7), bg=CELL_BG, fg=MUTED, justify="center").pack(pady=(4,0))

    def _build_center(self, parent):
        frame = tk.Frame(parent, bg=BG)
        frame.grid(row=0, column=1)

        # Status bar
        self.status_frame = tk.Frame(frame, bg=PANEL_BG, pady=8, padx=16)
        self.status_frame.pack(fill="x", pady=(0, 10))
        self.status_label = tk.Label(self.status_frame, text="",
                                     font=("Courier", 11, "bold"),
                                     bg=PANEL_BG, fg=ACCENT, width=34)
        self.status_label.pack()

        # Board
        board_outer = tk.Frame(frame, bg=PANEL_BG, padx=16, pady=16)
        board_outer.pack()
        self.buttons = []
        for i in range(9):
            btn = tk.Button(board_outer, text="", width=5, height=2,
                            font=("Courier", 26, "bold"),
                            bg=CELL_BG, fg=TEXT_COLOR,
                            activebackground=CELL_HOVER,
                            relief="flat", bd=0, cursor="hand2",
                            command=lambda idx=i: self.human_move(idx))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, ipadx=8, ipady=8)
            btn.bind("<Enter>", lambda e, b=btn: self._hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._hover(b, False))
            self.buttons.append(btn)

        # Controls
        ctrl = tk.Frame(frame, bg=BG, pady=10)
        ctrl.pack()

        # Difficulty
        tk.Label(ctrl, text="Difficulty:", font=("Courier", 9),
                 bg=BG, fg=MUTED).grid(row=0, column=0, padx=5)
        for i, diff in enumerate(["Easy", "Medium", "Hard"]):
            rb = tk.Radiobutton(ctrl, text=diff, variable=self.difficulty, value=diff,
                                font=("Courier", 9, "bold"),
                                bg=BG, fg=TEXT_COLOR, selectcolor=PANEL_BG,
                                activebackground=BG, activeforeground=ACCENT,
                                indicatoron=False, padx=10, pady=4,
                                relief="flat", bd=1,
                                command=self.reset_game)
            rb.grid(row=0, column=i+1, padx=3)

        # Buttons row
        btn_frame = tk.Frame(frame, bg=BG, pady=8)
        btn_frame.pack()

        tk.Button(btn_frame, text="↺  NEW GAME",
                  font=("Courier", 9, "bold"), bg=ACCENT, fg="#000",
                  activebackground="#ffd060", relief="flat", padx=14, pady=6,
                  cursor="hand2", command=self.reset_game).pack(side="left", padx=5)

        self.heat_btn = tk.Button(btn_frame, text="🌡  HEAT MAP: OFF",
                                   font=("Courier", 9), bg=PANEL_BG, fg=TEXT_COLOR,
                                   activebackground=CELL_HOVER, relief="flat",
                                   padx=14, pady=6, cursor="hand2",
                                   command=self.toggle_heat)
        self.heat_btn.pack(side="left", padx=5)

        # Score bar
        score_frame = tk.Frame(frame, bg=PANEL_BG, pady=8, padx=16)
        score_frame.pack(fill="x", pady=(6, 0))
        tk.Label(score_frame, text="SCORE", font=("Courier", 8, "bold"),
                 bg=PANEL_BG, fg=MUTED).pack()
        scores_inner = tk.Frame(score_frame, bg=PANEL_BG)
        scores_inner.pack()
        self.score_you   = tk.Label(scores_inner, text="YOU: 0",
                                     font=("Courier", 11, "bold"), bg=PANEL_BG, fg=X_COLOR)
        self.score_draw  = tk.Label(scores_inner, text="DRAW: 0",
                                     font=("Courier", 11, "bold"), bg=PANEL_BG, fg=MUTED)
        self.score_ai    = tk.Label(scores_inner, text="AI: 0",
                                     font=("Courier", 11, "bold"), bg=PANEL_BG, fg=O_COLOR)
        self.score_you.pack(side="left", padx=14)
        self.score_draw.pack(side="left", padx=14)
        self.score_ai.pack(side="left", padx=14)

    def _build_right_panel(self, parent):
        frame = tk.Frame(parent, bg=PANEL_BG, bd=0,
                         width=200, padx=12, pady=12)
        frame.grid(row=0, column=2, sticky="ns", padx=(10,0))
        frame.grid_propagate(False)

        tk.Label(frame, text="◉  AI STATISTICS",
                 font=("Courier", 9, "bold"), bg=PANEL_BG, fg=O_COLOR).pack(anchor="w", pady=(0,10))

        self.stat_labels = {}
        stats_info = [
            ("iterations", "Iterations",  "0",   ACCENT),
            ("best_wr",    "Best Win %",  "—",   GREEN),
            ("ai_move",    "AI's Move",   "—",   O_COLOR),
            ("nodes",      "Nodes Est.",  "0",   "#b088f9"),
        ]
        for key, label, default, color in stats_info:
            box = tk.Frame(frame, bg=CELL_BG, pady=6, padx=10)
            box.pack(fill="x", pady=3)
            tk.Label(box, text=label, font=("Courier", 7),
                     bg=CELL_BG, fg=MUTED).pack(anchor="w")
            lbl = tk.Label(box, text=default, font=("Courier", 14, "bold"),
                           bg=CELL_BG, fg=color)
            lbl.pack(anchor="w")
            self.stat_labels[key] = lbl

        # Move log
        tk.Label(frame, text="◉  MOVE LOG",
                 font=("Courier", 9, "bold"), bg=PANEL_BG, fg=ACCENT).pack(anchor="w", pady=(16,6))
        log_frame = tk.Frame(frame, bg=CELL_BG, pady=6, padx=8)
        log_frame.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_frame, font=("Courier", 8),
                                bg=CELL_BG, fg=TEXT_COLOR,
                                relief="flat", bd=0, width=22, height=10,
                                state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("ai",    foreground=O_COLOR)
        self.log_text.tag_config("human", foreground=X_COLOR)
        self.log_text.tag_config("info",  foreground=MUTED)

    # HOVER EFFECT 

    def _hover(self, btn, entering):
        if btn["text"] == "" and not self.game_over:
            btn.config(bg=CELL_HOVER if entering else CELL_BG)

    # PHASE HIGHLIGHT 

    def highlight_phase(self, key):
        colors = {"sel": "#f8c12a", "exp": "#ff4d6d", "sim": "#4cc9f0", "back": "#06d6a0"}
        for k, box in self.phase_labels.items():
            if k == key:
                box.config(bg=colors.get(k, CELL_BG))
                for w in box.winfo_children():
                    w.config(bg=colors.get(k, CELL_BG))
            else:
                box.config(bg=CELL_BG)
                for w in box.winfo_children():
                    w.config(bg=CELL_BG)

    def clear_phases(self):
        for box in self.phase_labels.values():
            box.config(bg=CELL_BG)
            for w in box.winfo_children():
                w.config(bg=CELL_BG)

    # STATUS 

    def update_status(self, msg, color=TEXT_COLOR):
        self.status_label.config(text=msg, fg=color)

    # GAME LOGIC 

    def human_move(self, idx):
        if self.game_over or self.board[idx] is not None:
            return
        self.board[idx] = self.human_player
        self.buttons[idx].config(text="X", fg=X_COLOR, state="disabled")
        self.add_log(f"You → cell {idx+1}", "human")

        if self.check_end(self.human_player):
            return
        self.update_status("AI is thinking…", O_COLOR)
        self.disable_board()

        # Run AI in background thread so GUI doesn't freeze
        threading.Thread(target=self.ai_move_thread, daemon=True).start()

    def ai_move_thread(self):
        iters = DIFFICULTY[self.difficulty.get()]

        # Animate phases
        for phase in ["sel", "exp", "sim", "back"]:
            self.root.after(0, self.highlight_phase, phase)
            import time; time.sleep(0.18)

        move, scores = mcts(self.board, self.ai_player, iters)
        self.root.after(0, self.apply_ai_move, move, scores, iters)

    def apply_ai_move(self, move, scores, iters):
        self.clear_phases()
        self.board[move] = self.ai_player
        self.buttons[move].config(text="O", fg=O_COLOR, state="disabled")
        self.scores_var = scores

        # Update stats
        best_node_visits = max(scores.values()) if scores else 0
        best_wr_raw = scores.get(move, 0)
        self.stat_labels["iterations"].config(text=str(iters))
        self.stat_labels["best_wr"].config(text=f"{(best_node_visits/(iters+1)*100):.0f}%")
        self.stat_labels["ai_move"].config(text=f"Cell {move+1}")
        self.stat_labels["nodes"].config(text=f"~{iters*2}")

        self.add_log(f"AI  → cell {move+1}  ({iters} sims)", "ai")

        if self.show_heat.get():
            self.apply_heat()

        if self.check_end(self.ai_player):
            return

        self.enable_board()
        self.update_status("Our turn!  We are X", ACCENT)

    def check_end(self, player):
        if check_winner(self.board, player):
            self.game_over = True
            line = get_winning_line(self.board, player)
            for i in line:
                self.buttons[i].config(bg=WIN_COLOR, fg="#000")
            if player == self.human_player:
                self.stats["human_wins"] += 1
                self.update_status("🎉  WE WIN!  MCTS Defeated!", X_COLOR)
                self.add_log("── WE WIN! ──", "human")
            else:
                self.stats["ai_wins"] += 1
                self.update_status("🤖  AI WINS! We Try harder!", O_COLOR)
                self.add_log("── AI WINS! ──", "ai")
            self.update_scores()
            return True

        if is_draw(self.board):
            self.game_over = True
            self.stats["draws"] += 1
            self.update_status("🤝  DRAW!  MCTS played perfectly.", MUTED)
            self.add_log("── DRAW! ──", "info")
            self.update_scores()
            return True

        return False

    def disable_board(self):
        for btn in self.buttons:
            if btn["text"] == "":
                btn.config(state="disabled", cursor="")

    def enable_board(self):
        for i, btn in enumerate(self.buttons):
            if self.board[i] is None:
                btn.config(state="normal", cursor="hand2")

    #  HEAT MAP 

    def toggle_heat(self):
        self.show_heat.set(not self.show_heat.get())
        if self.show_heat.get():
            self.heat_btn.config(text="🌡  HEAT MAP: ON", fg=GREEN)
            self.apply_heat()
        else:
            self.heat_btn.config(text="🌡  HEAT MAP: OFF", fg=TEXT_COLOR)
            self.clear_heat()

    def apply_heat(self):
        if not self.scores_var:
            return
        max_v = max(self.scores_var.values()) if self.scores_var else 1
        for i, btn in enumerate(self.buttons):
            if self.board[i] is None and max_v > 0:
                intensity = self.scores_var.get(i, 0) / max_v
                r = int(22 + intensity * (6 - 22))
                g = int(33 + intensity * (214 - 33))
                b = int(62 + intensity * (160 - 62))
                color = f"#{r:02x}{g:02x}{b:02x}"
                btn.config(bg=color)

    def clear_heat(self):
        for i, btn in enumerate(self.buttons):
            if self.board[i] is None:
                btn.config(bg=CELL_BG)

    # SCORES 

    def update_scores(self):
        self.score_you.config(text=f"YOU: {self.stats['human_wins']}")
        self.score_draw.config(text=f"DRAW: {self.stats['draws']}")
        self.score_ai.config(text=f"AI: {self.stats['ai_wins']}")

    # LOG 

    def add_log(self, msg, tag="info"):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # RESET 

    def reset_game(self):
        self.board     = [None] * 9
        self.game_over = False
        self.scores_var = {}
        self.clear_phases()
        self.clear_heat()

        for btn in self.buttons:
            btn.config(text="", fg=TEXT_COLOR, bg=CELL_BG,
                       state="normal", cursor="hand2")

        self.stat_labels["iterations"].config(text="0")
        self.stat_labels["best_wr"].config(text="—")
        self.stat_labels["ai_move"].config(text="—")
        self.stat_labels["nodes"].config(text="0")

        self.update_status("Our turn!  We are X", ACCENT)
        self.add_log("── NEW GAME ──", "info")



#  ENTRY POINT


if __name__ == "__main__":
    root = tk.Tk()
    app  = MCTSApp(root)
    root.mainloop()