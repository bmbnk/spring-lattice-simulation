#       /\  /\  /\  /
# (0,0)/  \/  \/  \/   |------y
#      |  |   |   |    |
#      |  |   |   |    |x
#      \  /\  /\  /\
#       \/  \/  \/  \
#       |   |   |   |
#       | <- l1 |   |
#       /\  /\  /\  /
#      / <- l2\/  \/
#     |alpha in radians
#     |   |   |    |
#
#   |
#   |  <- len1 vector
#   \/
#
#    -|
#   /  <- len2_up vector
#  /
#
#  \
#   \  <- len2_down vector
#   _|


import math

from physics import Vector3D


def hex_lattice(n_hex_rows, n_hex_cols, l1, l2, alpha):
    x_vec = Vector3D(1, 0, 0)
    l1_vec = Vector3D(l1, 0, 0)
    l2_vec_up = (
        Vector3D(0, 1, 0) + Vector3D(-1, 0, 0) * math.tan(alpha - math.pi / 2)
    ).normalize() * l2
    l2_vec_down = Vector3D(0, 0, 0) + l2_vec_up
    l2_vec_down.a1 *= -1

    coors = []
    connections = []
    lenghts = []

    n_cols = (n_hex_cols + 1) * 2
    n_rows = n_hex_rows + 1

    row_start = Vector3D(0, 0, 0)
    for i in range(n_rows):
        coors.append(row_start)
        for j in range(n_cols - 1):
            n = len(coors)
            coors.append(coors[-1] + (l2_vec_up if (i + j) % 2 == 0 else l2_vec_down))
            connections.append((n - 1, n))
            lenghts.append(l2)
            if (i + j) % 2 == 1:
                connections.append((n, n + n_cols))
                lenghts.append(l1)

        row_start += (
            l1_vec if i % 2 == 0 else l1_vec + 2 * x_vec * (x_vec @ l2_vec_down)
        )

    i = 0
    while i < len(connections):
        pair = connections[i]
        if pair[0] >= len(coors) or pair[1] >= len(coors):
            del connections[i]
            del lenghts[i]
        else:
            i += 1

    coors = [(c.a1, c.a2, c.a3) for c in coors]

    return coors, connections, lenghts
