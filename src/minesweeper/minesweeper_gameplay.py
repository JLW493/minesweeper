import pygame
import random
import sys
import time

# Define constants
CELL_SIZE = 30
PANEL_HEIGHT = 100
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RESET_BUTTON_COLOR = (0, 100, 255)

pygame.init()

# Fonts
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 28)

class Cell:
    def __init__(self, row, col):
        """Initializes each cell

        Args:
            row (_int_): Row of cell
            col (_int_): Column of cell
        """
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
        self.rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + PANEL_HEIGHT, CELL_SIZE, CELL_SIZE)

    def draw(self, screen):
        """Draws the gameboard

        Args:
            screen (_attr_): Attribute of the Game class referring to the display
        """
        if self.is_revealed:
            if self.is_mine:
                pygame.draw.rect(screen, RED, self.rect)
                text = FONT.render("M", True, BLACK)
                screen.blit(text, (self.rect.x + 10, self.rect.y + 5))
            else:
                pygame.draw.rect(screen, GRAY, self.rect)
                if self.neighbor_mines > 0:
                    text = FONT.render(str(self.neighbor_mines), True, BLACK)
                    screen.blit(text, (self.rect.x + 10, self.rect.y + 5))
        else:
            pygame.draw.rect(screen, DARK_GRAY, self.rect)
            if self.is_flagged:
                pygame.draw.rect(screen, YELLOW, self.rect)
                text = FONT.render("F", True, BLACK)
                screen.blit(text, (self.rect.x + 10, self.rect.y + 5))
        pygame.draw.rect(screen, BLACK, self.rect, 1)

    def reveal(self, board):
        """Handles revealing mines

        Args:
            board (_attr_): Attribute of the Game class referring to the game board

        Returns:
            Boolean True/False: Whether a mine is revealed (Ending the game) or not
        """
        if self.is_flagged or self.is_revealed:
            return
        self.is_revealed = True
        if self.is_mine:
            return True  # Game over
        if self.neighbor_mines == 0:
            self.reveal_neighbors(board)
        return False

    def reveal_neighbors(self, board):
        """Handles revealing a cell's neighbors if the cell has no neighboring mines

        Args:
            board (_attr_): Attribute of the Game class referring to the game board
        """
        for r in range(max(0, self.row - 1), min(board.rows, self.row + 2)):
            for c in range(max(0, self.col - 1), min(board.cols, self.col + 2)):
                if not board.cells[r][c].is_revealed:
                    board.cells[r][c].reveal(board)

    def toggle_flag(self):
        """Handles flagging or unflagging cells
        """
        if not self.is_revealed:
            self.is_flagged = not self.is_flagged

class Board:
    def __init__(self, rows, cols, mines):
        """Establishes the game board

        Args:
            rows (_int_): Number of rows
            cols (_int_): Number of columns
            mines (_int_): Number of mines
        """
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.cells = [[Cell(r, c) for c in range(cols)] for r in range(rows)]
        self.mine_locations = []
        self.first_click = True

    def place_mines(self, exclude_row, exclude_col):
        """Places all mines at the first click

        Args:
            exclude_row (_int_): Row of first click, to have no mines on or around it
            exclude_col (_int_): Column of first click, to have no mines on or around it
        """
        # Ensure no mines around the first clicked cell and its neighbors
        exclude_positions = [(r, c) for r in range(max(0, exclude_row - 1), min(self.rows, exclude_row + 2))
                             for c in range(max(0, exclude_col - 1), min(self.cols, exclude_col + 2))]
        
        available_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)
                               if (r, c) not in exclude_positions]
        self.mine_locations = random.sample(available_positions, self.mines)
        
        for (r, c) in self.mine_locations:
            self.cells[r][c].is_mine = True
        
        self.calculate_neighbor_mines()

    def calculate_neighbor_mines(self):
        """Loops a function counting mines around a cell
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.cells[row][col].is_mine:
                    self.cells[row][col].neighbor_mines = self.count_mines_around(row, col)

    def count_mines_around(self, row, col):
        """Counts the mines around a cell

        Args:
            row (_type_): Row of cell
            col (_type_): Column of cell

        Returns:
            integer count: Number of mines around a cell
        """
        count = 0
        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.cells[r][c].is_mine:
                    count += 1
        return count

    def draw(self, screen):
        """Draws the game board

        Args:
            screen (_attr_): Attribute of the Game class related to the screen
        """
        for row in self.cells:
            for cell in row:
                cell.draw(screen)

    def reveal_all_mines(self):
        """Reveals all mines if the player loses
        """
        for (r, c) in self.mine_locations:
            self.cells[r][c].is_revealed = True

class Game:
    def __init__(self):
        """Defines the Game
        """
        self.screen = pygame.display.set_mode((600, 700))
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.won = False  # Track if the player has won
        self.start_time = None
        self.timer_text = ""
        self.rows = 16
        self.cols = 16
        self.mines = 40
        self.board = Board(self.rows, self.cols, self.mines)
        self.start_menu()

    def start_menu(self):
        """Defines anc creates the start menu
        """
        self.screen = pygame.display.set_mode((600, 700))
        self.screen.fill(WHITE)
        self.draw_text("Minesweeper", FONT, BLACK, self.screen, 230, 100)
        self.draw_text("Rows: ", SMALL_FONT, BLACK, self.screen, 100, 250)
        self.draw_text("Cols: ", SMALL_FONT, BLACK, self.screen, 100, 300)
        self.draw_text("Mines: ", SMALL_FONT, BLACK, self.screen, 100, 350)
        self.draw_text("Press Enter to start", SMALL_FONT, BLACK, self.screen, 200, 450)

        # Input boxes
        self.input_boxes = [pygame.Rect(200, 250, 100, 36), pygame.Rect(200, 300, 100, 36), pygame.Rect(200, 350, 100, 36)]
        self.input_text = ["16", "16", "40"]  # Default values
        self.active_box = None  # Track which input box is active

        pygame.display.flip()
        self.menu_loop()

    def menu_loop(self):
        """Handles operations in the menu

        Raises:
            ValueError: An error if the number of mines is greater than the number of cels
        """
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if an input box was clicked
                    for i, box in enumerate(self.input_boxes):
                        if box.collidepoint(event.pos):
                            self.active_box = i
                            break
                if event.type == pygame.KEYDOWN:
                    if self.active_box is not None:
                        if event.key == pygame.K_RETURN:
                            # Update rows, cols, and mines with the user input
                            try:
                                self.rows = int(self.input_text[0])
                                self.cols = int(self.input_text[1])
                                self.mines = int(self.input_text[2])
                                if self.mines >= self.rows * self.cols:
                                    raise ValueError("Too many mines")
                                self.start_game()
                                return
                            except ValueError:
                                print("Invalid input!")
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text[self.active_box] = self.input_text[self.active_box][:-1]
                        elif event.unicode.isdigit():
                            self.input_text[self.active_box] += event.unicode

            self.screen.fill(WHITE)
            self.draw_text("Minesweeper", FONT, BLACK, self.screen, 230, 100)
            self.draw_text("Rows: ", SMALL_FONT, BLACK, self.screen, 100, 250)
            self.draw_text("Cols: ", SMALL_FONT, BLACK, self.screen, 100, 300)
            self.draw_text("Mines: ", SMALL_FONT, BLACK, self.screen, 100, 350)
            self.draw_text("Press Enter to start", SMALL_FONT, BLACK, self.screen, 200, 450)

            # Draw input boxes and current text
            for i, box in enumerate(self.input_boxes):
                pygame.draw.rect(self.screen, DARK_GRAY, box, 2)
                text_surface = FONT.render(self.input_text[i], True, BLACK)
                self.screen.blit(text_surface, (box.x + 5, box.y + 5))

            pygame.display.flip()

    def start_game(self):
        """Begins each game
        """
        # Reset the board size and number of mines based on user input
        self.screen = pygame.display.set_mode((self.cols * CELL_SIZE, self.rows * CELL_SIZE + PANEL_HEIGHT))
        self.board = Board(self.rows, self.cols, self.mines)
        self.start_time = time.time()
        self.timer_text = "Time: 0"
        self.game_over = False
        self.run()

    def run(self):
        """Calls four functions that run the gameplay
        """
        while self.running:
            self.handle_events()
            self.update_timer()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                row, col = self.get_clicked_cell(event.pos)
                if row is not None and col is not None:
                    if event.button == 1:  # Left click
                        if self.board.first_click:
                            self.board.place_mines(row, col)
                            self.board.first_click = False
                        self.handle_left_click(row, col)
                    elif event.button == 3:  # Right click
                        self.handle_right_click(row, col)

    def get_clicked_cell(self, pos):
        x, y = pos
        if y < PANEL_HEIGHT:
            return None, None
        row = (y - PANEL_HEIGHT) // CELL_SIZE
        col = x // CELL_SIZE
        return row, col

    def handle_left_click(self, row, col):
        """Handles left clicking cells

        Args:
            row (_int_): Row of cell
            col (_int_): Column of cell
        """
        cell = self.board.cells[row][col]
        if cell.reveal(self.board):  # Mine clicked
            self.board.reveal_all_mines()
            self.game_over = True
            self.won = False  # Game lost
        elif self.check_win():  # Check if the game is won
            self.game_over = True
            self.won = True

    def handle_right_click(self, row, col):
        """Handles right clicking (flagging) each cell

        Args:
            row (_int_): Row of cell
            col (_int_): Column of cell
        """
        cell = self.board.cells[row][col]
        cell.toggle_flag()

    def update_timer(self):
        """Runs the timer
        """
        if not self.game_over and not self.board.first_click:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_text = f"Time: {elapsed_time}"

    def draw(self):
        """Draws the game
        """
        self.screen.fill(WHITE)
        self.board.draw(self.screen)
        self.draw_panel()
        pygame.display.flip()

    def draw_panel(self):
        """Draws the game panel
        """
        pygame.draw.rect(self.screen, GRAY, (0, 0, self.cols * CELL_SIZE, PANEL_HEIGHT))
        timer_label = SMALL_FONT.render(self.timer_text, True, BLACK)
        self.screen.blit(timer_label, (10, 10))

        # Reset button
        reset_button_rect = pygame.Rect(self.cols * CELL_SIZE - 100, 20, 80, 40)
        pygame.draw.rect(self.screen, RESET_BUTTON_COLOR, reset_button_rect)
        reset_text = SMALL_FONT.render("Reset", True, WHITE)
        self.screen.blit(reset_text, (self.cols * CELL_SIZE - 90, 30))

        if pygame.mouse.get_pressed()[0]:  # Left click
            if reset_button_rect.collidepoint(pygame.mouse.get_pos()):
                self.start_menu()  # Reset the game to start menu

        # Display win/lose message
        if self.game_over:
            if self.won:
                message = "You Win!"
            else:
                message = "Game Over!"
            result_text = FONT.render(message, True, RED)
            self.screen.blit(result_text, (self.cols * CELL_SIZE // 2 - 80, PANEL_HEIGHT // 2 - 20))

    def draw_text(self, text, font, color, surface, x, y):
        """Handles all graphic text

        Args:
            text (_string_): Content of text
            font (_string_): Font of text
            color (_string_): Color of text
            surface (_string_): Surface of writing
            x (_int_): X-Coordinate of text
            y (_int_): Y-Coordinate of text
        """
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def check_win(self):
        """Check if all non-mine cells are revealed."""
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board.cells[row][col]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True


if __name__ == "__main__":
    Game().start()
