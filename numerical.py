from physics import MassPoint


def euler(mps: tuple[MassPoint], t, dt, as_: tuple):
    steps = range(int(t / dt))

    for _ in steps:
        for i, mp in enumerate(mps):
            mp.coor += mp.v * dt
            mp.v += as_[i]() * dt


def verlet(mps: tuple[MassPoint], t, dt, as_: tuple):
    steps = range(int(t / dt))

    a1 = [as_[i]() for i in range(len(as_))]

    for _ in steps:
        for i, mp in enumerate(mps):
            mp.coor += mp.v * dt + a1[i] * dt**2 / 2
            a2 = as_[i](mp)
            mp.v += (a2 + a1) * dt / 2

            a1[i] = a2
