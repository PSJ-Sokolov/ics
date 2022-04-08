# STD IMPORT
import random
from statistics import mean

# MESA:
from mesa import Model
from mesa.datacollection import \
    DataCollector  # Data collection, to plot mean infectiousness
from mesa.space import SingleGrid  # spatial grid
from mesa.time import RandomActivation  # for asynchronous updating
from mesa.time import \
    SimultaneousActivation  # updating scheme for synchronous updating

# USER IMPORT:
import cell
CellState = cell.CellState
tick = cell.tick
Cell = cell.Cell
Genome = cell.Genome

# The next bit uses some functional programming techniques (Haskell, LISP) such as partial application and currying.

CS, cs = CellState, lambda m: m.schedule.agents


def fracN(s: CellState):
    """Currying function that manufactures functions that calculate fraction of cells in a certain state `s' inside
    sir_model `m' """
    return lambda m: len(
        [c.now.state for c in cs(m) if c.now.state == s]) / len(cs(m))


fracS, fracI, fracR = fracN(CS.SUSCEPTIBLE), fracN(CS.INFECTED), fracN(
    CS.RESISTANT)
# Computes the mean infection duration in all infected individuals
compute_mean_infection_duration = lambda m: mean(
    c.now.infection_duration for c in cs(m) if c.now.state == CS.INFECTED)


class SIRModel(Model):
    """Description of the sir_model"""

    def __init__(self, width: int, height: int):
        # Set the sir_model parameters:
        self.infectiousness: float = 2.0  # Infection strength per infected
        # individual
        self.infection_duration: tick = 5  # Duration of infection
        self.resistance_duration: tick = 10
        self.h_inf: float = 10  # Scaling of infectiousness
        self.seed_density: float = 0.1

        # Initialize components:
        self.grid = SingleGrid(width, height, torus=True)
        self.schedule = SimultaneousActivation(self)
        self.running = True

        # Seed the board with infected cells randomly:
        for (_, x, y) in self.grid.coord_iter():
            # Place randomly generated individuals
            c = Cell((x, y), self)
            if random.random() < self.seed_density:
                c.now = Genome(CellState.INFECTED,
                               self.infectiousness,
                               self.infection_duration,
                               self.resistance_duration,
                               random.randint(0, self.infection_duration))
            self.grid.place_agent(c, (x, y))
            self.schedule.add(c)

        # Add data collector, to plot the number of individuals of different types
        self.dataCollector1 = DataCollector(
            model_reporters={'S': fracS, 'I': fracI, 'R': fracR})

        # Add data collector, to plot the mean infection duration
        self.dataCollector2 = DataCollector(model_reporters={
            "Mean_infection_duration": compute_mean_infection_duration})

    def step(self):
        self.dataCollector1.collect(self)
        self.dataCollector2.collect(self)
        self.schedule.step()


def model_factory(i=2.0, di=5, hi=10, d=0.1) -> SIRModel:
    class ParameterizedSIRModel(SIRModel):
        def __init__(self, width, height):
            super().__init__(width, height)
            self.infectiousness = i
            self.infection_duration = di
            self.h_inf = hi
            self.seed_density = d
    return ParameterizedSIRModel
