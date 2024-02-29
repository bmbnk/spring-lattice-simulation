class Vector3D:
    def __init__(self, a1, a2, a3):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3


class MassPoint:
    def __init__(self, mass, coordinates: Vector3D, velocity: Vector3D):
        self.mass = mass
        self.coor = coordinates
        self.v = velocity


class Spring:
    def __init__(self, k, p1: MassPoint, p2: MassPoint):
        self.p1 = p1
        self.p2 = p2
        self.k = k
