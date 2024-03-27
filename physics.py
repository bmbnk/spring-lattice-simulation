from typing import Callable


class Vector3D:
    def __init__(self, x, y, z):
        self.__coors = [x, y, z]

    def __add__(self, other):
        return Vector3D(*[self[i] + other[i] for i in range(3)])

    def __eq__(self, v):
        return all([self[i] == v[i] for i in range(3)])

    def __getitem__(self, idx):
        if idx not in [0, 1, 2]:
            raise IndexError
        return self.__coors[idx]

    def __matmul__(self, other):
        return sum([self[i] * other[i] for i in range(3)])

    def __mul__(self, a):
        assert isinstance(a, (int, float))
        return Vector3D(*[a * coor for coor in self])

    def __neg__(self):
        return Vector3D(*[-coor for coor in self])

    def __repr__(self):
        return f"{self.__class__.__name__}" + "(" + ", ".join(*self) + ")"

    def __rmul__(self, a):
        return self * a

    def __setitem__(self, idx, val):
        assert isinstance(val, (int, float))
        if idx not in [0, 1, 2]:
            raise IndexError
        self.__coors[idx] = val

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, a):
        self *= 1 / a
        return self

    def len(self):
        return sum([coor**2 for coor in self]) ** (1 / 2)

    def normalize(self):
        self /= self.len()
        return self


class MassPoint:
    def __init__(self, mass, coordinates: Vector3D, velocity: Vector3D):
        self.__mass = mass
        self.__coor = coordinates
        self.__v = velocity
        self.__coor_history = []
        self.__v_history = []
        self.__forces = set()

    @property
    def a(self):
        a = Vector3D(0, 0, 0)
        for f in self.__forces:
            a += f()
        return a / self.m

    @property
    def coor(self):
        return self.__coor

    @coor.setter
    def coor(self, value):
        self.__coor = value
        self.__coor_history.append(value)

    @property
    def history(self):
        return (self.__coor_history, self.__v_history)

    @property
    def m(self):
        return self.__mass

    @property
    def v(self):
        return self.__v

    @v.setter
    def v(self, value):
        self.__v = value
        self.__v_history.append(value)

    def add_force(self, force: Callable):
        self.__forces.add(force)


class Spring:
    def __init__(self, k, l0, mp1: MassPoint, mp2: MassPoint):
        self.mp1 = mp1
        self.mp2 = mp2
        self.__k = k
        self.__l0 = l0

        mp1.add_force(self.force_mp1)
        mp2.add_force(self.force_mp2)

    def direction(self):
        return (self.mp2.coor - self.mp1.coor).normalize()

    def force_mp1(self):
        return self.direction() * -self.force_val()

    def force_mp2(self):
        return self.direction() * self.force_val()

    def force_val(self):
        l = (self.mp2.coor - self.mp1.coor).len()
        return -self.__k * (l - self.__l0)


class System:
    def __init__(self, coors, masses, connections, k_vals, s_lenghts, solver):
        assert len(coors) == len(masses)
        assert len(connections) == len(k_vals) == len(s_lenghts)

        self.mps = []
        self.springs = []
        self.__solver = solver

        for c, m in zip(coors, masses):
            mp = MassPoint(m, c, Vector3D(0, 0, 0))
            self.mps.append(mp)

        for con, k, s_len in zip(connections, k_vals, s_lenghts):
            mps = []
            for mp in self.mps:
                if mp.coor in con:
                    mps.append(mp)

            spring = Spring(k, s_len, mps[0], mps[1])
            self.springs.append(spring)

    def simulate(self, t, dt):
        self.__solver(self.mps, t, dt)
