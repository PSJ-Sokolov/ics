# STD IMPORT
import random
from statistics import mean

# MESA:
import mesa
from mesa import Model
from mesa.datacollection import \
    DataCollector  # Data collection, to plot mean infectiousness
from mesa.space import SingleGrid  # spatial grid
from mesa.time import RandomActivation  # for asynchronous updating
from mesa.time import \
    SimultaneousActivation  # updating scheme for synchronous updating

# USER IMPORT:
import cell

# The next bit uses some functional programming techniques (Haskell, LISP) such as partial application and currying.

CS, cs = cell.CellState, lambda m: m.schedule.agents


def frac_n(s: cell.CellState):
    """Currying function that manufactures functions that calculate fraction of cells in a certain state `s' inside
    model `m' """
    return lambda m: len(
        [c.now.state for c in cs(m) if c.now.state == s]) / len(cs(m))


fracS, fracI, fracR = frac_n(CS.SUSCEPTIBLE), frac_n(CS.INFECTED), frac_n(
    CS.RESISTANT)


class SIRModel(mesa.Model):
    """Description of the model"""

    def __init__(self, width: int, height: int):
        """"""
        # Set the model parameters:
        self.infectiousness: float = 2.0
        self.infection_duration: cell.tick = 5  # Duration of infection
        self.resistance_duration: cell.tick = 10
        self.h_inf: float = 10  # Scaling of infectiousness
        self.seed_density: float = 0.1

        # Initialize components:
        self.grid = mesa.space.SingleGrid(width, height, torus=True)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.running = True

        # Seed the board with infected cells randomly:
        for (_, x, y) in self.grid.coord_iter():
            # Place randomly generated individuals
            c = cell.Cell((x, y), self)
            if random.random() < self.seed_density:
                c.now = cell.Genome(cell.CellState.INFECTED,
                                    self.infectiousness,
                                    self.infection_duration,
                                    self.resistance_duration,
                                    random.randint(0, self.infection_duration))
            self.grid.place_agent(c, (x, y))
            self.schedule.add(c)

        # Plot fraction of population by type.
        self.dataCollector1 = mesa.datacollection.DataCollector(
            model_reporters={'S': fracS, 'I': fracI, 'R': fracR})

        # Plot mean_infection_duration
        self.dataCollector2 = mesa.datacollection.DataCollector(
            model_reporters={
                "Mean_infection_duration": self.mean_infection_duration
            })

    def mean_infection_duration(self):
        """Computes the mean infection duration in all infected individuals"""
        return mean(c.now.infection_duration for c in cs(self)
                    if c.now.state == CS.INFECTED)

    def step(self):
        self.dataCollector1.collect(self)
        self.dataCollector2.collect(self)
        self.schedule.step()


def model_factory(i=2.0, di=5, hi=10, dr=10, d=0.1) -> SIRModel:
    class ParameterizedSIRModel(SIRModel):
        def __init__(self, width, height):
            super().__init__(width, height)
            self.infectiousness = i
            self.infection_duration = di
            self.resistance_duration = dr
            self.h_inf = hi
            self.seed_density = d

    return ParameterizedSIRModel
