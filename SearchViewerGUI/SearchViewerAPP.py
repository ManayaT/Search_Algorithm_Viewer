import sys
import os
from copy import deepcopy

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QRadioButton, QPushButton, QLineEdit, QLabel,
    QSlider, QMessageBox, QComboBox
)
from PySide6.QtGui import QPainter, QColor, QMouseEvent
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, QEventLoop


# Searchモジュールのインポート
from Modules import a_star_module as a_star
from Modules import bfs_module as bfs
from Modules import dfs_module as dfs
from Modules import iddfs_module as iddfs

# --- 定数定義 ---
DEFAULT_GRID_SIZE = 10
MIN_GRID_SIZE = 10
MAX_GRID_SIZE = 30
CELL_SIZE = 40
MARGIN_WIDTH = 40
MARGIN_HEIGHT = 200
SLIDER_MIN = 0
SLIDER_MAX = 100
SLIDER_DEFAULT = 50
SLIDER_INTERVAL = 1
DEFAULT_COLOR = "white"  # 白 (空白セル)
START_COLOR = "#ee4400"  # 赤 (スタート)
GOAL_COLOR = "blue"  # 青 (ゴール)
WALL_COLOR = "darkgray"  # 黒 (障害物)
L1_COLOR = "#98e2fb"  # ライトブルー (L1リスト)
L2_COLOR = "#98fb98"  # ライトグリーン (L2リスト)
RESULT_COLOR = "yellow"  # リセット時の色

class GridWidget(QWidget):
    def __init__(self, rows=DEFAULT_GRID_SIZE, cols=DEFAULT_GRID_SIZE, cell_size=CELL_SIZE):
        super().__init__()
        self.cell_size = cell_size
        self.set_grid(rows, cols)
        self.setMouseTracking(True)
        self.is_dragging = False
        self.color_mode = START_COLOR
        self.last_orange_cell = None
        self.last_brightGreen_cell = None

    def set_grid(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[DEFAULT_COLOR for _ in range(cols)] for _ in range(rows)]
        self.setFixedSize(self.cols * self.cell_size, self.rows * self.cell_size)
        self.update()

    def reset_grid(self):
        self.set_grid(self.rows, self.cols)
        self.last_orange_cell = None
        self.last_brightGreen_cell = None

    def set_color_mode(self, mode: str):
        self.color_mode = mode

    def paintEvent(self, event):
        painter = QPainter(self)
        for row in range(self.rows):
            for col in range(self.cols):
                rect = QRect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                color = self.grid[row][col]
                if color:
                    painter.fillRect(rect, QColor(color))
                painter.drawRect(rect)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.color_cell(event.position().toPoint(), drag=False)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and self.color_mode == WALL_COLOR:
            self.color_cell(event.position().toPoint(), drag=True)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def color_cell(self, pos: QPoint, drag: bool):
        col = pos.x() // self.cell_size
        row = pos.y() // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            current_color = self.grid[row][col]

            if drag and self.color_mode == WALL_COLOR:
                if current_color is DEFAULT_COLOR:
                    self.grid[row][col] = WALL_COLOR
                    self.update()

            elif not drag:
                if self.color_mode == START_COLOR:
                    if self.last_orange_cell:
                        r, c = self.last_orange_cell
                        self.grid[r][c] = DEFAULT_COLOR
                    self.grid[row][col] = START_COLOR
                    self.last_orange_cell = (row, col)
                    self.update()

                elif self.color_mode == GOAL_COLOR:
                    if self.last_brightGreen_cell:
                        r, c = self.last_brightGreen_cell
                        self.grid[r][c] = DEFAULT_COLOR
                    self.grid[row][col] = GOAL_COLOR
                    self.last_brightGreen_cell = (row, col)
                    self.update()

    def get_grid_colors(self):
        return [row[:] for row in self.grid]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SearchViewerAPP")
        self.grid_widget = GridWidget()

        # --- サイズ入力 ---
        size_label = QLabel(f"サイズ ({MIN_GRID_SIZE}〜{MAX_GRID_SIZE}):")
        self.size_input = QLineEdit(str(DEFAULT_GRID_SIZE))
        self.size_input.setFixedWidth(50)
        self.resize_button = QPushButton("変更")
        self.resize_button.clicked.connect(self.change_grid_size)

        size_layout = QHBoxLayout()
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_input)
        size_layout.addWidget(self.resize_button)
        size_layout.addStretch()

        # --- ラジオボタン ---
        self.radio_orange = QRadioButton("赤 (スタート)")
        self.radio_brightGreen = QRadioButton("青 (ゴール)")
        self.radio_darkgray = QRadioButton("黒 (障害物)")

        self.radio_orange.setChecked(True)
        self.radio_orange.toggled.connect(lambda: self.grid_widget.set_color_mode(START_COLOR))
        self.radio_brightGreen.toggled.connect(lambda: self.grid_widget.set_color_mode(GOAL_COLOR))
        self.radio_darkgray.toggled.connect(lambda: self.grid_widget.set_color_mode(WALL_COLOR))

        self.reset_button = QPushButton("リセット")
        self.reset_button.clicked.connect(self.grid_widget.reset_grid)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_orange)
        radio_layout.addWidget(self.radio_brightGreen)
        radio_layout.addWidget(self.radio_darkgray)
        radio_layout.addWidget(self.reset_button)
        radio_layout.addStretch()

        # --- アルゴリズム選択 ---
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItem("DFS")
        self.algorithm_combo.addItem("BFS")
        self.algorithm_combo.addItem("IDDFS") # ←注意
        self.algorithm_combo.addItem("A*")
        self.algorithm_combo.setCurrentText("DFS")

        # --- スライダーと実行ボタン ---
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(SLIDER_MIN)
        self.slider.setMaximum(SLIDER_MAX)
        self.slider.setValue(SLIDER_DEFAULT)
        self.slider.setTickInterval(SLIDER_INTERVAL)

        self.slider_value_label = QLabel(f"探索コスト:{self.slider.value() / SLIDER_MAX:.2f}")
        self.slider.valueChanged.connect(self.update_slider_label)

        self.search_button = QPushButton("実行")
        self.search_button.clicked.connect(self.execute_search)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.slider_value_label)
        bottom_layout.addWidget(self.slider)
        bottom_layout.addWidget(self.search_button)

        # --- メインレイアウト ---
        layout = QVBoxLayout()
        layout.addLayout(size_layout)
        layout.addLayout(radio_layout)
        layout.addWidget(self.grid_widget)
        layout.addLayout(bottom_layout)

        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("アルゴリズム:"))
        algo_layout.addWidget(self.algorithm_combo)
        algo_layout.addStretch()
        layout.addLayout(algo_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.adjust_window_size()


    def change_grid_size(self):
        try:
            size = int(self.size_input.text())
            if MIN_GRID_SIZE <= size <= MAX_GRID_SIZE:
                self.grid_widget.set_grid(size, size)
                self.grid_widget.last_orange_cell = None
                self.grid_widget.last_brightGreen_cell = None
                self.adjust_window_size()
            else:
                print(f"サイズは{MIN_GRID_SIZE}〜{MAX_GRID_SIZE}の範囲で入力してください")
        except ValueError:
            print("数値を入力してください")

    def adjust_window_size(self):
        width = self.grid_widget.width() + MARGIN_WIDTH
        height = self.grid_widget.height() + MARGIN_HEIGHT
        self.setFixedSize(width, height)

    def execute_search(self):
        value = self.slider.value() / SLIDER_MAX
        from copy import deepcopy
        original_grid_state = deepcopy(self.grid_widget.grid)
        grid_colors = self.grid_widget.get_grid_colors()

        selected_algo = self.algorithm_combo.currentText()

        if selected_algo == "A*":
            searcher = a_star.Searcher(
                grid_colors,
                passed_cost=value,
                start_symbol=START_COLOR,
                goal_symbol=GOAL_COLOR,
                load_symbol=DEFAULT_COLOR,
                wall_symbol=WALL_COLOR
            )
        elif selected_algo == "DFS":
            searcher = dfs.Searcher(
                grid_colors,
                passed_cost=value,
                start_symbol=START_COLOR,
                goal_symbol=GOAL_COLOR,
                load_symbol=DEFAULT_COLOR,
                wall_symbol=WALL_COLOR
            )
        elif selected_algo == "BFS":
            searcher = bfs.Searcher(
                grid_colors,
                passed_cost=value,
                start_symbol=START_COLOR,
                goal_symbol=GOAL_COLOR,
                load_symbol=DEFAULT_COLOR,
                wall_symbol=WALL_COLOR
            )
        elif selected_algo == "IDDFS":
            searcher = iddfs.Searcher(
                grid_colors,
                passed_cost=value,
                start_symbol=START_COLOR,
                goal_symbol=GOAL_COLOR,
                load_symbol=DEFAULT_COLOR,
                wall_symbol=WALL_COLOR
            )

        searcher.search(debug=False)

        if selected_algo == "IDDFS":
            list_2s = searcher.get_depth_list_2_records().items()
            for depth, list_2 in list_2s:
                for i in list_2:
                    y, x = i.getTarget()
                    if self.grid_widget.grid[y][x] == L2_COLOR:
                        self.grid_widget.grid[y][x] = DEFAULT_COLOR
                        self.grid_widget.update()
                        QTimer.singleShot(30, loop.quit)
                        loop.exec()
                    if self.grid_widget.grid[y][x] == DEFAULT_COLOR:
                        self.grid_widget.grid[y][x] = L2_COLOR
                    self.grid_widget.update()
                    loop = QEventLoop()
                    QTimer.singleShot(70, loop.quit)
                    loop.exec()
                self.grid_widget.grid = deepcopy(original_grid_state)
                self.grid_widget.update()
        else:
            list_2 = searcher.get_list_2()    
            list_1_records = searcher.get_list_1_records()        
            for elem_L1, elem_L2 in zip(list_1_records, list_2):
                for i in elem_L1:
                    y2, x2 = i
                    if self.grid_widget.grid[y2][x2] == DEFAULT_COLOR:
                        self.grid_widget.grid[y2][x2] = L1_COLOR
                        self.grid_widget.update()
                        loop = QEventLoop()
                        QTimer.singleShot(50, loop.quit)
                        loop.exec()
                y1, x1 = elem_L2.getTarget()
                if self.grid_widget.grid[y1][x1] == (L1_COLOR):
                    self.grid_widget.grid[y1][x1] = L2_COLOR
                    self.grid_widget.update()
                    loop = QEventLoop()
                    QTimer.singleShot(70, loop.quit)
                    loop.exec()

        # 経路描画
        for i in searcher.get_results_path():
            y, x = i
            if self.grid_widget.grid[y][x] in (DEFAULT_COLOR, L2_COLOR):
                self.grid_widget.grid[y][x] = RESULT_COLOR
        self.grid_widget.update()

        # ポップアップ表示
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("探索結果")
        if searcher.get_goal_flag():
            msg_box.setText("探索に成功しました．")
        else:
            msg_box.setText("探索に失敗しました．")

        reset_button = msg_box.addButton("リセット", QMessageBox.AcceptRole)
        retry_button = msg_box.addButton("リトライ", QMessageBox.ActionRole)
        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked == reset_button:
            self.grid_widget.reset_grid()
        elif clicked == retry_button:
            self.grid_widget.grid = deepcopy(original_grid_state)
            self.grid_widget.update()

    def update_slider_label(self, value):
        self.slider_value_label.setText(f"探索コスト: {value / SLIDER_MAX:.2f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())