from common.constants import *

class MapManager:
    """
    Static maze map (32x16).
    '#' = wall, '.' = empty
    """

    def __init__(self):
        self.grid = self._load_map()
        self.walls = set()
        self._build_wall_set()

    def _load_map(self):
        return [
            "##################################",
            "#................................#",
            "#.####....####.....####.......####",
            "#................................#",
            "#.####..#.####.....####.......####",
            "#..................#.............#",
            "#.####..#.####.....####.........##",
            "#.....................#..........#",
            "#.####..#.####..#..####.........##",
            "#................................#",
            "#.####..#.####..#..####..#.....###",
            "#................................#",
            "#.####....####..#..####..#....####",
            "#................................#",
            "#.................###............#",
            "##################################",
        ]

    def _build_wall_set(self):
        for y, row in enumerate(self.grid):
            for x, ch in enumerate(row):
                if ch == "#":
                    self.walls.add((x, y))

    def export_map(self):
        return {
            "rows": ROWS,
            "cols": COLS,
            "grid": self.grid
        }

    def is_wall_cell(self, cx, cy):
        return (cx, cy) in self.walls

    def is_collision(self, x, y):
        cx = int(x // CELL_SIZE)
        cy = int(y // CELL_SIZE)
        return self.is_wall_cell(cx, cy)

    def ray_blocked(self, x1, y1, x2, y2):
        if x1 == x2:
            step = 1 if y2 > y1 else -1
            for y in range(y1 + step, y2, step):
                if self.is_wall_cell(x1, y):
                    return True
        elif y1 == y2:
            step = 1 if x2 > x1 else -1
            for x in range(x1 + step, x2, step):
                if self.is_wall_cell(x, y1):
                    return True
        return False
