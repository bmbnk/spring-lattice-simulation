import pickle as pkl

import matplotlib.animation as animation
import matplotlib.pyplot as plt

DT = 1e-2
SPEED_FACTOR = 50
FPS = 60
SIM_STEP = int(SPEED_FACTOR / DT / FPS)
SAVE = False
VID_FILENAME = "test.mp4"

DATA_DIR = "./data/system.pkl"


def update_fig(frame, system, scats, line):
    time = frame * SIM_STEP

    for scat, mp in zip(scats, system.mps):
        coor = mp.history[0][time]
        scat.set_data(([coor.a1], [coor.a2]))
        scat.set_3d_properties(coor.a3)

    for line, spring in zip(lines, system.springs):
        coor1 = spring.mp1.history[0][time]
        coor2 = spring.mp2.history[0][time]

        line.set_data(([coor1.a1, coor2.a1], [coor1.a2, coor2.a2]))
        line.set_3d_properties([coor1.a3, coor2.a3])
    return scats


with open(DATA_DIR, "rb") as f:
    system = pkl.load(f)


fig = plt.figure()
ax = fig.add_subplot(projection="3d")

scats = [
    ax.plot(
        mp.history[0][0].a1, mp.history[0][0].a2, mp.history[0][0].a3, c="r", marker="o"
    )[0]
    for mp in system.mps
]
lines = [ax.plot([], [], [])[0] for _ in range(len(system.springs))]


ax.set(xlim3d=(0, 50), xlabel="X")
ax.set(ylim3d=(0, 50), ylabel="Y")
ax.set(zlim3d=(-50, 50), zlabel="Z")


num_steps = int(len(system.mps[0].history[0]) / SIM_STEP)
ani = animation.FuncAnimation(
    fig,
    update_fig,
    num_steps,
    fargs=(system, scats, lines),
    interval=FPS,
    blit=False,
)

if SAVE:
    ani.save(filename=VID_FILENAME, writer="ffmpeg")

plt.show()
