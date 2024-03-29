from typing import Iterable

import tqdm

from physics import MassPoint


def euler(mps: Iterable[MassPoint], t, dt, pbar=False):
    steps = range(int(t / dt))
    if pbar:
        steps = tqdm.tqdm(steps)

    for _ in steps:
        for mp in mps:
            mp.coor += mp.v * dt
            mp.v += mp.a * dt


def verlet(mps: Iterable[MassPoint], t, dt, pbar=False):
    steps = range(int(t / dt))
    if pbar:
        steps = tqdm.tqdm(steps)

    a_prev = [mp.a for mp in mps]

    for _ in steps:
        for i, mp in enumerate(mps):
            mp.coor += mp.v * dt + a_prev[i] * dt**2 / 2
            a_next = mp.a
            mp.v += (a_prev[i] + a_next) * dt / 2

            a_prev[i] = a_next
