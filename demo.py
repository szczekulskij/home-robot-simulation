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
        room_color=[0, 0, 0],
    )
    # r2coords = [(1.75, 2.5), (3.5, 2.5), (3.5, 4), (1.75, 4)]
    # world.add_room(footprint=r2coords, color=[0, 0.6, 0])
    # r3coords = [(-1, 1), (-1, 3.5), (-3.0, 3.5), (-2.5, 1)]
    # world.add_room(footprint=r3coords, color=[0, 0, 0.6])

    t1coords = [(-15, -5), (-15, 5), (-10, 5), (-10, -5) ]
    table1 = world.add_table(
        table_coordinates = t1coords,
        parent = "room1",
        name = "table1",
    )

    object1 = world.add_object(
        centroid = (-12, -3),
        size = 0.5,
        parent = table1,
        name = "object1",
        color = (1, 1, 1),
    )

    return world


if __name__ == "__main__":
    world = create_world()
    start_gui(world)
