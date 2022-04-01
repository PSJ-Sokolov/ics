import numpy as np
import matplotlib.pyplot as plt

# Parameters
Tinf = 5
Timm = 5
Inf = 2.0
h = 10


maxtime = 25

# Initial values of prey and predator
St = 0.8
It = 0.1
Rt = 0.1

# Arrays with time points and simulation outcomes
times = np.arange(0,maxtime)
S = []
I = []
R = []

for i in range(maxtime):
    # Add data to data arrays:
    S.append(St)
    I.append(It)
    R.append(Rt)
    # Calculate next step:
    St1 = St + (1/Timm)*Rt - 8*Inf*It*St/(8*Inf*It+h)
    It1 = It + 8*Inf*It*St/(8*Inf*It+h) - (1/Tinf)*It
    Rt1 = Rt + (1/Tinf)*It - (1/Timm)*Rt
    # Set values to next step:
    St = St1
    It = It1
    Rt = Rt1

# Plot
plt.plot(times, S, 'black', lw = 2.0)
plt.plot(times, I, 'red', lw = 2.0)
plt.plot(times, R, 'blue', lw = 2.0)
plt.xlabel("Time")
plt.ylabel("SIR MODEL MFA")
plt.show()
