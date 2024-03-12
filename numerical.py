from typing import Iterable

from physics import MassPoint


def euler(mps: Iterable[MassPoint], t, dt):
    steps = range(int(t / dt))

    for _ in steps:
        for mp in mps:
            mp.coor += mp.v * dt
            mp.v += mp.a * dt


def verlet(mps: Iterable[MassPoint], t, dt):
    steps = range(int(t / dt))

    a_prev = [mp.a for mp in mps]

    for _ in steps:
        for mp in mps:
            mp.coor += mp.v * dt + a_prev * dt**2 / 2
            a_next = mp.a
            mp.v += (a_prev + a_next) * dt / 2

            a_prev = a_next
