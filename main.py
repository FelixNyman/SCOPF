import numpy as np
from solve import solve
from network import Network

# Idea coppy solution as inital guess fro partial derivateion. in OPF



network = Network("hgj")

network.buses_from_file("sfd")
network.matrices()
solve(network)

