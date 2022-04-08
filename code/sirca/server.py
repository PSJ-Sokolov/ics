# STD INCLUDE:
from __future__ import annotations

# MESA INCLUDE:
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

# USER INCLUDE:
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
    portrayal = {
        'Shape': 'rect',
        'w': 1,
        'h': 1,
        'Filled': 'true',
        'Layer': 1,
    }
    # logging.debug(f"Cell at {cell.position} with state: {cell.now.state}")
    portrayal["Color"] = COLORS[cell.now.state]
    return portrayal


def make_grid(width=100, height=100):
    return CanvasGrid(portray_cell, width, height, 5 * width, 5 * height)


# Make a chart for plotting the density of individuals
# TODO turn this into a stacked graph (if MESA supports this)
chartSIR = ChartModule([
    {'Label': 'S', 'Color': 'grey'},
    {'Label': 'I', 'Color': COLORS[CellState.INFECTED]},
    {'Label': 'R', 'Color': COLORS[CellState.RESISTANT]},
], data_collector_name='dataCollector1')
# Let chart plot the mean infection time
chartMI = ChartModule([{"Label": "Mean_infection_duration", "Color": "Black"}],
                      data_collector_name="dataCollector2")


def make_server(i=2.0, di=5, hi=10, dr=10, d=0.1, t=True, w=100, h=100):
    """ Launch the server that will run and display the model """
    return ModularServer(model_factory(i, di, hi, dr, d, t),
                         [make_grid(w, h), chartSIR, chartMI],
                         "SIR-model",
                         {"width": w, "height": h})
