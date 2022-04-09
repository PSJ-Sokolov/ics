from __future__ import annotations

import logging
import random
from enum import Enum, auto
from mesa import Agent, Model
from dataclasses import dataclass
import typing
from sys import float_info
EPS = float_info.epsilon
#import model

# from model import SIRModel

tick: typing.TypeAlias = int  # Ticks as type that have happened since event.


class CellState(Enum):
    """An enum that determines the states that the cells in our CA can be in.

    Because we use a SIR model they can either be S -- SUSCEPTIBLE, I -- INFECTED, or R -- RESISTANT
    """
    SUSCEPTIBLE = auto()
    INFECTED = auto()
    RESISTANT = auto()


@dataclass
class Genome:
    """"A struct of all the relevant data for a single cell in our CA.

    Putting it into a single struct makes updating the state of our Cells
    easier.

    Attributes
    ----------
    state : CellState
        State of a cell of our CA = SUSCEPTIBLE | INFECTED | RESISTANT
    infectiousness : float
        Severity of the infection per affected individual.
    infection_duration : tick
        Duration of the infection (in ticks).
    resistance_duration : tick
        How long the cell will stay resistant after recovery (in ticks).
    tick : tick
        The current tick the cell is on.
    """
    state: CellState = CellState.SUSCEPTIBLE
    infectiousness: float = 0.0
    infection_duration: tick = 0
    resistance_duration: tick = 0
    tick: tick = 0


class Cell(Agent):
    """Description of the grid points of the CA"""

    def __init__(self, position: tuple[int, int], model: model.SIRModel,
                 initial_state: CellState = CellState.SUSCEPTIBLE):
        """Create cell in given x,y position, with given initial state

        Parameters
        ----------
        model : object
        """
        super().__init__(position, model)
        self.position: tuple[int, int] = position
        self.now: Genome = Genome(initial_state)
        self.nxt: Genome = Genome()

    def step(self):
        """Compute the next state of a cell"""
        self.nxt = self.now  # Ordinary case: Just update

        if self.now.state == CellState.SUSCEPTIBLE:
            self.transfer_state_s_to_i()
        elif self.now.state == CellState.INFECTED:
            self.transfer_state_i_to_r()
        elif self.now.state == CellState.RESISTANT:
            self.transfer_state_r_to_s()

    @property
    def neighbors(self) -> list[Cell]:
        """ Get a list of the 8 surrounding neighbors of the now cell (
        cardinal and diagonal). """
        return self.model.grid.get_neighbors(self.position, moore=True,
                                             include_center=False)

    def get_neighbors_by_state(self, state: CellState) -> typing.Iterable[Cell]:
        """Get the neighbors of the current Cell that are of a certain
        CellState state.

        Parameters
        ----------
        state : CellState
            A state that we want to filter the neighbors by.

        Returns
        -------
        typing.Iterable[Cell]
            Neighbors of the current cell that have Cell.now.state == state
        """
        return (n for n in self.neighbors if n.now.state == state)

    @property
    def infected_neighbors(self) -> typing.Iterable[Cell]:
        """

        Returns
        -------

        """
        return self.get_neighbors_by_state(CellState.INFECTED)

    @property
    def random_infected_neighbor(self) -> Cell:
        xs = list(self.infected_neighbors)
        xsi = [x.now.infectiousness for x in xs]
        try:
            n = random.choices(xs, xsi)[0]
        except ValueError as err:
            logging.debug(f"INFECTED NEIGBORS: {xs=} WEIGHTS!: {xsi=}, {err}")
            raise SystemExit("CRASH AND BURN!")
        else:
            return n

    @property
    def infection_load(self) -> float:
        """The severity of the infection load the current cell is affected by

        Due to the infectiousness of the disease in neighboring Cells."""
        return sum(n.now.infectiousness for n in self.neighbors)

    @property
    def infection_probability(self) -> float:
        """Calculates the probability this cell could get infected.

        Returns
        -------
        The probability that this cell could get infected [0,1].
        """
        return self.infection_load / (self.infection_load + self.model.h_inf)

    @property
    def mutated_genome(self) -> Genome:
        i = max(EPS, self.now.infectiousness + random.gauss(0, 1))
        di = max(1, self.now.infection_duration + random.randrange(-1, 2))
        dr = max(1, self.now.resistance_duration + random.randrange(-1, 2))
        return Genome(CellState.INFECTED, i, di, dr, self.now.tick)

    def transfer_genome(self, state: CellState) -> Genome:
        """"""
        x = self.now
        return Genome(state, x.infectiousness, x.infection_duration,
                      x.resistance_duration, tick=0)

    def transfer_state_s_to_i(self):
        """Transfer the state from CellState.SUSCEPTIBLE to
        CellSTATE.INFECTED, if more time than self.infection_duration has
        passed, else just increment current tick.
        """
        # Do we have infected neighbors?
        logging.debug("ON SUSCEPTIBLE CELL")
        if list(self.infected_neighbors):
            logging.debug("THE SUSCEPTIBLE CELL HAS INFECTED NEIGHBORS")
            # And we're lucky enough to get infected.
            if random.random() < self.infection_probability:
                logging.debug("WE'RE GETTING INFECTED")
                # Get infected by a mutation of a random neighbor.
                logging.debug("CHOOSING A RANDOM NEIGBOR")
                if n := self.random_infected_neighbor:
                    logging.debug(f"THE RANDOM NEIGHBOR IS {n}, {n.now}")
                    # Take random infected neighboring cell & inherit from it.
                    self.nxt = n.mutated_genome

    def tick(self):
        self.now.tick += 1

    def transfer_state_i_to_r(self):
        """Transfer the state from CellState.INFECTED to
        CellSTATE.RESISTANT, if more time than self.infection_duration has
        passed, else just increment current tick.
        """
        logging.debug(f"ON INFECTED {self.position=}, {self.now=}")
        if self.now.tick > self.now.infection_duration:
            logging.debug(f"RECOVERING {self.position=}, {self.now=}")
            self.nxt = self.transfer_genome(CellState.RESISTANT)
        else:
            logging.debug(f"TICKING INFECTED {self.position=}, {self.now=}")
            self.tick()
            self.nxt = self.mutated_genome

    def transfer_state_r_to_s(self):
        """Transfer the state from CellState.RESISTANT to
        CellSTATE.SUSCEPTIBLE, if more time than self.resistance_duration has
        passed, else just increment current tick.
        """
        logging.debug(f"ON RESISTANT {self.position=}, {self.now=}")
        if self.now.tick > self.now.resistance_duration:
            logging.debug(f"AGAIN SUSCEPTIBLE {self.position=}, {self.now=}")
            self.nxt = self.transfer_genome(CellState.SUSCEPTIBLE)
        else:
            logging.debug(f"TICKING SUSCEPTIBLE {self.position=}, {self.now=}")
            self.tick()

    def advance(self):
        """Set the now state to the nxt calculated internal state."""
        logging.debug(f"NEXT: {self.nxt=}")
        self.now = self.nxt
