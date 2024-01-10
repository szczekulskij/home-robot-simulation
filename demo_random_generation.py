#!/usr/bin/env python3

"""
Test script showing how to build a world and use it
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
    r1coords = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
    world.add_room(
        room_coordinates=r1coords,
        room_name = "room1",
        room_color=[0, 0, 0],
    )

    table1 = world.add_random_table(
        room_name = "room1",
        parent = "room1",
        name = "table1",
    )

    table2 = world.add_random_table(
        room_name = "room1",
        parent = "room1",
        name = "table2",
    )

    object1 = world.add_random_object(
        table_name = "table1", 
        min_distance_between_objects = 0.1, 
        object_size=None, 
        max_iter = 1000)
    

    object2 = world.add_random_object(
        table_name = "table1", 
        min_distance_between_objects = 0.1, 
        object_size=None, 
        max_iter = 1000)
    
    object3 = world.add_random_object(
        table_name = "table1", 
        min_distance_between_objects = 0.1, 
        object_size=None, 
        max_iter = 1000)

    return world



if __name__ == "__main__":
    world = create_world()
    start_gui(world)
