"""


"""
# STD IMPORT
import logging
import random
from statistics import mean, StatisticsError
from mesa.space import SingleGrid
from mesa.time import  SimultaneousActivation
from mesa.datacollection import DataCollector

# MESA:
import mesa

# USER IMPORT:
import cell

# The next bit uses some functional programming techniques (Haskell,
# LISP) such as partial application and currying.

CS, cs = cell.CellState, lambda m: m.schedule.agents


def frac_n(s: cell.CellState):
    """Currying function that manufactures functions that calculate fraction
    of cells in a certain state `s' inside model `m' """
    return lambda m: len(
        [c.now.state for c in cs(m) if c.now.state == s]) / len(cs(m))


fracS, fracI, fracR = frac_n(CS.SUSCEPTIBLE), frac_n(CS.INFECTED), frac_n(
    CS.RESISTANT)


def model_factory(i=2.0, di=5, hi=10, dr=10, d=0.1, w=100, h=100, t=True):
    class SIRModel(mesa.Model):
        """Description of the model"""

        def __init__(self, width: int, height: int):
            """"""
            # Set the model parameters:
            n = 1
            d = 10
            s = -1
            f = 1 + (s * (n/d))
            self.infectiousness = 0.03
            self.infection_duration = 10
            self.resistance_duration = int(f * self.infection_duration)
            self.h_inf = 10
            self.seed_density = 10 / (w * h)
            self.torus = False

            # Initialize components:
            self.grid = mesa.space.SingleGrid(width, height, torus=self.torus)
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
                                        random.randint(0,
                                                       self.infection_duration)
                                        )
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

            self.dataCollector3 = mesa.datacollection.DataCollector(
                model_reporters={
                    "Mean_resistance_duration": self.mean_resistance_duration
                })

            self.dataCollector4 = mesa.datacollection.DataCollector(
                model_reporters={
                    "Mean_resistant_tick": self.mean_resistant_tick
                })

            self.dataCollector5 = mesa.datacollection.DataCollector(
                model_reporters={
                    "Mean_infected_tick": self.mean_infected_tick
                })

        def mean_infection_duration(self) -> float:
            """Computes the mean infection duration in all infected
            individuals """
            xs = cs(self)
            return mean(c.now.infection_duration for c in cs(self)
                        if c.now.state == CS.INFECTED)

        def mean_infection_duration(self) -> float:
            """Computes the mean infection duration in all infected
            individuals """
            return mean(c.now.infection_duration for c in cs(self)
                        if c.now.state == CS.INFECTED)

        def mean_resistance_duration(self) -> float:
            """Computes the mean resistance duration in all resistant
            individuals """
            return mean(c.now.resistance_duration for c in cs(self)
                        if c.now.state == CS.INFECTED)

        def mean_resistant_tick(self) -> float:
            """Computes the mean resistance duration in all resistant
            individuals """
            try:
                m = mean(c.now.tick for c in cs(self) if c.now.state ==
                         CS.RESISTANT)
            except StatisticsError as Err:
                return 0
            else:
                return m

        def mean_infected_tick(self) -> float:
            """Computes the mean resistance duration in all resistant
            individuals """
            return mean(c.now.tick for c in cs(self) if c.now.state ==
                        CS.INFECTED)


        @property
        def parameters(self) -> str:
            return f"i:{self.infectiousness} di:{self.infection_duration} " \
                   f"dr:{self.resistance_duration} h_inf:{self.h_inf} " \
                   f" d:{self.seed_density} t:{self.torus}"

        def step(self):
            self.dataCollector1.collect(self)
            self.dataCollector2.collect(self)
            self.dataCollector3.collect(self)
            self.dataCollector4.collect(self)
            self.dataCollector5.collect(self)
            self.schedule.step()

    return SIRModel
