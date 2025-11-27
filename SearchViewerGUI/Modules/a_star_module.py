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
        self.maze_size = [len(maze_list), len(maze_list[0])]
        self.idx_list = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        self.idx_len = len(self.idx_list)

        # 状態管理用
        self.list_1 = []
        self.list_2 = []
        self.goal_flag = False
        self.results_path = []

        self.list_1_record = []  # 各展開ごとのL1リスト記録

        # スタート／ゴール地点
        self.start_position = self._find_symbol(self.start_symbol)
        self.goal_position = self._find_symbol(self.goal_symbol)


    def _find_symbol(self, symbol):
        return next(([i, j] for i, row in enumerate(self.maze_list) 
                     for j, item in enumerate(row) if item == symbol), None)

    def euclideanDistance(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def h(self, x1, y1, x2, y2):
        return self.euclideanDistance(x1, y1, x2, y2)

    def search(self, debug=False):
        if not self.start_position or not self.goal_position:
            raise ValueError("スタート地点またはゴール地点が見つかりません")

        start_node = St()
        start_node.setTarget(self.start_position)
        self.list_1.append(start_node)
        self.list_1_record.append([start_node.getTarget()])
        goal_node = St()

        if debug:
            num = 0

        while True:
            if len(self.list_1) == 0:
                if debug:
                    print("探索失敗")
                break

            if debug:
                num += 1
                print(f"{num} 回目の探索")

            if debug:
                print(f"探索リスト: {[i.getTarget() for i in self.list_1]}")

            tmp_u = self.list_1.pop(0)
            self.list_2.append(tmp_u)

            if tmp_u.getTarget() == self.goal_position:
                self.goal_flag = True
                goal_node = tmp_u
                if debug:
                    print("探索成功")
                break

            temp_list_1 = []

            for idx in self.idx_list:
                tmp_y = tmp_u.getTarget()[0] + idx[0]
                tmp_x = tmp_u.getTarget()[1] + idx[1]

                if (-1 < tmp_x < self.maze_size[1]) and (-1 < tmp_y < self.maze_size[0]):
                    existing_open = next((e for e in self.list_1 if e.getTarget() == [tmp_y, tmp_x]), None)
                    existing_closed = next((e for e in self.list_2 if e.getTarget() == [tmp_y, tmp_x]), None)
                    node_symbol = self.maze_list[tmp_y][tmp_x]

                    if node_symbol in (self.load_symbol, self.goal_symbol):
                        if existing_open is None and existing_closed is None:
                            tmp_v = St()
                            tmp_v.setTarget([tmp_y, tmp_x])
                            tmp_v.setBeforeTarget(tmp_u.getTarget())
                            tmp_v.setCost(tmp_u.getCost() + self.cost)
                            tmp_v.setDistance(self.h(tmp_y, tmp_x, self.goal_position[0], self.goal_position[1]))
                            self.list_1.append(tmp_v)

                            temp_list_1.append(tmp_v.getTarget())

                        elif existing_open is not None and (new_g := tmp_u.getCost() + self.cost) < existing_open.getCost():
                            existing_open.setCost(new_g)
                            existing_open.setBeforeTarget(tmp_u.getTarget())

                        elif existing_closed is not None and (new_g := tmp_u.getCost() + self.cost) < existing_closed.getCost():
                            self.list_2.remove(existing_closed)
                            existing_closed.setCost(new_g)
                            existing_closed.setBeforeTarget(tmp_u.getTarget())
                            self.list_1.append(existing_closed)

                            temp_list_1.append(tmp_v.getTarget())

                            print("再探索:", existing_closed.getTarget())

                        self.copy_list[tmp_y][tmp_x] = self.route_symbol

                if debug:
                    for row in self.copy_list:
                        print([item for item in row])
                    print("\n")

            self.list_1_record.append(temp_list_1)

            self.list_1.sort(key=lambda n: n.getCost() + n.getDistance())

        if self.goal_flag:
            tmp = goal_node
            while True:
                self.maze_list[tmp.getTarget()[0]][tmp.getTarget()[1]] = self.route_symbol
                self.results_path.append(tmp.getTarget())
                if tmp.getTarget() == self.start_position:
                    break
                tmp = next((e for e in self.list_2 if e.getTarget() == tmp.getBeforeTarget()), None)

    def print_maze(self, maze=None, label="地図"):
        if maze is None:
            maze = self.maze_list
        print(label + ":")
        for row in maze:
            print([item for item in row])

    def get_results_path(self):
        return self.results_path
    
    def get_list_1(self):
        return self.list_1
    
    def get_list_2(self):
        return self.list_2
    
    def get_list_1_records(self):
        return self.list_1_record
    
    def get_goal_flag(self):
        return self.goal_flag
    
    def get_start_position(self):
        return self.start_position
    
    def get_goal_position(self):
        return self.goal_position

if __name__ == "__main__":
    maze_list = [
        ["@",".",".",".","."],
        [".",".",".",".","."],
        [".",".",".","#","."],
        [".",".","#","#","."],
        [".",".",".",".","*"],
    ]

    searcher = Searcher(maze_list)
    searcher.search(debug=True)
    print(f"list_2: {[i.getTarget() for i in searcher.get_list_2()]}")
    print(f"list_2の要素数: {len(searcher.get_list_2())}")
    print(f"list_1_records: {searcher.get_list_1_records()}")
    print(f"list_1_recordsの要素数: {len(searcher.get_list_1_records())}")
    searcher.print_maze(label="経路")
