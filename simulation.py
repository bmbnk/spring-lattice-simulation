import matplotlib.pyplot as plt
from numerical import euler, verlet

m = 1
k = 0.001
l0 = 1
dt = 1e-1
t = 10000

l = 1.2
v = 0.1

ls, _ = euler(m, k, l0, dt, t, l, v)

plt.plot(range(len(ls)), ls, label="Euler")
plt.xlabel("Steps")
# plt.ylabel("Length")
plt.ylabel("Energy")
plt.title(f"{dt=}")

ls, _ = verlet(m, k, l0, dt, t, l, v)
plt.plot(range(len(ls)), ls, label="Verlet")


plt.legend()
plt.show()
