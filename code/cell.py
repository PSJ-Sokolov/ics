from __future__ import annotations
import logging
import random
from enum import Enum, auto
from mesa import Agent
from dataclasses import dataclass
import typing


class CellState(Enum):
    """An enum that determines the states that the cells in our CA can be in.

    Because we use a SIR model they can either be S -- SUSCEPTIBLE, I -- INFECTED, or R -- RESISTANT
    """
    SUSCEPTIBLE = auto()
    INFECTED = auto()
    RESISTANT = auto()


@dataclass
class MutableData:
    state: CellState = CellState.SUSCEPTIBLE  # State of cell of CA = SUS | INF | RES
    infectiousness: float = 0.0  # Infection strength per infected individual
    infection_duration: int = 0  # Duration of infection
    resistance_duration: int = 0  # Duration of resistance
    tick: int = 0  # Current tick the cell is on.


class Cell(Agent):
    """Description of the grid points of the CA"""

    def __init__(self, position, model, initial_state=CellState.SUSCEPTIBLE):
        """Create cell in given x,y position, with given initial state"""
        super().__init__(position, model)
        self.position = position
        self.now = MutableData(initial_state)
        self.nxt = MutableData()

    @property
    def neighbors(self) -> list['Cell']:
        """ Get a list of the 8 surrounding neighbors of the now cell (
        cardinal and diagonal). """
        return self.model.grid.get_neighbors(self.position, moore=True,
                                             include_center=False)

    @property
    def infection_load(self):
        return sum(n.now.infectiousness for n in self.neighbors)

    def step(self):
        """Compute the next state of a cell"""
        self.nxt = self.now  # Ordinary case: Just update

        if self.now.state == CellState.SUSCEPTIBLE:
            self.transfer_state_s_to_i()
        elif self.now.state == CellState.INFECTED:
            self.transfer_state_i_to_r()
        elif self.now.state == CellState.RESISTANT:
            self.transfer_state_r_to_s()

    def transfer_state_s_to_i(self):
        logging.debug(f'SUS AT: {self.position} IN{self}')
        neighbors: list[Cell] = self.neighbors
        logging.debug(f'NEIGBOURS: {neighbors}')
        # Sum total_infection for the now cell.
        logging.debug(f'TOTAL INFECTIOUSNESS IS {self.infection_load}')

        infection_probability, infection_load = 0.0, self.infection_load
        # This deals with the evolution of the disease.
        if infection_load > 0:
            infection_probability = infection_load / (
                    infection_load + self.model.h_inf)
        # Take a random cell from the neighboring diseased cells to inherit the disease characteristics from.
        # TODO Fix this, this should be able to be done more cleanly.
        logging.debug(f'infection_probability IS {infection_probability}')
        if random.random() < infection_probability:
            logging.debug('RANDOMNESS DID TRIGGER IN THE STEP METHOD')
            self.nxt.state = CellState.INFECTED
            # Inherit infectiousness of one infecting neighbor.now.
            infection_probability_sum = 0.0  # A random value that gets bumped up as time goes on.
            rand = random.uniform(0,
                                  infection_load)  # A random value that is uniformly distributed,
            # it goes from zero to the total infectiousness..
            # Filter the cells that are diseased.
            for neighbor in neighbors:
                if neighbor.now.state == CellState.SUSCEPTIBLE:
                    # bump up the bump value by its susceptibility.
                    infection_probability_sum += neighbor.now.infectiousness
                    # if the cell has not randomly been infected yet by one of its neighbors the change of
                    # infection will rise.
                    if rand < infection_probability_sum:
                        # Inherit pathogen characteristics from infecting neighbor.now.
                        self.nxt.infectiousness = neighbor.now.infectiousness
                        self.nxt.infection_duration = neighbor.now.infection_duration
                        break
        # This just seems (?) to amount to taking one of the INFECTED neighbors of a
        # SUSCEPTIBLE cell at random and inheriting its characteristics
        # when becoming infected by it at random.

        # TODO We can use something like:
        # random.choices(neighbors, weights=(neighbors weighted by infectiousness))
        # Infectiousness
        # to replace almost this whole part of the method. (I think?)

    def transfer_state_i_to_r(self):
        if self.now.tick > self.now.infection_duration:
            self.nxt = MutableData(CellState.RESISTANT)
        else:
            self.now.tick += 1

    def transfer_state_r_to_s(self):
        if self.now.tick > self.now.resistance_duration:
            self.nxt = MutableData(CellState.SUSCEPTIBLE)
        else:
            self.now.tick += 1

    def advance(self):
        """Set the now state to the new calculated internal state."""
        self.now = self.nxt
