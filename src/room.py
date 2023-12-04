from shapely import intersects_xy
from shapely.geometry import Polygon
from shapely.plotting import patch_from_polygon

class Room:
    """Representation of a room in a world."""

    def __init__(
        self,
        name=None,
        footprint=[],
        color=[0.4, 0.4, 0.4],
    ):
        """
        Creates a Room instance.

        :param name: Room name.
        :type name: str, optional
        :param footprint: Point list or Shapely polygon describing the room 2D footprint (required).
        :type footprint: :class:`shapely.geometry.Polygon`/list[:class:`pyrobosim.utils.pose.Pose`]
        :param color: Visualization color as an (R, G, B) tuple in the range (0.0, 1.0)
        :type color: (float, float, float), optional
        """
        self.name = name
        self.viz_color = color

        # Entities associated with the room
        self.hallways = []
        self.locations = []
        self.graph_nodes = []

        # Create the room polygon
        self.height = height
        if isinstance(footprint, list):
            self.polygon = Polygon(footprint)
        else:
            self.polygon, _ = polygon_and_height_from_footprint(footprint)
        if self.polygon.is_empty:
            raise Exception("Room footprint cannot be empty.")

        self.centroid = list(self.polygon.centroid.coords)[0]
        self.update_collision_polygons()
        self.update_visualization_polygon()

        # Create a navigation pose list -- if none specified, use the room centroid
        if nav_poses is not None:
            self.nav_poses = nav_poses
        else:
            self.nav_poses = [Pose.from_list(self.centroid)]