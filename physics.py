import math
from typing import Callable


class Vector3D:
    def __init__(self, a1, a2, a3):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3

    def __add__(self, other):
        return Vector3D(self.a1 + other.a1, self.a2 + other.a2, self.a3 + other.a3)

    def __mul__(self, a):
        assert isinstance(a, (int, float))

        result = Vector3D(self.a1, self.a2, self.a3)
        result.a1 *= a
        result.a2 *= a
        result.a3 *= a

        return result

    def __rmul__(self, a):
        return self * a

    def __eq__(self, v):
        return all((self.a1 == v.a1, self.a2 == v.a2, self.a3 == v.a3))

    def __truediv__(self, a):
        self *= 1 / a
        return self

    def len(self):
        return math.sqrt(self.a1**2 + self.a2**2 + self.a3**2)

    def __matmul__(self, other):
        return self.a1 * other.a1 + self.a2 * other.a2 + self.a3 * other.a3

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a1}, {self.a2}, {self.a3})"

    def __sub__(self, other):
        return Vector3D(self.a1 - other.a1, self.a2 - other.a2, self.a3 - other.a3)

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

    def add_force(self, force: Callable):
        self.__forces.add(force)

    @property
    def coor(self):
        return self.__coor

    @coor.setter
    def coor(self, value):
        self.__coor = value
        self.__coor_history.append(value)

    @property
    def a(self):
        a = Vector3D(0, 0, 0)
        for f in self.__forces:
            a += f()
        return a / self.m

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
            c_3d = [0] * 3
            for i, coor in enumerate(c):
                c_3d[i] = coor
            c_3d = Vector3D(*c_3d)

            mp = MassPoint(m, c_3d, Vector3D(0, 0, 0))
            self.mps.append(mp)

        for con, k, s_len in zip(connections, k_vals, s_lenghts):
            spring = Spring(k, s_len, self.mps[con[0]], self.mps[con[1]])
            self.springs.append(spring)

    def simulate(self, t, dt):
        self.__solver(self.mps, t, dt)
