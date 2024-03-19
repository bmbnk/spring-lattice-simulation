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

    next_coor = Vector3D(0, 0, 0)
    for i in range(n_rows):
        for j in range(n_cols):
            coors.append(next_coor)
            idx = len(coors) - 1
            if j < n_cols - 1:
                next_coor = coors[-1] + (l2_vec_up if (i + j) % 2 == 0 else l2_vec_down)
                connections.append((idx, idx + 1))
                lenghts.append(l2)
            if (i + j) % 2 == 0:
                connections.append((idx, idx + n_cols))
                lenghts.append(l1)

        next_coor = coors[-n_cols] + (
            l1_vec if i % 2 == 0 else l1_vec + 2 * x_vec * (x_vec @ l2_vec_down)
        )

    # Change indices in connections to coordinates
    i = 0
    while i < len(connections):
        con = connections[i]
        con_coors = []
        for j in range(len(con)):
            if con[j] < len(coors):
                con_coors.append(coors[con[j]])

        if len(con_coors) == 2:
            connections[i] = (con_coors[0], con_coors[1])
            i += 1
        else:
            del connections[i]
            del lenghts[i]

    # Remove connections to not existing points
    i = 0
    while i < len(coors):
        idxs = []
        for j in range(len(connections)):
            if coors[i] in connections[j]:
                idxs.append(j)
                if len(idxs) > 1:
                    break

        if len(idxs) == 1:
            del connections[idxs[0]]
            del lenghts[idxs[0]]
            del coors[i]
        else:
            i += 1

    return coors, connections, lenghts
