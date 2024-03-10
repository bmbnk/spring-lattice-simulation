import pickle as pkl

import matplotlib.animation as animation
import matplotlib.pyplot as plt

DT = 1e-2
SPEED_FACTOR = 40
FPS = 60

COORS_DIR = "./data/coors.pkl"


def update_fig(frame, coors, scats):
    for scat, coor in zip(scats, coors):
        c = coor[frame]
        scat.set_data((c.a1, c.a2))
        scat.set_3d_properties(c.a3)

    return scats


def filter_frames(coors):
    step = SPEED_FACTOR / DT / FPS
    frames = int(len(coors[0]) / step)
    new_coors = (
        tuple(coors[0][int(i * step)] for i in range(frames)),
        tuple(coors[1][int(i * step)] for i in range(frames)),
    )

    return new_coors


with open(COORS_DIR, "rb") as f:
    coors = pkl.load(f)

coors = filter_frames(coors)
num_steps = len(coors[0])

fig = plt.figure()
ax = fig.add_subplot(projection="3d")
scats = [ax.plot(c[0].a1, c[0].a2, c[0].a3, c="r", marker="o")[0] for c in coors]

ax.set(xlim3d=(-25, 25), xlabel="X")
ax.set(ylim3d=(0, 50), ylabel="Y")
ax.set(zlim3d=(-50, 50), zlabel="Z")


ani = animation.FuncAnimation(
    fig,
    update_fig,
    num_steps,
    fargs=(coors, scats),
    interval=FPS,
    blit=True,
)

plt.show()
