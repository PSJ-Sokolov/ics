# STD IMPORT
import random
from statistics import mean

# MESA:
from mesa                import Model
from mesa.datacollection import DataCollector          # Data collection, to plot mean infectivity
from mesa.space          import SingleGrid             # spatial grid
from mesa.time           import RandomActivation       # for asynchronous updating
from mesa.time           import SimultaneousActivation # updating scheme for synchronous updating

# USER IMPORT:
from cell                import Cell, CellState        # Function that describes behaviour of single cells

CS, cs = CellState, lambda m: m.schedule.agents
def fracN(s):
    """Currying function that manufactures functions that calculate fraction of cells in a certain state `s' inside model `m'"""
    return lambda m: len([c.state for c in cs(m) if c.state == s]) / len(cs(m))
fracS, fracI, fracR = fracN(CS.SUSCEPTIBLE), fracN(CS.INFECTED), fracN(CS.RECOVERED)

#Computes the mean infection duration in all infected individuals
compute_mean_infduration = lambda m: mean(c.infection_duration for c in cs(m) if c.state == CS.INFECTED)

def ModelFactory(i = 2.0, di = 5, hi = 10):
    class SIRModel(Model):
        """Description of the model"""
        def __init__(self, width, height):
            # Set the model parameters:
            self.infectivity        = i   # Infection strength per infected individual
            self.infection_duration = di # Duration of infection
            self.h_inf              = hi  # Scaling of infectivity

            # Initialize components:
            self.grid     = SingleGrid(width, height, torus=True)
            self.schedule = SimultaneousActivation(self)
            self.running  = True

            # Seed the board with infected cells randomly:
            for (_, x, y) in self.grid.coord_iter():
                # Place randomly generated individuals
                cell = Cell((x,y), self)
                rand = random.random()
                if rand < 0.1:
                    cell.state              = CellState.INFECTED
                    cell.infectivity        = self.infectivity
                    cell.infection_duration = self.infection_duration
                    cell.time               = random.randint(0, self.infection_duration)
                else:
                    cell.state = CellState.SUSCEPTIBLE
                self.grid.place_agent(cell, (x,y))
                self.schedule.add(cell)
            # TODO This should be done shorter.

            # Add data collector, to plot the number of individuals of different types
            self.datacollector1 = DataCollector(model_reporters={'S': fracS, 'I': fracI, 'R': fracR})

            # Add data collector, to plot the mean infection duration
            self.datacollector2 = DataCollector(model_reporters={"Mean_infduration": compute_mean_infduration})

        def step(self):
            self.datacollector1.collect(self)
            self.datacollector2.collect(self)
            self.schedule.step()
    return SIRModel
