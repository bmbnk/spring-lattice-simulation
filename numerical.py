def euler(m, k, l0, dt, t, l, v):
    steps = range(int(t / dt))

    ls = []
    es = []
    vs = []
    for _ in steps:
        a = -k * (l - l0) / m
        l = l + v * dt
        v = v + a * dt

        e = k * l**2 / 2 + m * v**2 / 2

        es.append(e)
        ls.append(l)
        vs.append(v)

    return ls, es


def verlet(m, k, l0, dt, t, l, v):
    steps = range(int(t / dt))

    ls = []
    vs = []
    es = []

    a1 = -k * (l - l0) / m
    for _ in steps:
        l = l + v * dt + a1 * dt**2 / 2
        a2 = -k * (l - l0) / m
        v = v + (a2 + a1) * dt / 2

        a1 = a2
        e = k * l**2 / 2 + m * v**2 / 2

        es.append(e)
        ls.append(l)
        vs.append(v)

    return ls, es
