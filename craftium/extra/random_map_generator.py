import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import math

class RandomMapGen():
    """Random dungeon map generator. This class is intended to be used
    for the `Craftium/ProcDungeons-v0` environment, but you could implement
    and use your own generator (must use the same ascii format).

    :param n_rooms: Number of rooms of the dungeon.
    :param room_min_size: Minimum size (both height and width) of the room.
    :param room_max_size: Maximum size (both height and width) of the room.
    :param dispersion: Affects the _distance between the rooms.
    :param min_monsters_per_room: Minimum number of monsters per room.
    :param max_monsters_per_room: Maximum number of monsters per room.
    :param monsters: A dictionary with the `a`, `b`, `c`, and `d` keys (refers to the type of the monster), where values are the probability of spawning a monster of that type. Types are sorted from `a` less dangerous to, `d`, more.
    :param monsters_in_player_spawn: If set to `True`, monsters can spawn in the same room as the player.
    """
    def __init__(
            self,
            n_rooms: int = 4,
            room_min_size: int = 7,
            room_max_size: int = 15,
            dispersion: float = 1.,
            min_monsters_per_room: int = 0,
            max_monsters_per_room: int = 5,
            monsters: dict[str, float] = {"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1},
            monsters_in_player_spawn: bool = False,
    ):
        assert room_min_size >= 5, "Minimum room size must be >= 5"
        assert room_min_size <= room_max_size , "Room min size must be smaller or equal to max size"
        rooms = [[[0, 0],
                  list(np.random.randint(room_min_size, room_max_size+1, size=2))]
                 for _ in range(n_rooms)]

        # place the rooms in non-overlapping placements
        collide = True
        while collide:
            for i in range(n_rooms):
                others = rooms[:i] + rooms[i+1:]

                if sum([self._collide(rooms[i], other) for other in others]) == 0:
                    continue

                others_center = np.array(others).mean(axis=0).mean(axis=0)
                center = np.array(rooms[i]).mean(axis=0)
                d = (dispersion*(center - others_center)).astype(np.int64)
                d[d==0] = np.random.randint(-1, 2)

                rooms[i][0][0] += d[0]
                rooms[i][1][0] += d[0]
                rooms[i][0][1] += d[1]
                rooms[i][1][1] += d[1]

                collide = False
                for k in range(n_rooms):
                    for j in range(n_rooms):
                        if k != j:
                            if self._collide(rooms[k], rooms[j]):
                                collide = True
                                break
                if not collide:
                    break
            # plt.clf()
            # self.plot(rooms)
            # plt.pause(0.01)

        # translate the rooms to the x>=0 y>=0 quadrant
        rooms = np.array(rooms)
        rooms[:, :, 0] -= rooms[:, :, 0].min()
        rooms[:, :, 1] -= rooms[:, :, 1].min()

        # place all corridors
        corrs = []
        for i in range(n_rooms):
            # compute the _distances from the room i to the other rooms
            c = np.array(self._box_center(rooms[i]))
            dists = [np.power(c - np.array(self._box_center(rooms[j])), 2).sum() for j in range(n_rooms) if i != j]
            indices = list(range(n_rooms))
            indices.remove(i)
            indices = np.array(indices)
            for j in indices[np.argsort(dists)]:
                cor = [self._box_center(rooms[i]), self._box_center(rooms[j])]
                # the corridor should not intersect with any room
                cor_intersects_rooms = sum([
                    self._line_intersects_box(cor, rooms[k]) for k in range(n_rooms) if k != i and k != j
                ]) > 0
                # the corridor should not intersect with other corridors
                cor_intersects_cor = sum([self.lines_intersect(cor, c) for c in corrs]) > 0
                if not (cor_intersects_rooms or cor_intersects_cor):
                    corrs.append(cor)
                    # if 0.5 > np.random.rand(): # add another (extra) corridor with 0.5 prob
                    #     break
                    break
        # make all rooms accessible
        corrs, _ = self._add_minimum_edges(corrs)

        # plt.clf()
        # self.plot(rooms, corridors=corrs)
        # plt.show()

        # place the player in the center of a random room
        idx1 = np.random.randint(0, len(corrs))
        idx2 = np.random.randint(0, 2)
        self.player_pos = corrs[idx1][idx2]

        # place the objective in the most distant room to the player
        dists = [self._distance(self.player_pos, self._box_center(r)) for r in rooms]
        room_idx = np.argmax(dists)
        self.objective_pos = self._box_center(rooms[room_idx])

        # place monsters
        monster_names = list(monsters.keys())
        monster_probs = list(monsters.values())
        monster_type_indices = -np.arange(1, len(monster_probs)+1)
        monster_locs = []
        for room in rooms:
            if (not monsters_in_player_spawn
                and self._box_center(room) == self.player_pos) or max_monsters_per_room == 0:
                continue
            # number of monsters in this room
            n = np.random.randint(min_monsters_per_room, max_monsters_per_room)
            type_idx = np.random.choice(monster_type_indices, p=monster_probs)
            # compute al locations within a room that a monster can spawn
            places = []
            for x in range(room[0, 0]+2, room[1, 0]-1):
                for y in range(room[0, 1]+2, room[1, 1]-1):
                    if not (self.objective_pos == np.array([x, y])).all(): # check the position isn't objective's
                        places.append([x, y])
            # select random placements for the monsters
            for idx in np.random.choice(len(places), min(n, len(places)), replace=False):
                monster_locs.append((type_idx, places[idx]))

        self.monster_locs = monster_locs
        self.monster_names = monster_names
        self.monster_type_indices = monster_type_indices

        self.corridors = np.array(corrs)
        self.rooms = rooms

    def _bresenham(self, x0, y0, x1, y1):
        """Yield integer coordinates on the line from (x0, y0) to (x1, y1).

        This function is directly taken from https://github.com/encukou/_bresenham under the MIT license.
        """
        dx = x1 - x0
        dy = y1 - y0

        xsign = 1 if dx > 0 else -1
        ysign = 1 if dy > 0 else -1

        dx = abs(dx)
        dy = abs(dy)

        if dx > dy:
            xx, xy, yx, yy = xsign, 0, 0, ysign
        else:
            dx, dy = dy, dx
            xx, xy, yx, yy = 0, ysign, xsign, 0

        D = 2*dy - dx
        y = 0

        for x in range(dx + 1):
            yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
            if D >= 0:
                y += 1
                D -= 2*dx
            D += 2*dy

    def rasterize(self, wall_height=2):
        """Converts the generated map into an ASCII string.

        :params wall_height: Height of the walls of the dungeon.
        """
        assert wall_height >= 1, "Wall height must be >= 1"
        ncols, nrows = self.rooms[:, :, 0].max(), self.rooms[:, :, 1].max()
        m = np.zeros((nrows, ncols), dtype=np.int8)

        # add rooms
        for room in self.rooms:
            m[room[0, 1]:room[1, 1], room[0, 0]:room[1, 0]] = 1

        # add corridors
        for corr in self.corridors:
            x0, y0, x1, y1 = corr[0, 0], corr[0, 1], corr[1, 0], corr[1, 1]
            lines = list(self._bresenham(x0, y0, x1, y1))
            for (x, y) in lines:
                m[y, x] = 1
                # increase line thickness from 1 to 3 (minimum)
                m[y+1, x], m[y-1, x] = 1, 1
                m[y+2, x], m[y-2, x] = 1, 1
                m[y, x+1], m[y, x-1] = 1, 1
                m[y, x+2], m[y, x-2] = 1, 1

        # add walls
        layers = [m]
        l1 = np.zeros((nrows, ncols), dtype=np.int8)
        for i in range(nrows):
            for j in range(ncols):
                if m[i, j] == 0:
                    continue
                # check if the block i,j is completely surrounded with other blocks or not
                v = True
                if i > 0:
                    v = v and m[i-1, j] == 1
                if i < nrows - 1:
                    v = v and m[i+1, j] == 1
                if j > 0:
                    v = v and m[i, j-1] == 1
                if j < ncols - 1:
                    v = v and m[i, j+1] == 1
                if not v or (i == 0 or i == nrows-1 or j == 0 or j == ncols - 1):
                    l1[i, j] = 1

        # add walls
        for _ in range(wall_height):
            layers.append(l1.copy())

        # place the player
        layers[1][self.player_pos[1], self.player_pos[0]] = 2

        # place the objective
        layers[1][self.objective_pos[1], self.objective_pos[0]] = 3

        # place the monsters
        for type_idx, pos in self.monster_locs:
            layers[1][pos[1], pos[0]] = type_idx

        # convert layer matrices into a string
        s = ""
        for il, layer in enumerate(layers):
            for i in range(nrows):
                for j in range(ncols):
                    char = " "
                    if layer[i][j] == 1:
                        char = "#"
                    elif layer[i][j] == 2:
                        char = "@"
                    elif layer[i][j] == 3:
                        char = "O"
                    elif layer[i][j] < 0: # negative values are monsters
                        char = self.monster_names[(-layer[i][j])-1]
                    s += char
                if il < len(layers)-1 or i < nrows-1:
                    s += "\n"
            if il < len(layers)-1: # skip separator in last layer
                s += "-\n"
        return s

    def plot(self, rooms, corridors=[]):
        ax = plt.gca()
        for room in rooms:
            rect = plt.Rectangle(
                xy=room[0],
                height=room[1][1]-room[0][1],
                width=room[1][0]-room[0][0],
                fill=False,
                linewidth=2,
            )
            ax.add_patch(rect)
            plt.scatter(*self._box_center(room))

        for corr in corridors:
            plt.plot([corr[0][0], corr[1][0]], [corr[0][1], corr[1][1]])

        lims = np.array(rooms)
        plt.xlim([lims.min()-10, lims.max()+10])
        plt.ylim([lims.min()-10, lims.max()+10])

    def _box_center(self, a):
        return int((a[0][0]+a[1][0])/2), int((a[0][1]+a[1][1])/2)

    def lines_intersect(self, line1, line2):
        def on_segment(p, q, r):
            """Check if point q lies on the segment pr"""
            if (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
                min(p[1], r[1]) <= q[1] <= max(p[1], r[1])):
                return True
            return False

        def orientation(p, q, r):
            """Determine the orientation of the triplet (p, q, r)
            0 -> p, q and r are collinear
            1 -> Clockwise
            2 -> Counterclockwise
            """
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # collinear
            elif val > 0:
                return 1  # clockwise
            else:
                return 2  # counterclockwise

        def do_intersect(p1, q1, p2, q2):
            """Check if the line segments 'p1q1' and 'p2q2' intersect"""

            # Check if they share an endpoint, if so, return False (no intersection)
            if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
                return False

            # Find the four orientations needed for general and special cases
            o1 = orientation(p1, q1, p2)
            o2 = orientation(p1, q1, q2)
            o3 = orientation(p2, q2, p1)
            o4 = orientation(p2, q2, q1)

            # General case
            if o1 != o2 and o3 != o4:
                return True

            # Special Cases (excluding shared endpoint cases)
            if o1 == 0 and on_segment(p1, p2, q1):
                return True
            if o2 == 0 and on_segment(p1, q2, q1):
                return True
            if o3 == 0 and on_segment(p2, p1, q2):
                return True
            if o4 == 0 and on_segment(p2, q1, q2):
                return True

            return False

        # Extract points from the lines
        (p1, q1) = line1
        (p2, q2) = line2

        return do_intersect(p1, q1, p2, q2)

    def _line_intersects_box(self, line, box):
        """Check if a line intersects a rectangular box"""
        # Extract the line points
        (x1, y1), (x2, y2) = line

        # Extract the box points
        (box_left, box_top), (box_right, box_bottom) = box

        # Define the four sides of the box as lines
        box_edges = [
            [(box_left, box_top), (box_right, box_top)],  # top edge
            [(box_right, box_top), (box_right, box_bottom)],  # right edge
            [(box_right, box_bottom), (box_left, box_bottom)],  # bottom edge
            [(box_left, box_bottom), (box_left, box_top)]  # left edge
        ]

        # Check if the line intersects any of the four sides of the box
        for edge in box_edges:
            if self.lines_intersect(line, edge):
                return True

        # Check if the line is completely inside the box
        if (box_left <= x1 <= box_right and box_top <= y1 <= box_bottom) or \
           (box_left <= x2 <= box_right and box_top <= y2 <= box_bottom):
            return True

        return False

    def _distance(self, node1, node2):
        """Calculate Euclidean _distance between two nodes."""
        return math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)

    def _add_minimum_edges(self, edges):
        """Add the minimum number of edges to connect all components."""

        def find_components(edges):
            """Find connected components in the graph using DFS."""
            graph = defaultdict(list)
            for (a, b) in edges:
                graph[a].append(b)
                graph[b].append(a)

            visited = set()
            components = []

            def dfs(node, component):
                stack = [node]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        stack.extend(graph[current])

            for node in graph:
                if node not in visited:
                    component = []
                    dfs(node, component)
                    components.append(component)

            return components

        # Find all the connected components
        components = find_components(edges)

        # If there's only one component, the graph is already fully connected
        if len(components) == 1:
            return edges, []

        new_edges = []

        # Find the closest pair of nodes between different components
        while len(components) > 1:
            min_dist = float('inf')
            edge_to_add = None
            comp1, comp2 = None, None

            # Check all pairs of components
            for i in range(len(components)):
                for j in range(i + 1, len(components)):
                    for node1 in components[i]:
                        for node2 in components[j]:
                            dist = self._distance(node1, node2)
                            if dist < min_dist:
                                min_dist = dist
                                edge_to_add = (node1, node2)
                                comp1, comp2 = i, j

            # Add the closest edge
            new_edges.append(edge_to_add)
            edges.append(edge_to_add)

            # Merge the two components
            components[comp1].extend(components[comp2])
            components.pop(comp2)

        return edges, new_edges

    def _collide(self, a, b):
        b1 = np.array(a).flatten()
        b2 = np.array(b).flatten()
        return not (b1[0] > b2[2] or b1[2] < b2[0] or b1[1] > b2[3] or b1[3] < b2[1])

if __name__ == "__main__":
    mapgen = RandomMapGen(
        n_rooms=2,
        dispersion=0.4,
        room_min_size=5,
        room_max_size=10,
        min_monsters_per_room=1,
        max_monsters_per_room=3,
    )

    # mapgen.plot(mapgen.rooms)
    s = mapgen.rasterize()
    print(s)
