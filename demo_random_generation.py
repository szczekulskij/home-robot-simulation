#!/usr/bin/env python3

"""
Test script showing how to build a world and use it
"""
import os
import argparse
import numpy as np
import random

from src.core import World
from src.gui import start_gui

def generate_random_world():
    """Create a test world"""
    world = World()

    # 1. Create a room
    r1coords = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
    world.add_room(
        room_coordinates=r1coords,
        room_name = "room1",
        room_color=[0, 0, 0],
    )

    # 2. Add tables
    nr_tables = random.randint(2, 3)
    for i in range(nr_tables):
        table_name = "table" + str(i)
        world.add_random_table(
            room_name="room1",
            parent = "room1",
            name=table_name,
        )

    # 3. Add objects
    for table in world.tables:
        nr_objects = random.randint(2, 5)
        for i in range(nr_objects):
            world.add_random_object(
                table_name=table.name,
            )

    return world



if __name__ == "__main__":
    world = generate_random_world()
    start_gui(world)
