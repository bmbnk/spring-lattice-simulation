from physics import MassPoint


def euler(mps: list[MassPoint], t, dt, a):
    steps = range(int(t / dt))

    for _ in steps:
        for mp in mps:
            mp.coor += mp.v * dt
            mp.v += a() * dt


def verlet(mps: list[MassPoint], t, dt, a):
    steps = range(int(t / dt))

    a1 = a()
    for _ in steps:
        for mp in mps:
            mp.coor += mp.v * dt + a1 * dt**2 / 2
            a2 = a()
            mp.v += (a2 + a1) * dt / 2

            a1 = a2
