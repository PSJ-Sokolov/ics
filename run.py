from server import makeServer
server = makeServer(i = 2.0, di = 5, hi = 10)
server.port = 8521 # Default port
server.launch()
