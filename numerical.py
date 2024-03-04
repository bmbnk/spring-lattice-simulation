def euler(m, k, l0, dt, t, l, v):
    steps = range(int(t / dt))

    ls = []
    vs = []
    for _ in steps:
        a = -k * (l - l0) / m
        l = l + v * dt
        v = v + a * dt

        ls.append(l)
        vs.append(v)

    return ls, vs


def verlet(m, k, l0, dt, t, l, v):
    steps = range(int(t / dt))

    ls = []
    vs = []

    a1 = -k * (l - l0) / m
    for _ in steps:
        l = l + v * dt + a1 * dt**2 / 2
        a2 = -k * (l - l0) / m
        v = v + (a2 + a1) * dt / 2

        a1 = a2

        ls.append(l)
        vs.append(v)

    return ls, vs
