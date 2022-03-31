import random
from statistics import mean

from mesa import Model
from mesa.time import SimultaneousActivation # updating scheme for synchronous updating
from mesa.time import RandomActivation # for asynchronous updating
from mesa.space import SingleGrid # spatial grid
from mesa.datacollection import DataCollector # Data collection, to plot mean infectivity

from cell import Cell, CellState # Function that describes behaviour of single cells

CS = CellState
def getSt(s):
    """Get an iterator of one and only one kind of state `s' out of the model `m'"""
    def f(m):
        return list(filter(lambda c: c.state == s, m.schedule.agents)) # must wrap in list which is dumb.
    return f
getI, getS = getSt(CS.INFECTED), getSt(CS.SUSCEPTIBLE)

def fracN(g):
    """Get the fraction of cells in `m' that fall under predicate `g'"""
    def f(m):
        return len(g(m)) / len(m.schedule.agents)
    return f
fracI, fracS = fracN(getI), fracN(getS)

#Computes the mean infection duration in all infected individuals
compute_mean_infduration = lambda m: mean(x.infection_duration for x in getI(m))

class SIRModel(Model):
    """Description of the model"""
    def __init__(self, width, height):
        # Set the model parameters
        self.infectivity        = 2.0  # Infection strength per infected individual
        self.infection_duration = 5    # Duration of infection
        self.r                  = 0.04 # Reproduction rate per susceptible
        self.d                  = 0.05 # Natural death rate
        self.h_inf              = 10.  # Scaling of infectivity

        self.grid     = SingleGrid(width, height, torus=True)
        self.schedule = SimultaneousActivation(self)
        for (contents, x, y) in self.grid.coord_iter():
            # Place randomly generated individuals
            cell = Cell((x,y), self)
            rand = random.random()
            if rand < 0.1:
                cell.state = CellState.SUSCEPTIBLE
            elif rand < 0.2:
                cell.state       = CellState.INFECTED
                cell.inf         = self.infectivity
                cell.infduration = self.infection_duration
                cell.timecounter = random.randint(0, self.infection_duration)
            else:
                cell.state = CellState.SUSCEPTIBLE
            self.grid.place_agent(cell, (x,y))
            self.schedule.add(cell)

        # Add data collector, to plot the number of individuals of different types
        self.datacollector1 = DataCollector(model_reporters={"S": fracS, "I": fracI})

        # Add data collector, to plot the mean infection duration
        self.datacollector2 = DataCollector(model_reporters={"Mean_infduration": compute_mean_infduration})

        self.running = True

    def step(self):
        self.datacollector1.collect(self)
        self.datacollector2.collect(self)
        self.schedule.step()
