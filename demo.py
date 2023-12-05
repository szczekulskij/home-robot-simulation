#!/usr/bin/env python3

"""
Test script showing how to build a world and use it with pyrobosim
"""
import os
import argparse
import numpy as np

from src.core import World
from src.gui import start_gui




def create_world():
    """Create a test world"""
    world = World()

    # Add rooms
    r1coords = [(-20, -10), (20, -10), (20, 10), (-20, 10)]
    world.add_room(
        room_coordinates=r1coords,
        room_name = "room1",
        room_color=[1, 0, 0],
    )
    # r2coords = [(1.75, 2.5), (3.5, 2.5), (3.5, 4), (1.75, 4)]
    # world.add_room(footprint=r2coords, color=[0, 0.6, 0])
    # r3coords = [(-1, 1), (-1, 3.5), (-3.0, 3.5), (-2.5, 1)]
    # world.add_room(footprint=r3coords, color=[0, 0, 0.6])

    table1 = world.add_table(
        # table_coordinates = None, parent=None, name=None, color=None
        table_coordinates = [(0.5, 0.5), (1.0, 0.5), (1.0, 1.0), (0.5, 1.0)],
        parent = "room1"
    )

    return world


if __name__ == "__main__":
    world = create_world()
    start_gui(world)
