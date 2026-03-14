"""
NAME: SIDDHARTH YADAV
ROLL NO:2511CS04

MY Project1 Title::Monte Carlo Tree Search (MCTS) — Tic-Tac-Toe

HERE WE , Describe Briefly ,HOW MCTS WORKS (4 phases every iteration):
  1. SELECTION      — Walk down the tree using UCB1 to find a promising node
  2. EXPANSION      — Add a new unexplored child node
  3. SIMULATION     — Play a random game ("rollout") to the end
  4. BACKPROPAGATION— Update wins/visits count from leaf back to root

How We Run: python mcts_tictactoe.py
"""

import math
import random


#  GAME LOGIC

WINNING_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],   # rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],   # columns
    [0, 4, 8], [2, 4, 6],              # diagonals
]


def check_winner(board: list, player: str) -> bool:
    """Return True if 'player' has three in a row."""
    return any(all(board[i] == player for i in line) for line in WINNING_LINES)


def is_draw(board: list) -> bool:
    """Return True if the board is full (no winner)."""
    return all(cell is not None for cell in board)


def get_empty_cells(board: list) -> list:
    """Return indices of empty cells."""
    return [i for i, cell in enumerate(board) if cell is None]


def is_terminal(board: list) -> bool:
    """Return True if the game is over (win or draw)."""
    return check_winner(board, 'X') or check_winner(board, 'O') or is_draw(board)


def get_result(board: list) -> str | None:
    """Return 'X', 'O', or None (draw) for a finished game."""
    if check_winner(board, 'X'):
        return 'X'
    if check_winner(board, 'O'):
        return 'O'
    return None  # draw


def other_player(player: str) -> str:
    return 'O' if player == 'X' else 'X'

#  MCTS NODE


class MCTSNode:
    

    def __init__(self, state: list, player: str, move=None, parent=None):
        self.state = state[:]          # copy of board
        self.player = player           # whose turn it is next
        self.move = move               # move that created this node
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried = get_empty_cells(state)  # unexplored moves

    def is_fully_expanded(self) -> bool:
        """True when every possible move has a child node."""
        return len(self.untried) == 0

    def ucb1(self, exploration_c: float = math.sqrt(2)) -> float:
        """
        Here We Define,,Upper Confidence Bound 1 formula:
        """
        if self.visits == 0:
            return float('inf')   # always try unvisited nodes first
        exploit = self.wins / self.visits
        explore = exploration_c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploit + explore

    def best_child_ucb1(self) -> 'MCTSNode':
        """WE ,Select child with highest UCB1 score"""
        return max(self.children, key=lambda c: c.ucb1())

    def most_visited_child(self) -> 'MCTSNode':
        """WE,Select child with most visits for final move selection."""
        return max(self.children, key=lambda c: c.visits)

    def __repr__(self):
        wr = self.wins / self.visits if self.visits else 0
        return f"Node(move={self.move}, visits={self.visits}, win%={wr:.1%})"



#  THE 4 PHASES OF MCTS

def selection(root: MCTSNode) -> MCTSNode:

    #PHASE 1 — SELECTION

    node = root
    while not is_terminal(node.state) and node.is_fully_expanded():
        node = node.best_child_ucb1()
    return node


def expansion(node: MCTSNode) -> MCTSNode:

    #PHASE 2 — EXPANSION
    
    if is_terminal(node.state) or not node.untried:
        return node  # nothing to expand

    move = random.choice(node.untried)
    node.untried.remove(move)

    new_state = node.state[:]
    new_state[move] = other_player(node.player) 
    new_state = node.state[:]
    new_state[move] = node.player                # current node's player makes the move
    child = MCTSNode(
        state=new_state,
        player=other_player(node.player),        # next player's turn
        move=move,
        parent=node
    )
    node.children.append(child)
    return child


def simulation(node: MCTSNode) -> str | None:
    
    #PHASE 3 — SIMULATION
    
    state = node.state[:]
    current_player = node.player   # whose turn it is

    while not is_terminal(state):
        move = random.choice(get_empty_cells(state))
        state[move] = current_player
        current_player = other_player(current_player)

    return get_result(state)


def backpropagation(node: MCTSNode, result: str | None, ai_player: str) -> None:
    
    #PHASE 4 — BACKPROPAGATION
    
    while node is not None:
        node.visits += 1
        if result == ai_player:
            node.wins += 1
        node = node.parent



#  MAIN MCTS FUNCTION

def mcts(board: list, ai_player: str, iterations: int = 1000) -> int:
    
    root = MCTSNode(state=board, player=ai_player)

    for i in range(iterations):
        # 1. SELECTION 
        selected = selection(root)

        # 2. EXPANSION 
        expanded = expansion(selected)

        # 3. SIMULATION 
        result = simulation(expanded)

        # 4. BACKPROPAGATION
        backpropagation(expanded, result, ai_player)

    # Choose the move with the most visits (most explored = most reliable)
    best = root.most_visited_child()
    print(f"\n[MCTS] Ran {iterations} iterations | Best move: {best.move} "
          f"| Win rate: {best.wins/best.visits:.1%} | Visits: {best.visits}")
    return best.move



#  DISPLAY HELPERS


def print_board(board: list) -> None:
    """Pretty-print the board with indices for reference."""
    symbols = {None: '.', 'X': 'X', 'O': 'O'}
    print()
    for row in range(3):
        cells = [symbols[board[row*3+col]] for col in range(3)]
        print(f"  {cells[0]} | {cells[1]} | {cells[2]}")
        if row < 2:
            print("  ---------")
    print()


def print_indices() -> None:
    """This function Show the cell index layout."""
    print("\n  Cell indices:")
    for row in range(3):
        print(f"  {row*3} | {row*3+1} | {row*3+2}")
        if row < 2:
            print("  ---------")
    print()



#  GAME LOOP

def play_game(ai_player: str = 'O', iterations: int = 1000) -> None:
    """
    Play an interactive game of Tic-Tac-Toe against the MCTS AI.
    Human(We) is X, AI is O (by default).
    """
    board = [None] * 9
    human = other_player(ai_player)
    current = 'X'   # X always goes first

    print("\n" + "═"*40)
    print("   MCTS TIC-TAC-TOE")
    print(f"   You: {human}  |  AI: {ai_player}  |  Iterations: {iterations}")
    print("═"*40)
    print_indices()

    while True:
        print_board(board)

        if current == human:
            # Human move
            while True:
                try:
                    move = int(input(f"  Your move [{human}] (0-8): "))
                    if 0 <= move <= 8 and board[move] is None:
                        break
                    print("  ✗ Invalid cell, try again.")
                except ValueError:
                    print("  ✗ Enter a number 0-8.")
            board[move] = human

        else:
            # AI move
            print(f"  AI [{ai_player}] is thinking…")
            move = mcts(board, ai_player, iterations)
            board[move] = ai_player
            print(f"  AI [{ai_player}] played cell {move}")

        # Check game end
        if check_winner(board, current):
            print_board(board)
            if current == human:
                print("  🎉 Congratulations — WE WIN!")
            else:
                print("  🤖 AI wins! Try again with fewer iterations.")
            break

        if is_draw(board):
            print_board(board)
            print("  🤝 It's a draw! MCTS played perfectly.")
            break

        current = other_player(current)



#  ENTRY POINT


if __name__ == "__main__":
    print("\nDifficulty settings:")
    print("  easy   →  100 iterations")
    print("  medium →  500 iterations")
    print("  hard   → 2000 iterations")

    choice = input("\nChoose difficulty (easy/medium/hard) [default: medium]: ").strip().lower()
    iters = {"easy": 100, "medium": 500, "hard": 2000}.get(choice, 500)

    play_game(ai_player='O', iterations=iters)




