""" Representations for objects that exist in the world. """

import numpy as np
from shapely.plotting import patch_from_polygon
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point
import random



class Object:
    """Represents an object in the world."""
    def __init__(
        self, 
        centroid = None, 
        radius = None,
        parent=None, 
        name=None, 
        color=None,
        nr=None,
        nr_of_other_objects=None,):
        """
        Creates an object instance.

        :param name: Name of the object.
        :type name: str, optional
        :param parent: Parent of the object (typically a :class:`pyrobosim.core.locations.ObjectSpawn`)
        :type parent: Entity
        :param color: Visualization color as an (R, G, B) tuple in the range (0.0, 1.0).
            If using a category with a defined color, this parameter overrides the category color.
        :type color: (float, float, float), optional
        """
        DEFAULT_VIZ_COLOR = (1, 1, 1)
        
        # Validate input
        if centroid is None:
            raise Exception("Room coordinates pose must be specified.")
        if radius is None:
            raise Exception("Object size must be specified.")

        # double check centroid is a 2D coordinate
        assert len(centroid) == 2

        self.name = name
        self.parent = parent
        self.radius = radius
        if nr is None:
            if nr_of_other_objects is None:
                raise Exception("Object nr must be specified.")
            nr = nr_of_other_objects + 1
        elif nr is not None :
            print("nr:", nr)
            if nr_of_other_objects is not None:
                raise Exception("Object nr and nr_of_other_objects cannot both be specified. It encourages errors.")
            self.nr = nr

        if len(centroid) == 2 and isinstance(centroid, (list,tuple)):
            self.polygon = Point(centroid).buffer(radius)
        else :
            raise Exception("object_coordinates must be a list of coordinates")


        if color != None: 
            self.color = color
        else: 
            self.color = self.get_random_color()

        self.viz_color = color


        self.viz_text = nr
        self.centroid = centroid
        self.update_visualization_polygon()

    def get_room_name(self):
        """
        Returns the name of the room containing the object.

        :return: Room name.
        :rtype: str
        """
        return self.parent.get_room_name()


    def update_visualization_polygon(self):
        """Updates the visualization polygon for the object."""
        self.viz_patch = patch_from_polygon(
            self.polygon,
            facecolor=self.viz_color,
            edgecolor=self.viz_color,
            linewidth=2,
            alpha=0.75,
            zorder=3,
        )

    def __repr__(self):
        """Returns printable string."""
        return f"Object: {self.name}"

    def print_details(self):
        """Prints string with details."""
        print(f"Object: {self.name} in {self.parent.name}\n\t{self.pose}")

    def get_random_color(self):
        return [random.random(), random.random(), random.random()]