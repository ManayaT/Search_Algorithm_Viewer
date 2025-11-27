import copy
try:
    from .structure import Structure as St  # 相対インポート
except ImportError:
    from structure import Structure as St  # 絶対インポート
import math

class Searcher:
    def __init__(self, maze_list, passed_cost=0.5,
             start_symbol="@", goal_symbol="*",
             load_symbol=".", wall_symbol="#", route_symbol="■"):

        # 引数で渡された設定値
        self.maze_list = maze_list
        self.cost = passed_cost
        self.start_symbol = start_symbol
        self.goal_symbol = goal_symbol
        self.load_symbol = load_symbol
        self.wall_symbol = wall_symbol
        self.route_symbol = route_symbol

        # 構造と位置関係
        self.copy_list = copy.deepcopy(maze_list)
        # ★ maze_sizeを活用することで，IndexOutOfRangeを防ぐことができます ★
        self.maze_size = [len(maze_list), len(maze_list[0])]
        # ★ 探索順番（右，下，左，上） ★
        self.idx_list = [[0, 1], [1, 0], [0, -1], [-1, 0]]
        self.idx_len = len(self.idx_list)

        # 状態管理用
        self.list_1 = []
        self.list_2 = []
        self.goal_flag = False
        self.results_path = []

        # スタート／ゴール地点（start_position = [i,j]の形）
        self.start_position = self._find_symbol(self.start_symbol)
        self.goal_position = self._find_symbol(self.goal_symbol)

    def search(self, debug=False):
        if not self.start_position or not self.goal_position:
            raise ValueError("スタート地点またはゴール地点が見つかりません")

        start_node = St()
        start_node.setTarget(self.start_position)
        self.list_1.append(start_node)
        goal_node = St()

    # <---演習部分--->
        while True:
            # L1が空になった場合は終了
            if len(self.list_1) == 0:
                print("None")
                break

            # スタックなので，L1の最後のノードを取り出す
            node_n = self.list_1.pop(0)
            self.list_2.append(node_n)
            
            # 取り出したノードがゴールだった場合
            if node_n.getTarget() == self.goal_position:
                self.goal_flag = True
                goal_node = node_n
                break

            # 注目ノードの周囲を探索
            for idx in self.idx_list:
                tmp_y = node_n.getTarget()[0] + idx[0]
                tmp_x = node_n.getTarget()[1] + idx[1]

                if (-1 < tmp_x < self.maze_size[1]) and (-1 < tmp_y < self.maze_size[0]):
                    # L1とL2に重複がないか確認できるコード
                    existing_open = next((e for e in self.list_1 if e.getTarget() == [tmp_y, tmp_x]), None)
                    existing_closed = next((e for e in self.list_2 if e.getTarget() == [tmp_y, tmp_x]), None)
                    
                    node_symbol = self.maze_list[tmp_y][tmp_x]
                    
                    # ノードのシンボルが "." または "*" かどうかを確認
                    if node_symbol in (self.load_symbol, self.goal_symbol):
                        # L1とL2に重複がない場合にノードを追加
                        if existing_open is None and existing_closed is None:
                            
                            # 新しい子ノードを作成(構造体の定義)
                            node_n_child = St()
                            # 子ノードに現在注目している座標を設定
                            node_n_child.setTarget([tmp_y, tmp_x])
                            # ここで親ノードの情報を設定
                            node_n_child.setBeforeTarget(node_n.getTarget())
                            # L1の最後に子ノード（構造体）を追加
                            self.list_1.append(node_n_child)

    # <---演習部分--->
        if self.goal_flag:
            tmp = goal_node
            while True:
                self.maze_list[tmp.getTarget()[0]][tmp.getTarget()[1]] = self.route_symbol
                self.results_path.append(tmp.getTarget())
                if tmp.getTarget() == self.start_position:
                    break
                tmp = next((e for e in self.list_2 if e.getTarget() == tmp.getBeforeTarget()), None)
            self.results_path.reverse()


    def _find_symbol(self, symbol):
        return next(([i, j] for i, row in enumerate(self.maze_list) 
                     for j, item in enumerate(row) if item == symbol), None)

    def _print_maze(self, maze=None, label="地図"):
        if maze is None:
            maze = self.maze_list
        print(label + ":")
        for row in maze:
            print([item for item in row])

    # 他プログラムから呼び出す際に使用
    def get_results_path(self):
        return self.results_path
    
    def get_list_1(self):
        return self.list_1
    
    def get_list_2(self):
        return self.list_2
    
    def get_goal_flag(self):
        return self.goal_flag
    
    def get_start_position(self):
        return self.start_position
    
    def get_goal_position(self):
        return self.goal_position

if __name__ == "__main__":
    # スタートからゴールまでの経路が存在するパターン
    maze_list = [
        ["@",".",".",".","."],
        [".",".",".",".","."],
        [".",".",".",".","."],
        [".",".",".",".","."],
        [".",".",".",".","*"],
    ]

    # 探索アルゴリズムの実行
    searcher = Searcher(maze_list)
    searcher.search()

    if searcher.get_goal_flag():
        print("探索成功")
        # print(f"list_2: {[i.getTarget() for i in searcher.get_list_2()]}")
        print(f"経路: {searcher.get_results_path()}")
    searcher._print_maze(label="経路")
