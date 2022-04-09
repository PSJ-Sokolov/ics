"""

"""
from __future__ import annotations
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from cell import CellState, Cell
from model import model_factory

COLORS = {
    CellState.SUSCEPTIBLE: 'white',
    CellState.INFECTED: 'red',
    CellState.RESISTANT: 'blue',
}


def portray_cell(cell: Cell):
    """ Portrayal function: defines the portrayal of the cells """
    assert cell is not None
    portrayal = {'Shape': 'rect', 'r': 1, 'w': 1, 'h': 1,
                 'Filled': 'true',
                 'Layer': 0,
                 "Color": COLORS[cell.now.state]}
    return portrayal


def make_grid(width=100, height=100):
    return CanvasGrid(portray_cell, width, height, 5 * width, 5 * height)


# Make a chart for plotting the density of individuals
chartSIR = ChartModule([
    {'Label': 'S', 'Color': 'grey'},
    {'Label': 'I', 'Color': COLORS[CellState.INFECTED]},
    {'Label': 'R', 'Color': COLORS[CellState.RESISTANT]},
], data_collector_name='dataCollector1')

chartMI = ChartModule([{"Label": "Mean_infection_duration", "Color": "Black"}],
                      data_collector_name="dataCollector2")

chartDR = ChartModule([{"Label": "Mean_resistance_duration", "Color": "Black"}],
                      data_collector_name="dataCollector3")

chartRT = ChartModule([{"Label": "Mean_resistant_tick", "Color": "Black"}],
                      data_collector_name="dataCollector4")

chartIT = ChartModule([{"Label": "Mean_infected_tick", "Color": "Black"}],
                      data_collector_name="dataCollector5")


def make_server(i=2.0, di=5, hi=10, dr=10, d=0.1, t=True, w=100,
                h=100) -> ModularServer:
    """ Launch the server that will run and display the model """
    return ModularServer(model_factory(i, di, hi, dr, d, w, h, t), [
        make_grid(w, h), chartSIR, chartMI, chartDR, chartRT, chartIT,
    ], "SIR-model", {"width": w, "height": h})
