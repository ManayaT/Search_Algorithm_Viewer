import copy
try:
    from .structure import Structure as St  # 相対インポート
except ImportError:
    from structure import Structure as St  # 絶対インポート

class Searcher:
    def __init__(self, maze_list, passed_cost=0.5,
                 start_symbol="@", goal_symbol="*",
                 load_symbol=".", wall_symbol="#", route_symbol="■",
                 explored_symbol="□"):
        self.original_maze = maze_list
        self.start_symbol = start_symbol
        self.goal_symbol = goal_symbol
        self.load_symbol = load_symbol
        self.wall_symbol = wall_symbol
        self.route_symbol = route_symbol
        self.explored_symbol = explored_symbol
        self.passed_cost = passed_cost

        self.maze_size = (len(maze_list), len(maze_list[0]))
        # 優先方向: 右, 下, 左, 上
        self.idx_list = [[0, 1], [1, 0], [0, -1], [-1, 0]]

        self.start_position = self._find_symbol(start_symbol)
        self.goal_position = self._find_symbol(goal_symbol)
        self.goal_node = None
        self.goal_flag = False
        # 各深さごとの探索済みノード記録: {limit: [Structure, ...]}
        self.depth_list_2_records = {}
        self.results_path = []

    def _find_symbol(self, symbol):
        return next(([i, j] for i, row in enumerate(self.original_maze)
                     for j, item in enumerate(row) if item == symbol), None)

    def search(self, max_depth = 10, debug=False):
        if self.start_position is None or self.goal_position is None:
            raise ValueError("スタート地点またはゴール地点が見つかりません")

        self.goal_flag = False
        for limit in range(max_depth + 1):
            if debug:
                print(f"深さ制限: {limit}")
            # 初期化
            self.list_2 = []
            self.goal_node = None
            # DFS を再帰で実行
            visited = set()
            root = St()
            root.setTarget(self.start_position)
            root.setDistance(0)
            visited.add(tuple(self.start_position))
            found = self._depth_limited_search(root, visited, 0, limit, debug)

            # 探索済みノードを記録
            self.depth_list_2_records[limit] = list(self.list_2)

            if found:
                self.goal_flag = True
                if debug:
                    print(f"目標に到達: 深さ {limit} で発見")
                    self.print_maze(label="経路")
                self._reconstruct_path()
                return True
        return False

    def _depth_limited_search(self, node, visited, depth, limit, debug):
        # ノード訪問を記録
        self.list_2.append(node)
        if debug:
            print(f"探索ノード: {node.getTarget()} 深さ: {depth}")

        if node.getTarget() == self.goal_position:
            self.goal_node = node
            return True

        if depth >= limit:
            return False

        # 子ノード展開
        y, x = node.getTarget()
        for dy, dx in self.idx_list:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.maze_size[0] and 0 <= nx < self.maze_size[1]:
                if self.original_maze[ny][nx] in (self.load_symbol, self.goal_symbol):
                    coord = (ny, nx)
                    if coord not in visited:
                        child = St()
                        child.setTarget([ny, nx])
                        child.setBeforeTarget(node.getTarget())
                        child.setDistance(depth + 1)
                        visited.add(coord)
                        if self._depth_limited_search(child, visited, depth + 1, limit, debug):
                            return True
                        visited.remove(coord)
        return False

    def _print_iteration_maze(self, limit):
        display = copy.deepcopy(self.original_maze)
        for node in self.depth_list_2_records[limit]:
            y, x = node.getTarget()
            if display[y][x] == self.load_symbol:
                display[y][x] = self.explored_symbol
        print(f"探索後: 深さ制限 {limit}")
        for row in display:
            print([item for item in row])
        print()

    def _reconstruct_path(self):
        self.results_path = []
        node = self.goal_node
        while node:
            y, x = node.getTarget()
            self.original_maze[y][x] = self.route_symbol
            self.results_path.append([y, x])
            if node.getTarget() == self.start_position:
                break
            prev = node.getBeforeTarget()
            node = next((n for n in self.depth_list_2_records[node.getDistance() - 1] 
                         if n.getTarget() == prev), None)
        self.results_path.reverse()

    def print_maze(self, maze=None, label="地図"):
        maze = maze or self.original_maze
        print(label + ":")
        for row in maze:
            print([item for item in row])

    def get_results_path(self):
        return self.results_path

    # 誰か実装して
    # def get_depth_list_1_records(self):
    #     return self.depth_list_1_records

    def get_depth_list_2_records(self):
        return self.depth_list_2_records

    def get_goal_flag(self):
        return self.goal_flag

if __name__ == "__main__":
    maze_list = [
        ["."]*5 for _ in range(10)
    ]
    maze_list[1][1] = "@"
    maze_list[3][3] = "*"
    searcher = Searcher(maze_list)
    found = searcher.search(max_depth=10, debug=False)
    print("found:", found)
    print("goal_flag:", searcher.get_goal_flag())
    print("path:", searcher.get_results_path())
    for depth, rec in searcher.get_depth_list_2_records().items():
        print(f"Depth {depth}: {[n.getTarget() for n in rec]}")
