import math
from typing import Callable

import torch


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

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            + "("
            + ", ".join([str(coor) for coor in self])
            + ")"
        )

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
        self.__f_history = []

    @property
    def a(self):
        f_overall = Vector3D(0, 0, 0)
        for f in self.__forces:
            f_overall += f()

        self.__f_history.append(f_overall)
        return f_overall / self.m

    @property
    def coor(self):
        return self.__coor

    @coor.setter
    def coor(self, value):
        self.__coor = value
        self.__coor_history.append(value)

    @property
    def history(self):
        return (self.__coor_history, self.__v_history, self.__f_history)

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


class HingePotential:
    def __init__(self, spring1, spring2, k):
        self.sp1 = spring1
        self.sp2 = spring2
        self.__k = k
        self.__common_mp = None
        self.__edge_mps = None

        sp1mps = [self.sp1.mp1, self.sp1.mp2]
        sp2mps = [self.sp2.mp1, self.sp2.mp2]

        for sp1mp in sp1mps:
            for sp2mp in sp2mps:
                if sp1mp is sp2mp:
                    self.__common_mp = sp1mp
                    break

        self.__edge_mps = [mp for mp in sp1mps + sp2mps if mp is not self.__common_mp]

        r1 = self.__edge_mps[0].coor - self.__common_mp.coor
        r2 = self.__edge_mps[1].coor - self.__common_mp.coor
        self.__theta0 = math.acos((r1 @ r2) / (r1.len() * r2.len()))

        self.__common_mp.add_force(self.force_mp2)
        self.__edge_mps[0].add_force(self.force_mp1)
        self.__edge_mps[1].add_force(self.force_mp3)

    def __force(self, i):
        """i is an index for node: 1, 2, 3 - where 2 is the node in the middle"""
        rs = [
            torch.tensor([float(c) for c in self.__edge_mps[0].coor]),
            torch.tensor([float(c) for c in self.__common_mp.coor]),
            torch.tensor([float(c) for c in self.__edge_mps[1].coor]),
        ]

        rs[i - 1].requires_grad_()

        r12 = rs[0] - rs[1]
        r32 = rs[2] - rs[1]
        v = (
            -self.__k
            * (
                torch.acos((torch.dot(r32, r12)) / (torch.norm(r32) * torch.norm(r12)))
                - torch.pi / 3
            )
            ** 2
            / 2
        )

        v.backward()
        f = Vector3D(*[float(a) for a in rs[i - 1].grad])
        return f

    def force_mp1(self):
        return self.__force(1)

    def force_mp2(self):
        return self.__force(2)

    def force_mp3(self):
        return self.__force(3)


class System:
    def __init__(
        self,
        coors,
        masses,
        connections,
        k_vals,
        s_lenghts,
        solver,
        squeeze=True,
        hinge_potential=True,
        hinge_k=0.01,
    ):
        assert len(coors) == len(masses)
        assert len(connections) == len(k_vals) == len(s_lenghts)

        self.mps = []
        self.springs = []
        self.__solver = solver

        for i, (c, m) in enumerate(zip(coors, masses)):
            mp = MassPoint(m, c, Vector3D(0, 0, 0))
            self.mps.append(mp)

            ### Add off the plane velocity to the middle point ###
            # if i == len(coors) // 2:
            #     v_val = 1
            #     v = Vector3D(1, 1, 1).normalize() * v_val
            #     mp.v = v

        for con, k, s_len in zip(connections, k_vals, s_lenghts):
            mps = []
            for mp in self.mps:
                if mp.coor in con:
                    mps.append(mp)

            spring = Spring(k, s_len, mps[0], mps[1])
            self.springs.append(spring)

        if hinge_potential:
            self.__add_hinge_potential(self.springs, hinge_k)

        if squeeze:
            self.__squeeze()

    def simulate(self, t, dt):
        self.__solver(self.mps, t, dt, pbar=True)

    def __add_hinge_potential(self, springs: list[Spring], k):
        vert_springs = []
        nvert_springs = []

        for s in springs:
            r12 = s.mp1.coor - s.mp2.coor
            if r12.len() in r12 or -r12.len() in r12:
                vert_springs.append(s)
            else:
                nvert_springs.append(s)

        for vs in vert_springs:
            for vs_mpcoor in [vs.mp1.coor, vs.mp2.coor]:
                for s in nvert_springs:
                    if vs_mpcoor in [s.mp1.coor, s.mp2.coor]:
                        HingePotential(vs, s, k)

    def __squeeze(self, velocity=0.1, ax=1):
        """Add opposite velocities on the opposite sides of the lattice in y axis"""
        v = Vector3D(0, 0, 0)
        v[ax] = velocity

        min_dim = float("inf")
        max_dim = -float("inf")
        for mp in self.mps:
            if mp.coor[ax] < min_dim:
                min_dim = mp.coor[ax]
            if mp.coor[ax] > max_dim:
                max_dim = mp.coor[ax]

        min_dim_sec = float("inf")
        max_dim_sec = -float("inf")
        for mp in self.mps:
            if mp.coor[ax] < min_dim_sec and mp.coor[ax] > min_dim:
                min_dim_sec = mp.coor[ax]
            if mp.coor[ax] > max_dim_sec and mp.coor[ax] < max_dim:
                max_dim_sec = mp.coor[ax]

        for mp in self.mps:
            if mp.coor[ax] in [min_dim, min_dim_sec]:
                mp.v = v
            elif mp.coor[ax] in [max_dim, max_dim_sec]:
                mp.v = v * -1
