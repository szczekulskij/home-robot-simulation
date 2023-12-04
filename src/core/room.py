from shapely import intersects_xy
from shapely.geometry import Polygon
from shapely.plotting import patch_from_polygon

class Room:
    """Representation of a room in a world."""

    def __init__(
        self,
        room_coordinates=[],
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
        if color is None:
            self.viz_color = [0.4, 0.4, 0.4]
        else: 
            self.viz_color = color

        # Entities associated with the room
        self.tables = []

        # Create the room polygon
        if isinstance(room_coordinates, list):
            self.polygon = Polygon(room_coordinates)
        else :
            raise Exception("room_coordinates must be a list of coordinates")

        self.centroid = list(self.polygon.centroid.coords)[0]
        self.update_visualization_polygon()


        def update_visualization_polygon(self):
            """Updates visualization polygon of the room walls."""
            # self.viz_polygon = self.buffered_polygon.difference(self.polygon)
            self.viz_polygon = self.polygon

            self.viz_patch = patch_from_polygon(
                self.viz_polygon,
                facecolor=self.viz_color,
                edgecolor=self.viz_color,
                linewidth=2,
                alpha=0.75,
                zorder=2,
            )