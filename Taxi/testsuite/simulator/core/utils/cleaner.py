"""
    Resets all memory storages
"""

from simulator.core import config
from simulator.core import queue
from simulator.core.modules import candidates
from simulator.core.modules import orders
from simulator.core.modules import virtual_tariffs


def clear_all():
    config.clear()
    queue.EventQueue.clear()
    candidates.CandidatesModel.clear()
    orders.OrdersModel.clear()
    virtual_tariffs.VirtualTariffsModel.clear()
