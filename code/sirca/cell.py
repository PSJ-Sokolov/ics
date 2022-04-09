"""


"""
from __future__ import annotations
import random
from enum import Enum, auto
from mesa import Agent, Model
from dataclasses import dataclass
import typing
from sys import float_info
EPSILON = float_info.epsilon

tick: typing.TypeAlias = int  # Ticks as type that have happened since event.


class CellState(Enum):
    """An enum that determines the states that the cells in our CA can be in.

    Because we use a SIR model they can either be S -- SUSCEPTIBLE,
    I -- INFECTED, or R -- RESISTANT
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
        match self.now.state:
            case CellState.SUSCEPTIBLE:
                self.transfer_state_s_to_i()
            case CellState.INFECTED:
                self.transfer_state_i_to_r()
            case CellState.RESISTANT:
                self.transfer_state_r_to_s()

    @property
    def neighbors(self) -> list[Cell]:
        """ Get a list of the 8 surrounding neighbors of the now cell (
        cardinal and diagonal).

        Returns
        -------
        list[Cell]"""
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
        typing.Iterable[Cell]
        """
        return self.get_neighbors_by_state(CellState.INFECTED)

    @property
    def random_infected_neighbor(self) -> Cell:
        """

        Returns
        -------
        Cell

        """
        return random.choices(xs := list(self.infected_neighbors),
                              [x.now.infectiousness for x in xs])[0]

    @property
    def infection_load(self) -> float:
        """The severity of the infection load the current cell is affected by

        Due to the infectiousness of the disease in neighboring Cells.

        Returns
        -------
        float"""
        return sum(n.now.infectiousness for n in self.neighbors)

    @property
    def infection_probability(self) -> float:
        """Calculates the probability this cell could get infected.

        Returns
        -------
        float
        The probability that this cell could get infected [0,1].
        """
        return self.infection_load / (self.infection_load + self.model.h_inf)

    @property
    def mutated_genome(self) -> Genome:
        """

        Returns
        -------
        Genome
        """
        i = max(EPSILON, self.now.infectiousness + random.gauss(0, 1))
        di = max(1, self.now.infection_duration + random.randrange(-1, 2))
        dr = max(1, self.now.resistance_duration + random.randrange(-1, 2))
        return Genome(CellState.INFECTED, i, di, dr, self.now.tick)

    def transfer_genome(self, state: CellState) -> Genome:
        """"""
        return Genome(state, (x := self.now).infectiousness,
                      x.infection_duration,
                      x.resistance_duration, tick=0)

    def transfer_state_s_to_i(self):
        """Transfer the state from CellState.SUSCEPTIBLE to
        CellSTATE.INFECTED, if more time than self.infection_duration has
        passed, else just increment current tick.
        """
        if list(self.infected_neighbors):
            if random.random() < self.infection_probability:
                if n := self.random_infected_neighbor:
                    self.nxt = n.mutated_genome

    def tick(self):
        """Tick the internal time since a significant event by 1."""
        self.now.tick += 1

    def transfer_state_i_to_r(self):
        """Transfer the state from CellState.INFECTED to
        CellSTATE.RESISTANT, if more time than self.infection_duration has
        passed, else just increment current tick.
        """
        if self.now.tick > self.now.infection_duration:
            self.nxt = self.transfer_genome(CellState.RESISTANT)
        else:
            self.tick()
            self.nxt = self.mutated_genome

    def transfer_state_r_to_s(self):
        """Transfer the state from CellState.RESISTANT to
        CellSTATE.SUSCEPTIBLE, if more time than self.resistance_duration has
        passed, else just increment current tick.
        """
        if self.now.tick > self.now.resistance_duration:
            self.nxt = Genome()
        else:
            self.tick()

    def advance(self):
        """Set the now state to the nxt calculated internal state."""
        self.now = self.nxt
