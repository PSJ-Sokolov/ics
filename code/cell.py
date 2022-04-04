import logging
import random
from enum import Enum, auto
from mesa import Agent


class CellState(Enum):
    """An enum that determines the states that the cells in our CA can be in.

    Because we use a SIR model they can either be S -- SUSCEPTIBLE, I -- INFECTED, or R -- RESISTANT
    """
    SUSCEPTIBLE = auto()
    INFECTED = auto()
    RESISTANT = auto()


class Cell(Agent):
    """Description of the grid points of the CA"""

    def __init__(self, position, model, initial_state=CellState.SUSCEPTIBLE):
        """Create cell in given x,y position, with given initial state"""
        # Ceremony for the super class:
        super().__init__(position, model)
        self.x, self.y = position
        self.state = initial_state

        # Ceremony for the framework:
        self._next_state = None
        self._next_infectiousness = None
        self._next_infection_duration = None

        # Stuff that is relevant to our model:
        self.time = 0  # Duration infection
        self.infection_duration = 0
        self.infectiousness = 0.0  # infectiousness

    def step(self):
        """Compute the next state of a cell"""
        # Assume cell is unchanged, unless something happens below
        self._next_infectiousness = self.infectiousness
        self._next_infection_duration = self.infection_duration
        self._next_state = self.state

        # Susceptibles - might die or get infected
        if self.state == CellState.SUSCEPTIBLE:
            logging.debug(f'SUS AT: {self.x, self.y} IN{self}')
            # Get a list of the 8 surrounding neighbors of the current cell (cardinal and diagonal).
            neighbors = self.model.grid.get_neighbors((self.x, self.y), moore=True, include_center=False)
            # Sum total_infection for the current cell.
            total_infectiousness = sum(neighbor.infectiousness for neighbor in neighbors)
            logging.debug(f'TOTAL INFECTIOUSNESS IS {total_infectiousness}')

            infection_probability = 0.0
            # This deals with the evolution of the disease.
            if total_infectiousness > 0:
                infection_probability = total_infectiousness / (total_infectiousness + self.model.h_inf)
            # Take a random cell from the neighboring diseased cells to inherit the disease characteristics from.
            # TODO Fix this, this should be able to be done more cleanly.
            logging.debug(f'infection_probability IS {infection_probability}')
            if random.random() < infection_probability:
                logging.debug('RANDOMNESS DID TRIGGER IN THE STEP METHOD')
                self._next_state = CellState.INFECTED
                # Inherit infectiousness of one infecting neighbor.
                infection_probability_sum = 0.0  # A random value that gets bumped up as time goes on.
                rand = random.uniform(0, total_infectiousness)  # A random value that is uniformly distributed,
                # it goes from zero to the total infectiousness..
                # Filter the cells that are diseased.
                for neighbor in neighbors:
                    if neighbor.state == CellState.SUSCEPTIBLE:
                        # bump up the bump value by its susceptibility.
                        infection_probability_sum += neighbor.infectiousness
                        # if the cell has not randomly been infected yet by one of its neighbors the change of
                        # infection will rise.
                        if rand < infection_probability_sum:
                            # Inherit pathogen characteristics from infecting neighbor.
                            self._next_infectiousness = neighbor.inf
                            self._next_infection_duration = neighbor.infduration
                            break
            # This just seems (?) to amount to taking one of the INFECTED neighbors of a
            # SUSCEPTIBLE cell at random and inheriting its characteristics
            # when becoming infected by it at random.

            # TODO We can use something like:
            # random.choices(neighbors, weights=(neighbors weighted by infectiousness))
            # Infectiousness
            # to replace almost this whole part of the method. (I think?)

        # If the cell was SUSCEPTIBLE and it was sick for long enough we will set it to "CellState.RESISTANT"
        elif self.state == CellState.INFECTED:
            # Cells will recover over time.
            if self.time > self.infection_duration:
                self._next_state = CellState.RESISTANT
                self._next_infectiousness = 0.0
                self._next_infection_duration = 0
                self.time = 0
            # Else count how long it has been ill (and apply potential mutations *on next pass*)
            else:
                self.time += 1

    def advance(self):
        """Set the current state to the new calculated internal state."""
        self.state = self._next_state
        self.infectiousness = self._next_infectiousness
        self.infection_duration = self._next_infection_duration
