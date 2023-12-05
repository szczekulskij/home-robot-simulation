""" Representations for objects that exist in the world. """

import numpy as np
from shapely.plotting import patch_from_polygon
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point



class Object:
    """Represents an object in the world."""
    def __init__(
        self, 
        centroid = None, 
        size = None,
        parent=None, 
        name=None, 
        color=None):
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
        DEFAULT_VIZ_COLOR = (0, 0, 1)
        
        # Validate input
        if parent is None:
            raise Exception("Location parent must be specified.")
        if centroid is None:
            raise Exception("Room coordinates pose must be specified.")
        if size is None:
            raise Exception("Object size must be specified.")

        # double check centroid is a 2D coordinate
        assert len(centroid) == 2

        self.name = name
        self.parent = parent

        if len(centroid) == 2 and isinstance(centroid, (list,tuple)):
            self.polygon = Point(centroid).buffer(size)
        else :
            raise Exception("room_coordinates must be a list of coordinates")


        if color is not None: self.viz_color = color
        else: self.viz_color = DEFAULT_VIZ_COLOR


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
            facecolor=None,
            edgecolor=self.viz_color,
            linewidth=2,
            fill=None,
            alpha=0.75,
            zorder=3,
        )

    def __repr__(self):
        """Returns printable string."""
        return f"Object: {self.name}"

    def print_details(self):
        """Prints string with details."""
        print(f"Object: {self.name} in {self.parent.name}\n\t{self.pose}")
