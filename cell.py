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
        self.infection          = 0.0        # Infectivity

    def step(self):
        """Compute the next state of a cell"""
        # Assume cell is unchanged, unless something happens below
        self._nextinf         = self.inf
        self._nextinfduration = self.infduration
        self._nextstate       = self.state

        # Susceptibles - might die or get infected
        if self.state == CellState.SUSCEPTIBLE:
            # Get a list of the 8 surrounding neighbors of the current cell (cardinal and diagonal).
            neighbors = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
            # Summate total_infection for the current cell.
            # TODO: fix this, using a loop to contsruct a new variable is an anti-patern,
            #       should use listcomp or gen expr instead.
            tot_inf = 0.0
            for neighbor in neighbors:
                if neighbor.state == self.Infected:
                    tot_inf += neighbor.inf
            infprob = 0.0

            # This deals with the evolution of the disease.
            if tot_inf > 0:
                infprob = tot_inf / (tot_inf + self.model.h_inf)
            if random.random() < infprob:
                self._nextstate = self.Infected
                # Inherit infectivity of one infecting neighbor.
                infprobsum = 0.0
                rand = random.uniform(0, tot_inf)
                for neighbor in neighbors:
                    if neighbor.state == CellState.SUSCEPTIBLE:
                        infprobsum += neighbor.inf
                        if rand < infprobsum:
                            # Inherit pathogen characteristics from infecting neighbor.
                            self._nextinf = neighbor.inf
                            self._nextinfduration = neighbor.infduration
                            break

        # If the cell was SUSCEPTIBLE and it was sick for long enough we consider it "RECOVERED"
        elif self.state == CellState.SUSCEPTIBLE:
            # Natural death or death by disease
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
