import numpy as np
import matplotlib.pyplot as plt

# Parameters
Tinf1 = 5
Tinf2 = 10
Timm = 5
Inf = 2.0
h = 10


maxtime = 25

# Initial values of prey and predator
St = 0.8
It = 0.1
Yt = 0.1
Rt = 0.0

# Arrays with time points and simulation outcomes
times = np.arange(0,maxtime)
S = []
I = []
Y = []
R = []

for i in range(maxtime):
    # Add data to data arrays:
    S.append(St)
    I.append(It)
    Y.append(Yt)
    R.append(Rt)
    # Calculate next step:
    St1 = St + (1/Timm)*Rt - 8*Inf*It*St/(8*Inf*It+h) - 8*Inf*Yt*St/(8*Inf*Yt+h)
    It1 = It + 8*Inf*It*St/(8*Inf*It+h) - (1/Tinf1)*It
    Yt1 = Yt + 8*Inf*Yt*St/(8*Inf*Yt+h) - (1/Tinf2)*Yt
    Rt1 = Rt + (1/Tinf1)*It + (1/Tinf2)*Yt - (1/Timm)*Rt
    # Set values to next step:
    St = St1
    It = It1
    Yt = Yt1
    Rt = Rt1
    

# Plot
plt.plot(times, S, 'black', lw = 2.0)
plt.plot(times, I, 'red', lw = 2.0)
plt.plot(times, Y, 'pink', lw = 2.0)
plt.plot(times, R, 'blue', lw = 2.0)
plt.xlabel("Time")
plt.ylabel("SIR MODEL MFA")
plt.show()
