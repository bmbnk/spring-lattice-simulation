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
        return f"({self.a1}, {self.a2}, {self.a3})"

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
        return sum((f() for f in self.__forces)) / self.m

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
    def __init__(self, solver, k, l0, mp1: MassPoint, mp2: MassPoint):
        self.__mp1 = mp1
        self.__mp2 = mp2
        self.__k = k
        self.__l0 = l0
        self.__solver = solver

        mp1.add_force(self.force)
        mp2.add_force(self.force)

    def direction(self):
        return (self.__mp2.coor - self.__mp1.coor).normalize()

    def force(self):
        l = (self.__mp2.coor - self.__mp1.coor).len()
        dl = l - self.__l0

        if dl > self.__l0:
            raise Exception(
                "Undefined behaviour of the spring. Mass points should colide or pass through each other."
            )  # Add rebound by multiplying velocities by -0.8 for example at sticking point

        magnitude = -self.__k * (l - self.__l0)
        return self.direction() * magnitude

    def simulate(self, t, dt):
        self.__solver((self.__mp1, self.__mp2), t, dt)
