#!/usr/bin/python
import logging
import statistics

from server import makeServer

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run model', epilog='live long and prosper!')
    parser.add_argument('-i', action='store', type=float, default=2.0,   help='Provide infectivity (2.0 by default)')
    parser.add_argument('-d', action='store', type=int,   default=5,     help='Provide infectivity_duration (5 by default)')
    parser.add_argument('-r', action='store', type=int,   default=10,    help='Provide h_infectivity (10 by default)')
    args = parser.parse_args()
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.WARNING)
    logging.info(args)

    try:
        server = makeServer(args.i, args.d, args.r)
        server.launch()
    except statistics.StatisticsError:
        print("THERE ARE NO MORE INFECTED CELLS")
    finally:
        print("TERMINATING!")
else:
    server = makeServer()
