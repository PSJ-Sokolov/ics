from enum import Enum
import random
from mesa import Agent

class CellState(Enum):
    """An enum that determines the states that the cells in our CA can be in.

    Because we use a SIR model they can either be S -- SUSCEPTIBLE, I -- INFECTED, or R -- RECOVERED

    We use the values to colour the cells later on (in server.py).
    """
    SUSCEPTIBLE = "grey"
    INFECTED    = "red"
    RECOVERED   = "blue"

class Cell(Agent):
    """Description of the grid points of the CA"""
    def __init__(self, position, model, initial_state = CellState.SUSCEPTIBLE):
        """Create cell in given x,y position, with given initial state"""
        # Ceremony for the super class:
        super().__init__(positon,model)
        self.x,self.y           = pos
        self.state              = init_state

        # Ceremony for the framework:
        self._nextstate         = None
        self._nextinf           = None
        self._nextinfduration   = None

        # Stuff that is relevant to our model:
        self.time               = 0          # Duration infection
        self.infection_duration = 0
        self.infection          = 0.0        # Infectivity

    def step(self):
        """Compute the next state of a cell"""
        # Assume cell is unchanged, unless something happens below
        self._nextinf = self.inf
        self._nextinfduration = self.infduration
        self._nextstate = self.state

        # Susceptibles - might die or get infected
        if self.state == CellState.SUSCEPTIBLE:
            # Natural death
            #if random.random() < self.model.d:
            if False:
                pass
            #    self._nextstate = 0
            # Infection?
            else:
                neis = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
                tot_inf = 0.0
                for nei in neis:
                    if nei.state == self.Infected:
                        tot_inf += nei.inf
                infprob = 0.0
                if tot_inf > 0:
                    infprob = tot_inf / (tot_inf + self.model.h_inf)
                if random.random() < infprob:
                    self._nextstate = self.Infected
                    # Inherit infectivity of one infecting neighbour
                    infprobsum = 0.0
                    rand = random.uniform(0, tot_inf)
                    for nei in neis:
                        if nei.state == CellState.SUSCEPTIBLE:
                            infprobsum += nei.inf
                            if rand < infprobsum:
                                # Inherit pathogen characteristics from infecting neighbour
                                self._nextinf = nei.inf
                                self._nextinfduration = nei.infduration
                                break

        elif self.state == CellState.SUSCEPTIBLE:
            # Natural death or death by disease
            if  self.timecounter > self.infduration:
                self._nextstate = self.Recovered
                self._nextinf = 0.0
                self._nextinfduration = 0
                self.timecounter = 0
            # Else count how long it has been ill and apply potential mutations
            else:
                self.timecounter += 1

    def advance(self):
        self.state = self._nextstate
        self.inf = self._nextinf
        self.infduration = self._nextinfduration
