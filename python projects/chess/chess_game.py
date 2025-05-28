import pygame
import sys
import requests
from io import BytesIO
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900  # Extra space for image source selection
BOARD_SIZE = 8
SQUARE_SIZE = WINDOW_WIDTH // BOARD_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105, 150)
MOVE_HIGHLIGHT = (106, 168, 79, 150)
CAPTURE_HIGHLIGHT = (255, 0, 0, 100)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (100, 100, 100)

# Image source options
IMAGE_SOURCES = {
    "Wikimedia (Default)": {
        'wp': 'https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg',
        'wR': 'https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg',
        'wN': 'https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg',
        'wB': 'https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg',
        'wQ': 'https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg',
        'wK': 'https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg',
        'bp': 'https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg',
        'bR': 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg',
        'bN': 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg',
        'bB': 'https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg',
        'bQ': 'https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg',
        'bK': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg'
    },
    "Chess.com Style": {
        'wp': 'https://www.chess.com/chess-themes/pieces/neo/150/wp.png',
        'wR': 'https://www.chess.com/chess-themes/pieces/neo/150/wr.png',
        'wN': 'https://www.chess.com/chess-themes/pieces/neo/150/wn.png',
        'wB': 'https://www.chess.com/chess-themes/pieces/neo/150/wb.png',
        'wQ': 'https://www.chess.com/chess-themes/pieces/neo/150/wq.png',
        'wK': 'https://www.chess.com/chess-themes/pieces/neo/150/wk.png',
        'bp': 'https://www.chess.com/chess-themes/pieces/neo/150/bp.png',
        'bR': 'https://www.chess.com/chess-themes/pieces/neo/150/br.png',
        'bN': 'https://www.chess.com/chess-themes/pieces/neo/150/bn.png',
        'bB': 'https://www.chess.com/chess-themes/pieces/neo/150/bb.png',
        'bQ': 'https://www.chess.com/chess-themes/pieces/neo/150/bq.png',
        'bK': 'https://www.chess.com/chess-themes/pieces/neo/150/bk.png'
    },
    "Lichess Style": {
        'wp': 'https://lichess1.org/assets/piece/merida/wP.svg',
        'wR': 'https://lichess1.org/assets/piece/merida/wR.svg',
        'wN': 'https://lichess1.org/assets/piece/merida/wN.svg',
        'wB': 'https://lichess1.org/assets/piece/merida/wB.svg',
        'wQ': 'https://lichess1.org/assets/piece/merida/wQ.svg',
        'wK': 'https://lichess1.org/assets/piece/merida/wK.svg',
        'bp': 'https://lichess1.org/assets/piece/merida/bP.svg',
        'bR': 'https://lichess1.org/assets/piece/merida/bR.svg',
        'bN': 'https://lichess1.org/assets/piece/merida/bN.svg',
        'bB': 'https://lichess1.org/assets/piece/merida/bB.svg',
        'bQ': 'https://lichess1.org/assets/piece/merida/bQ.svg',
        'bK': 'https://lichess1.org/assets/piece/merida/bK.svg'
    },
    "Symbols (No Internet)": None  # Special case for symbol-based pieces
}

# Cache for downloaded images
image_cache = {}

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        
    def draw(self, surface):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        font = pygame.font.SysFont('Arial', 24)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

def create_symbol_pieces():
    """Create piece images using Unicode symbols"""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 
              'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    images = {}
    
    for piece in pieces:
        surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        color = (255, 255, 255) if piece[0] == 'w' else (50, 50, 50)
        text_color = (0, 0, 0) if piece[0] == 'w' else (255, 255, 255)
        
        # Draw a circle for the piece base
        pygame.draw.circle(surf, color, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
        
        # Add text for the piece type
        font = pygame.font.SysFont('Arial', SQUARE_SIZE//2)
        piece_symbol = ''
        if piece[1] == 'p': piece_symbol = '♟' if piece[0] == 'b' else '♙'
        elif piece[1] == 'R': piece_symbol = '♜' if piece[0] == 'b' else '♖'
        elif piece[1] == 'N': piece_symbol = '♞' if piece[0] == 'b' else '♘'
        elif piece[1] == 'B': piece_symbol = '♝' if piece[0] == 'b' else '♗'
        elif piece[1] == 'Q': piece_symbol = '♛' if piece[0] == 'b' else '♕'
        elif piece[1] == 'K': piece_symbol = '♚' if piece[0] == 'b' else '♔'
        
        text = font.render(piece_symbol, True, text_color)
        text_rect = text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
        surf.blit(text, text_rect)
        
        images[piece] = surf
    
    return images

def download_image(url):
    """Download an image from URL and return a pygame Surface"""
    try:
        if url in image_cache:
            return image_cache[url]
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Handle both SVG and PNG
        if url.lower().endswith('.svg'):
            from cairosvg import svg2png
            png_data = svg2png(bytestring=response.content)
            image_data = BytesIO(png_data)
        else:
            image_data = BytesIO(response.content)
        
        surface = pygame.image.load(image_data)
        
        # Scale to fit the square size
        scale_factor = (SQUARE_SIZE - 10) / max(surface.get_size())
        new_size = (int(surface.get_width() * scale_factor), 
                   int(surface.get_height() * scale_factor))
        surface = pygame.transform.scale(surface, new_size)
        
        image_cache[url] = surface
        return surface
    except Exception as e:
        print(f"Error loading image from {url}: {e}")
        # Return a blank surface if image fails to load
        return pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

def load_piece_images(image_source):
    """Load chess piece images from the selected source"""
    if image_source is None:  # Symbols fallback
        return create_symbol_pieces()
    
    images = {}
    for piece_code, url in image_source.items():
        images[piece_code] = download_image(url)
    return images

# ... [Keep all the ChessGame class code from previous version unchanged] ...

def image_selection_screen():
    """Screen to select which piece set to use"""
    buttons = []
    y_pos = WINDOW_HEIGHT - 150
    button_height = 40
    button_width = 250
    spacing = 20
    
    for i, (name, source) in enumerate(IMAGE_SOURCES.items()):
        x_pos = 50 + (i % 3) * (button_width + spacing)
        y = y_pos if i < 3 else y_pos + button_height + spacing
        buttons.append(Button(x_pos, y, button_width, button_height, name))
    
    font = pygame.font.SysFont('Arial', 36)
    title = font.render("Select Chess Piece Style", True, BLACK)
    title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 200))
    
    selected_source = None
    
    while selected_source is None:
        mouse_click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
        
        mouse_pos = pygame.mouse.get_pos()
        
        window.fill(WHITE)
        window.blit(title, title_rect)
        
        for i, button in enumerate(buttons):
            button.check_hover(mouse_pos)
            button.draw(window)
            
            if button.is_clicked(mouse_pos, mouse_click):
                selected_source = list(IMAGE_SOURCES.values())[i]
        
        pygame.display.update()
        clock.tick(FPS)
    
    return selected_source

def main():
    # Select image source first
    image_source = image_selection_screen()
    piece_images = load_piece_images(image_source)
    
    # Initialize game
    game = ChessGame()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Only process clicks on the board area
                    if mouse_y < BOARD_SIZE * SQUARE_SIZE:
                        board_x, board_y = mouse_x // SQUARE_SIZE, mouse_y // SQUARE_SIZE
                        
                        # If a piece is already selected, try to move it
                        if game.selected_piece:
                            if (board_x, board_y) in game.valid_moves:
                                game.make_move(game.selected_piece, (board_x, board_y))
                            else:
                                # Select a different piece if it's the current player's turn
                                piece = game.get_piece((board_x, board_y))
                                if piece and piece[0] == game.turn:
                                    game.selected_piece = (board_x, board_y)
                                    game.valid_moves = game.get_valid_moves((board_x, board_y))
                                else:
                                    game.selected_piece = None
                                    game.valid_moves = []
                        else:
                            # Select a piece if it's the current player's turn
                            piece = game.get_piece((board_x, board_y))
                            if piece and piece[0] == game.turn:
                                game.selected_piece = (board_x, board_y)
                                game.valid_moves = game.get_valid_moves((board_x, board_y))
        
        # Draw the board
        window.fill(WHITE)
        
        # Draw the chess board squares
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (x + y) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(window, color, (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight selected piece and valid moves
                if game.selected_piece and game.selected_piece == (x, y):
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(HIGHLIGHT)
                    window.blit(highlight, (x * SQUARE_SIZE, y * SQUARE_SIZE))
                
                if game.selected_piece and (x, y) in game.valid_moves:
                    target_piece = game.get_piece((x, y))
                    highlight_color = CAPTURE_HIGHLIGHT if target_piece else MOVE_HIGHLIGHT
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(highlight_color)
                    window.blit(highlight, (x * SQUARE_SIZE, y * SQUARE_SIZE))
        
        # Draw the pieces (centered in their squares)
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                piece = game.board[x][y]
                if piece:
                    image = piece_images[piece]
                    # Center the image in the square
                    pos_x = x * SQUARE_SIZE + (SQUARE_SIZE - image.get_width()) // 2
                    pos_y = y * SQUARE_SIZE + (SQUARE_SIZE - image.get_height()) // 2
                    window.blit(image, (pos_x, pos_y))
        
        # Draw captured pieces
        def draw_captured_pieces(side, x_start, y_pos):
            spacing = SQUARE_SIZE // 2
            for i, piece_code in enumerate(game.captured_pieces[side]):
                if i > 0 and i % 8 == 0:  # New line after 8 pieces
                    y_pos += spacing
                    x_start = 10
                image = piece_images[piece_code]
                scaled_image = pygame.transform.scale(image, (spacing, spacing))
                window.blit(scaled_image, (x_start, y_pos))
                x_start += spacing
        
        # Draw white's captured pieces (black pieces)
        font = pygame.font.SysFont('Arial', 20)
        label = font.render("Captured by White:", True, BLACK)
        window.blit(label, (10, BOARD_SIZE * SQUARE_SIZE + 10))
        draw_captured_pieces('w', 10, BOARD_SIZE * SQUARE_SIZE + 40)
        
        # Draw black's captured pieces (white pieces)
        label = font.render("Captured by Black:", True, BLACK)
        window.blit(label, (10, BOARD_SIZE * SQUARE_SIZE + 80))
        draw_captured_pieces('b', 10, BOARD_SIZE * SQUARE_SIZE + 110)
        
        # Draw game status
        font = pygame.font.SysFont('Arial', 24)
        status_text = f"{'White' if game.turn == 'w' else 'Black'} to move"
        if game.check:
            status_text += " - CHECK!"
        if game.checkmate:
            status_text = f"{'Black' if game.turn == 'w' else 'White'} wins by checkmate!"
        if game.stalemate:
            status_text = "Stalemate - Game drawn!"
        
        text = font.render(status_text, True, BLACK)
        window.blit(text, (10, WINDOW_HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Internet connection required for online images. Using symbols instead.")
        IMAGE_SOURCES["Symbols (No Internet)"] = None
        main()