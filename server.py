# STD INCLUDE:
import logging

# MESA INCLUDE:
from mesa.visualization.modules              import CanvasGrid
from mesa.visualization.modules              import ChartModule
from mesa.visualization.ModularVisualization import ModularServer

# USER INCLUDE:
from cell  import CellState
from model import SIRModel

# USER CONFIG:
logging.basicConfig(level=logging.WARNING)
DEBUG = logging.debug

COLORS = {
    CellState.SUSCEPTIBLE : 'white',
    CellState.INFECTED    : 'red' ,
    CellState.RECOVERED   : 'blue',
}

def portrayCell(cell):
    """ Portrayal function: defines the portrayal of the cells """
    assert cell is not None
    portrayal = {
        'Shape' : 'rect',
        'w'     :  1    ,
        'h'     :  1    ,
        'Filled': 'true',
        'Layer' :  1    ,
    }
    DEBUG(f"Cell at {cell.x, cell.y} with state: {cell.state}")
    portrayal["Color"] = COLORS[cell.state]
    return portrayal

""" Construct the simulation grid, all cells displayed as 5x5 squares """
gridwidth  = 100 # Change these parameters to change the grid size
gridheight = 100

# Make a grid to plot the population dynamics
grid  = CanvasGrid(portrayCell, gridwidth, gridheight, 5*gridwidth, 5*gridheight)
# Make a chart for plotting the density of individuals
chart = ChartModule([{"Label": "S", "Color": "grey"},{"Label": "I", "Color": "red"}], data_collector_name="datacollector1")
# Let chart plot the mean infection time
#chart = ChartModule([{"Label": "Mean_infduration", "Color": "Black"}], data_collector_name="datacollector2")


""" Launch the server that will run and display the model """
server = ModularServer(SIRModel,
                       [grid, chart],
                       "SIR-model",
                       {"width": gridwidth, "height": gridheight})
