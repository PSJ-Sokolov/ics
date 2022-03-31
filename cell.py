from enum import Enum, auto
import random
from mesa import Agent

class CellState(Enum):
    """An enum that determines the states that the cells in our CA can be in.

    Because we use a SIR model they can either be S -- SUSCEPTIBLE, I -- INFECTED, or R -- RECOVERED
    """
    SUSCEPTIBLE = auto()
    INFECTED    = auto()
    RECOVERED   = auto()

class Cell(Agent):
    """Description of the grid points of the CA"""
    def __init__(self, position, model, initial_state = CellState.SUSCEPTIBLE):
        """Create cell in given x,y position, with given initial state"""
        # Ceremony for the super class:
        super().__init__(position,model)
        self.x,self.y           = position
        self.state              = initial_state

        # Ceremony for the framework:
        self._nextstate         = None
        self._nextinf           = None
        self._nextinfduration   = None

        # Stuff that is relevant to our model:
        self.time               = 0          # Duration infection
        self.infection_duration = 0
        self.infectivity        = 0.0        # Infectivity

    def step(self):
        """Compute the next state of a cell"""
        # Assume cell is unchanged, unless something happens below
        self._nextinf         = self.infectivity
        self._nextinfduration = self.infection_duration
        self._nextstate       = self.state

        # Susceptibles - might die or get infected
        if self.state == CellState.SUSCEPTIBLE:
            # Get a list of the 8 surrounding neighbors of the current cell (cardinal and diagonal).
            neighbors = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
            # Summate total_infection for the current cell.
            total_infectivity = sum(neighbor.infectivity for neighbor in neighbors)

            infprob = 0.0
            # This deals with the evolution of the disease.
            if total_infectivity > 0:
                infprob = total_infectivity / (total_infectivity + self.model.h_inf)
            if random.random() < infprob:
                self._nextstate = self.Infected
                # Inherit infectivity of one infecting neighbor.
                infprobsum = 0.0
                rand = random.uniform(0, total_infectivity)
                for neighbor in neighbors:
                    if neighbor.state == CellState.SUSCEPTIBLE:
                        infprobsum += neighbor.inf
                        if rand < infprobsum:
                            # Inherit pathogen characteristics from infecting neighbor.
                            self._nextinf = neighbor.inf
                            self._nextinfduration = neighbor.infduration
                            break

        # If the cell was SUSCEPTIBLE and it was sick for long enough we will set it to "CellState.RECOVERED"
        elif self.state == CellState.SUSCEPTIBLE:
            # Cells will recover over time.
            if  self.timecounter > self.infection_duration:
                self._nextstate       = self.Recovered
                self._nextinf         = 0.0
                self._nextinfduration = 0
                self.timecounter      = 0
            # Else count how long it has been ill (and apply potential mutations *on next pass*)
            else:
                self.timecounter += 1

    def advance(self):
        """Set the current state to the new calculated internal state."""
        self.state       = self._nextstate
        self.inf         = self._nextinf
        self.infduration = self._nextinfduration
