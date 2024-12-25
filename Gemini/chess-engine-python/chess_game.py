import chess
import chess.engine
import tkinter as tk
import json
from PIL import Image, ImageTk
from random import choice

# Satranç taşları için görsel dosya adları
PIECE_IMAGES = {
    chess.PAWN: {True: "wp.png", False: "bp.png"},
    chess.KNIGHT: {True: "wn.png", False: "bn.png"},
    chess.BISHOP: {True: "wb.png", False: "bb.png"},
    chess.ROOK: {True: "wr.png", False: "br.png"},
    chess.QUEEN: {True: "wq.png", False: "bq.png"},
    chess.KING: {True: "wk.png", False: "bk.png"},
}

# Ayarlar
BOARD_SIZE = 480  # Satranç tahtası boyutu
SQUARE_SIZE = BOARD_SIZE // 8
MOVE_HISTORY_FILE = "move_history.json"

# Pozisyonel değer tabloları (her taş için örnek tablolar)
PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 5, 5, 5, 5, 5, 5, 5,
    1, 1, 2, 3, 3, 2, 1, 1,
    0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5,
    0, 0, 0, 2, 2, 0, 0, 0,
    0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5,
    0.5, 1, 1, -2, -2, 1, 1, 0.5,
    0, 0, 0, 0, 0, 0, 0, 0
]
KNIGHT_TABLE = [
    -5, -4, -3, -3, -3, -3, -4, -5,
    -4, -2, 0, 0, 0, 0, -2, -4,
    -3, 0, 1, 1.5, 1.5, 1, 0, -3,
    -3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3,
    -3, 0, 1.5, 2, 2, 1.5, 0, -3,
    -3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3,
    -4, -2, 0, 0.5, 0.5, 0, -2, -4,
    -5, -4, -3, -3, -3, -3, -4, -5
]
BISHOP_TABLE = [
    -2, -1, -1, -1, -1, -1, -1, -2,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0.5, 1, 1, 0.5, 0, -1,
    -1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1,
    -1, 0, 1, 1, 1, 1, 0, -1,
    -1, 1, 1, 1, 1, 1, 1, -1,
    -1, 0.5, 0, 0, 0, 0, 0.5, -1,
    -2, -1, -1, -1, -1, -1, -1, -2
]
ROOK_TABLE = [
    0, 0, 0, 0.5, 0.5, 0, 0, 0,
    0.5, 1, 1, 1, 1, 1, 1, 0.5,
    -0.5, 0, 0, 0, 0, 0, 0, -0.5,
    -0.5, 0, 0, 0, 0, 0, 0, -0.5,
    -0.5, 0, 0, 0, 0, 0, 0, -0.5,
    -0.5, 0, 0, 0, 0, 0, 0, -0.5,
    -0.5, 0, 0, 0, 0, 0, 0, -0.5,
    0, 0, 0, 0.5, 0.5, 0, 0, 0
]
QUEEN_TABLE = [
    -2, -1, -1, -0.5, -0.5, -1, -1, -2,
    -1, 0, 0, 0, 0, 0, 0, -1,
    -1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1,
    -0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
    0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5,
    -1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1,
    -1, 0, 0.5, 0, 0, 0, 0, -1,
    -2, -1, -1, -0.5, -0.5, -1, -1, -2
]
KING_TABLE = [
    2, 3, 1, 0, 0, 1, 3, 2,
    2, 2, 0, 0, 0, 0, 2, 2,
    -1, -2, -2, -2, -2, -2, -2, -1,
    -2, -3, -3, -4, -4, -3, -3, -2,
    -3, -4, -4, -5, -5, -4, -4, -3,
    -3, -4, -4, -5, -5, -4, -4, -3,
    -3, -4, -4, -5, -5, -4, -4, -3
]

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Satranç Motoru")

        # Satranç tahtası çizimi
        self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE, bg="white")
        self.canvas.pack()

        # Stockfish motoru yükleme
        self.stockfish_path = "C:\\Users\\efeyi\\Desktop\\stockfish\\stockfish.exe"
        self.stockfish_engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)

        # Satranç tahtası durumu
        self.board = chess.Board()

        # Taş görsellerini yükle
        self.piece_images = self.load_piece_images()

        # Hamle geçmişi ve öğrenme için yükleme
        self.move_history = self.load_move_history()

        self.update_board()
        self.root.after(500, self.game_loop)  # Oyun döngüsünü yavaşlatmak için süre artırıldı

    def load_piece_images(self):
        """Taş görsellerini yükler."""
        images = {}
        for piece_type, colors in PIECE_IMAGES.items():
            images[piece_type] = {
                True: ImageTk.PhotoImage(Image.open(colors[True]).resize((SQUARE_SIZE, SQUARE_SIZE))),
                False: ImageTk.PhotoImage(Image.open(colors[False]).resize((SQUARE_SIZE, SQUARE_SIZE))),
            }
        return images

    def load_move_history(self):
        """Hamle geçmişini JSON dosyasından yükler."""
        try:
            with open(MOVE_HISTORY_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_move_history(self):
        """Hamle geçmişini JSON dosyasına kaydeder."""
        with open(MOVE_HISTORY_FILE, "w") as f:
            json.dump(self.move_history, f, indent=4)

    def draw_board(self):
        """Satranç tahtasını çizer."""
        colors = ["#f0d9b5", "#b58863"]  # Açık kahverengi ve koyu kahverengi
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * SQUARE_SIZE, row * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def update_board(self):
        """Tahtayı günceller ve taşları çizer."""
        self.canvas.delete("all")
        self.draw_board()

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                image = self.piece_images[piece.piece_type][piece.color]
                self.canvas.create_image(x, y, anchor=tk.NW, image=image)

    def game_loop(self):
        """Satranç motorlarının sırasıyla hamle yapmasını sağlar."""
        if not self.board.is_game_over():
            if self.board.turn:  # Beyazın sırası (Minimax motoru)
                best_move = self.find_best_move_minimax(depth=4)  # Derinlik artırıldı
                if best_move is None:
                    best_move = choice(list(self.board.legal_moves))  # Rastgele geçerli bir hamle seç
                self.board.push(best_move)
            else:  # Siyahın sırası (Stockfish)
                result = self.stockfish_engine.play(self.board, chess.engine.Limit(time=0.5))  # Süre artırıldı
                self.board.push(result.move)

            self.update_board()
        else:
            self.analyze_game()
            self.board.reset()  # Oyun tamamlandığında yeni bir oyun başlat
        self.root.after(500, self.game_loop)  # Oyun döngüsünü yavaşlatmak için süre artırıldı

    def analyze_game(self):
        """Oyun sonu analiz yapar ve hamleleri değerlendirir."""
        temp_board = chess.Board()
        for move in self.board.move_stack:
            temp_board.push(move)
            info = self.stockfish_engine.analyse(temp_board, chess.engine.Limit(time=0.1))

            score = info["score"].relative.score()
            move_uci = move.uci()

            if move_uci not in self.move_history:
                self.move_history[move_uci] = {"good": 0, "bad": 0}

            if score is not None:
                if score > 0:
                    self.move_history[move_uci]["good"] += 1
                elif score < 0:
                    self.move_history[move_uci]["bad"] += 1

        # Hamle geçmişini kaydet
        self.save_move_history()

    def find_best_move_minimax(self, depth=4):
        """Minimax algoritmasını kullanarak en iyi hamleyi bulur (Basit bir versiyon)."""
        legal_moves = list(self.board.legal_moves)
        best_move = None
        best_value = float('-inf') if self.board.turn else float('inf')

        for move in legal_moves:
            move_uci = move.uci()
            if move_uci in self.move_history and self.move_history[move_uci]["bad"] > self.move_history[move_uci]["good"]:
                continue  # Kötü hamleleri atla

            self.board.push(move)
            move_value = self.minimax(depth - 1, self.board.turn, float('-inf'), float('inf'))
            self.board.pop()

            if self.board.turn:  # Beyaz için en büyük değeri arıyoruz
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
            else:  # Siyah için en küçük değeri arıyoruz
                if move_value < best_value:
                    best_value = move_value
                    best_move = move

        return best_move

    def minimax(self, depth, maximizing_player, alpha, beta):
        """Alfa-beta budaması ile geliştirilmiş Minimax algoritması."""
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()

        legal_moves = list(self.board.legal_moves)
        if maximizing_player:
            best_value = float('-inf')
            for move in legal_moves:
                self.board.push(move)
                best_value = max(best_value, self.minimax(depth - 1, False, alpha, beta))
                self.board.pop()
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return best_value
        else:
            best_value = float('inf')
            for move in legal_moves:
                self.board.push(move)
                best_value = min(best_value, self.minimax(depth - 1, True, alpha, beta))
                self.board.pop()
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_value

    def evaluate_board(self):
        """Tahtanın mevcut durumunu değerlendiren bir fonksiyon (örneğin, taş ve pozisyon değerleri)."""
        evaluation = 0

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_value = self.get_piece_value(piece)
                evaluation += piece_value
                evaluation += self.get_positional_value(piece, square)

        return evaluation

    def get_piece_value(self, piece):
        """Her bir taşın değerini döndürür."""
        if piece.piece_type == chess.PAWN:
            return 1
        elif piece.piece_type == chess.KNIGHT:
            return 3
        elif piece.piece_type == chess.BISHOP:
            return 3
        elif piece.piece_type == chess.ROOK:
            return 5
        elif piece.piece_type == chess.QUEEN:
            return 9
        elif piece.piece_type == chess.KING:
            return 0  # King değeri genellikle oyun bittiğinde çok önemlidir
        return 0

    def get_positional_value(self, piece, square):
        """Pozisyonel değer tablolarını kullanarak taşın pozisyon değerini döndürür."""
        if piece.piece_type == chess.PAWN:
            return PAWN_TABLE[square] if piece.color == chess.WHITE else PAWN_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.KNIGHT:
            return KNIGHT_TABLE[square] if piece.color == chess.WHITE else KNIGHT_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.BISHOP:
            return BISHOP_TABLE[square] if piece.color == chess.WHITE else BISHOP_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.ROOK:
            return ROOK_TABLE[square] if piece.color == chess.WHITE else ROOK_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.QUEEN:
            return QUEEN_TABLE[square] if piece.color == chess.WHITE else QUEEN_TABLE[chess.square_mirror(square)]
        elif piece.piece_type == chess.KING:
            return KING_TABLE[square] if piece.color == chess.WHITE else KING_TABLE[chess.square_mirror(square)]
        return 0

    def on_square_click(self, event):
        """Bir kareye tıklama işlemi (kullanıcı hamlesi)."""
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        square = chess.square(col, row)

        if self.board.is_game_over() or not self.board.turn:
            return

        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.get_move_from_user_input(square)

    def get_move_from_user_input(self, target_square):
        """Kullanıcıdan aldığı kareye göre hamle üretir (minimax ve Stockfish dışında)."""
        pass

# Ana tkinter uygulaması başlatma
root = tk.Tk()
app = ChessApp(root)
root.mainloop()