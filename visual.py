import pickle as pkl

import matplotlib.animation as animation
import matplotlib.pyplot as plt

SAVE = True
VID_PATH = "sim.mp4"
DATA_DIR = "./system.pkl"

DPI = 100
RESOLUTION = (2560, 1440)
AZIM_ANGLE = 45
ELEV_ANGLE = 60

DT = 1e-2
SPEED_FACTOR = 50
FPS = 60
SIM_STEP = int(SPEED_FACTOR / DT / FPS)


def update_fig(frame, system, scats, line):
    time = frame * SIM_STEP

    for scat, mp in zip(scats, system.mps):
        coor = mp.history[0][time]
        scat.set_data(([coor[0]], [coor[1]]))
        scat.set_3d_properties(coor[2])

    for line, spring in zip(lines, system.springs):
        coor1 = spring.mp1.history[0][time]
        coor2 = spring.mp2.history[0][time]

        line.set_data(([coor1[0], coor2[0]], [coor1[1], coor2[1]]))
        line.set_3d_properties([coor1[2], coor2[2]])
    return scats


with open(DATA_DIR, "rb") as f:
    system = pkl.load(f)


fig = plt.figure()
ax = fig.add_subplot(projection="3d")

scats = [
    ax.plot(
        mp.history[0][0][0], mp.history[0][0][1], mp.history[0][0][2], c="r", marker="o"
    )[0]
    for mp in system.mps
]
lines = [ax.plot([], [], [])[0] for _ in range(len(system.springs))]


ax.view_init(elev=ELEV_ANGLE, azim=AZIM_ANGLE)
ax.set(xlim3d=(0, 100), xlabel="X")
ax.set(ylim3d=(0, 100), ylabel="Y")
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
    w = RESOLUTION[0] // DPI
    h = RESOLUTION[1] // DPI
    fig.set_size_inches(w, h, True)
    ani.save(filename=VID_PATH, writer="ffmpeg")

plt.show()
