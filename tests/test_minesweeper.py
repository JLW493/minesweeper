import pytest
import pygame
from unittest.mock import MagicMock, patch
from minesweeper.minesweeper_gameplay import Cell, Board, Game

@pytest.fixture
def test_board():
    # Create a small 5x5 board for testing with a few mines for predictability
    board = Board(rows=5, cols=5, mines=3)
    board.place_mines(0, 0)  # Place mines after the first click on (0, 0)
    return board

def test_cell_initialization():
    cell = Cell(row=0, col=0)
    assert not cell.is_mine
    assert not cell.is_revealed
    assert not cell.is_flagged
    assert cell.neighbor_mines == 0

def test_place_mines(test_board):
    # Confirm there are exactly 3 mines
    mine_count = sum(cell.is_mine for row in test_board.cells for cell in row)
    assert mine_count == 3

def test_reveal_cell_no_mine(test_board):
    # Reveal a cell without a mine
    cell = test_board.cells[0][0]
    result = cell.reveal(test_board)
    assert cell.is_revealed
    assert result == False  # Should not trigger a game over

def test_reveal_cell_mine(test_board):
    # Manually set a mine for testing
    test_board.cells[1][1].is_mine = True
    result = test_board.cells[1][1].reveal(test_board)
    assert result == True  # Game over since it's a mine

def test_toggle_flag():
    cell = Cell(row=0, col=0)
    cell.toggle_flag()
    assert cell.is_flagged
    cell.toggle_flag()
    assert not cell.is_flagged

def test_calculate_neighbor_mines(test_board):
    # Set up a known board state with mines
    test_board.cells[1][1].is_mine = True
    test_board.cells[1][3].is_mine = True
    test_board.cells[3][1].is_mine = True
    test_board.calculate_neighbor_mines()
    
    # Check neighbor mine count for a cell that should have 3 mines around
    assert test_board.cells[2][2].neighbor_mines == 3

def test_reveal_all_mines(test_board):
    # Call reveal_all_mines and check that all mines are revealed
    test_board.reveal_all_mines()
    for row, col in test_board.mine_locations:
        assert test_board.cells[row][col].is_revealed

def test_check_win(test_board):
    # Reveal all non-mine cells to simulate a win
    for row in range(test_board.rows):
        for col in range(test_board.cols):
            cell = test_board.cells[row][col]
            if not cell.is_mine:
                cell.is_revealed = True
    assert test_board.check_win()

def test_game_start():
    game = Game()
    assert game.rows == 16
    assert game.cols == 16
    assert game.mines == 40

    # Verify that the board was created with the correct dimensions
    assert game.board.rows == game.rows
    assert game.board.cols == game.cols
    assert game.board.mines == game.mines

@pytest.mark.parametrize("rows, cols, mines", [
    (5, 5, 5),
    (10, 10, 10),
    (8, 8, 15),
])
def test_custom_board_size(rows, cols, mines):
    # Test board initialization with custom sizes
    board = Board(rows=rows, cols=cols, mines=mines)
    assert board.rows == rows
    assert board.cols == cols
    assert board.mines == mines
    assert len(board.cells) == rows
    assert len(board.cells[0]) == cols