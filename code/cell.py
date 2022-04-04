import logging
import random
from enum import Enum, auto
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
        self.x,self.y                 = position
        self.state                    = initial_state

        # Ceremony for the framework:
        self._next_state              = None
        self._next_infectivity        = None
        self._next_infection_duration = None

        # Stuff that is relevant to our model:
        self.time                     = 0   # Duration infection
        self.infection_duration       = 0
        self.infectivity              = 0.0 # Infectivity

    def step(self):
        """Compute the next state of a cell"""
        # Assume cell is unchanged, unless something happens below
        self._next_infectivity        = self.infectivity
        self._next_infection_duration = self.infection_duration
        self._next_state              = self.state

        # Susceptibles - might die or get infected
        if self.state == CellState.SUSCEPTIBLE:
            logging.debug(f'SUS AT: {self.x,self.y} IN{self}')
            # Get a list of the 8 surrounding neighbors of the current cell (cardinal and diagonal).
            neighbors = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
            # Summate total_infection for the current cell.
            total_infectivity = sum(neighbor.infectivity for neighbor in neighbors)
            logging.debug(f'TOTAL INFECTIVITY IS {total_infectivity}')

            infprob = 0.0
            # This deals with the evolution of the disease.
            if total_infectivity > 0:
                infprob = total_infectivity / (total_infectivity + self.model.h_inf)
            # Take a random cell from the neighboring diseased cells to inherit the disease characteristics from.
            # TODO Fix this, this should be able to be done more cleanly.
            logging.debug(f'infprob IS {infprob}')
            if random.random() < infprob:
                logging.debug('RANDOMNESS DID TRIGGER IN THE STEP METHOD')
                self._next_state = CellState.INFECTED
                # Inherit infectivity of one infecting neighbor.
                infprobsum = 0.0                                  # A random value that gets bumped up as time goes on.
                rand       = random.uniform(0, total_infectivity) # A random value that is uniformly distributed,
                # it goes from zero to the total infectivity..
                # Filter the cells that are diseased.
                for neighbor in neighbors:
                    if neighbor.state == CellState.SUSCEPTIBLE:
                        # bump up the bump value by its susceptibility.
                        infprobsum += neighbor.infectivity
                        # if the cell has not randomly been infected yet by one of its neighbors the change of
                        # infection will rise.
                        if rand < infprobsum:
                            # Inherit pathogen characteristics from infecting neighbor.
                            self._next_infectivity = neighbor.inf
                            self._next_infection_duration = neighbor.infduration
                            break
            # This just seems (?) to amount to taking one of the INFECTED neighbors of a
            # SUSCEPTIBLE cell at random and inheriting its characteristics
            # when becoming infected by it at random.

            # TODO We can use something like:
            # random.choices(neigbors, weights=(neighbors weighted by infectivity))
            # Infectiousness
            # to replace almost this whole part of the method. (I think?)

        # If the cell was SUSCEPTIBLE and it was sick for long enough we will set it to "CellState.RECOVERED"
        elif self.state == CellState.INFECTED:
            # Cells will recover over time.
            if  self.time > self.infection_duration:
                self._next_state              = CellState.RECOVERED
                self._next_infectivity        = 0.0
                self._next_infection_duration = 0
                self.time                     = 0
            # Else count how long it has been ill (and apply potential mutations *on next pass*)
            else:
                self.time += 1

    def advance(self):
        """Set the current state to the new calculated internal state."""
        self.state              = self._next_state
        self.infectivity        = self._next_infectivity
        self.infection_duration = self._next_infection_duration
