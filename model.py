import random

from mesa import Model
from mesa.time import SimultaneousActivation # updating scheme for synchronous updating
from mesa.time import RandomActivation # for asynchronous updating
from mesa.space import SingleGrid # spatial grid
from mesa.datacollection import DataCollector # Data collection, to plot mean infectivity

from cell import Cell # Function that describes behaviour of single cells

# Computes the mean infection duration in all infected individuals
def compute_mean_infduration(model):
    infs = [cell.infduration for cell in model.schedule.agents if cell.state == cell.Infected]
    return sum(infs)/len(infs)

# Computes the mean immunity duration in all recovered individuals
def compute_mean_immduration(model):
    imms = [cell.immduration for cell in model.schedule.agents if cell.state == cell.Recovered]
    return sum(imms)/len(imms)

# Computes the fraction of cells filled with an S individual
def fracS(model):
    nS = len([cell.state for cell in model.schedule.agents if cell.state == cell.Susceptible])
    return nS / len(model.schedule.agents)

# Computes the fraction of cells filled with an I individual
def fracI(model):
    nI = len([cell.state for cell in model.schedule.agents if cell.state == cell.Infected])
    return nI / len(model.schedule.agents)

# Computes the fraction of cells filled with an R individual
def fracR(model):
    nR = len([cell.state for cell in model.schedule.agents if cell.state == cell.Recovered])
    return nR / len(model.schedule.agents)

class SIRModel(Model):
    '''Description of the model'''
    
    def __init__(self, width, height):
        # Set the model parameters
        self.infectivity = 2.0      # Infection strength per infected individual
        self.infection_duration = 5 # Duration of infection
        self.immunity_duration = 5  # Duration of immunity
        self.r = 0.04               # Reproduction rate per susceptible #Not used
        self.d = 0.05               # Natural death rate                #Not used
        self.h_inf = 10.            # Scaling of infectivity
       
        self.grid = SingleGrid(width, height, torus=True)
        self.schedule = SimultaneousActivation(self)
        for (contents, x, y) in self.grid.coord_iter():
            # Place randomly generated individuals      #There should not be any empty cell
            cell = Cell((x,y), self)
            rand = random.random()
            if rand < 0.8:                              #Initial fraction of S
                cell.state = cell.Susceptible
            elif rand < 0.9:                            #Initial Fraction of S+I
                cell.state = cell.Infected
                cell.inf = self.infectivity
                cell.infduration = self.infection_duration
                cell.immduration = self.immunity_duration
                cell.timecounter = random.randint(0, self.infection_duration)
            else:
                cell.state = cell.Recovered
                cell.immduration = self.immunity_duration
                cell.timecounter = random.randint(0, self.immunity_duration)
            self.grid.place_agent(cell, (x,y))
            self.schedule.add(cell)

        # Add data collector, to plot the number of individuals of different types
        self.datacollector1 = DataCollector(model_reporters={"S": fracS, "I": fracI, "R": fracR})

        # Add data collector, to plot the mean infection duration
        self.datacollector2 = DataCollector(model_reporters={"Mean_infduration": compute_mean_infduration})
        
        # Add data collector, to plot the mean immunity duration
        self.datacollector3 = DataCollector(model_reporters={"Mean_immduration": compute_mean_immduration})
        
        self.running = True

    def step(self):
        self.datacollector1.collect(self)
        self.datacollector2.collect(self)
        self.datacollector3.collect(self)
        self.schedule.step()
    
