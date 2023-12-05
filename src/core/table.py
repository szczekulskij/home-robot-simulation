""" Representations for locations and their corresponding object spawns. """

from shapely import intersects_xy
from shapely.plotting import patch_from_polygon

from ..utils.general import EntityMetadata, InvalidEntityCategoryException
from ..utils.pose import Pose, rot2d


class Table:
    def __init__(self, room_coordinates = None, parent=None, name=None, color=None):
        """
        Creates a location instance.

        :param name: Name of the location.
        :type name: str, optional
        :param category: Location category (e.g., ``"table"``).
        :type category: str
        :param pose: Pose of the location (required).
        :type pose: :class:`pyrobosim.utils.pose.Pose`
        :param parent: Parent of the location (typically a :class:`pyrobosim.core.room.Room`)
        :type parent: Entity
        :param color: Visualization color as an (R, G, B) tuple in the range (0.0, 1.0).
            If using a category with a defined color, this parameter overrides the category color.
        :type color: (float, float, float), optional
        """
        DEFAULT_VIZ_COLOR = (0, 0, 0)
    

        # Validate input
        if parent is None:
            raise Exception("Location parent must be specified.")
        if room_coordinates is None:
            raise Exception("Room coordinates pose must be specified.")

        # Extract the model information from the model list
        self.name = name
        self.parent = parent
        self.room_coordinates = room_coordinates


        if color is not None: self.viz_color = color
        else: self.viz_color = DEFAULT_VIZ_COLOR

        self.create_polygons()
        self.create_spawn_locations()

    def get_room_name(self):
        """
        Returns the name of the room containing the location.

        :return: Room name.
        :rtype: str
        """
        if self.parent is None:
            return None
        else:
            return self.parent.name

    def is_inside(self, pose):
        """
        Checks if a pose is inside the location polygon.

        :param pose: Pose to check.
        :type pose: :class:`pyrobosim.utils.pose.Pose`/(float, float)
        :return: True if pose is inside the polygon, else False.
        :rtype: bool
        """
        if isinstance(pose, Pose):
            x, y = pose.x, pose.y
        else:
            x, y = pose[0], pose[1]
        return intersects_xy(self.polygon, x, y)

    def create_polygons(self, inflation_radius=0.0):
        """
        Creates collision and visualization polygons for the location.

        :param inflation_radius: Inflation radius, in meters.
        :type inflation_radius: float, optional
        """
        self.raw_polygon, self.height = polygon_and_height_from_footprint(
            self.metadata["footprint"],
            parent_polygon=self.parent.polygon if self.parent is not None else None,
        )
        self.polygon = transform_polygon(self.raw_polygon, self.pose)
        self.update_collision_polygon(inflation_radius=inflation_radius)
        self.update_visualization_polygon()


    def update_visualization_polygon(self):
        """Updates the visualization polygon for the location."""
        self.viz_patch = patch_from_polygon(
            self.polygon,
            facecolor=None,
            edgecolor=self.viz_color,
            linewidth=2,
            fill=None,
            alpha=0.75,
            zorder=2,
        )

    def create_spawn_locations(self):
        """Creates the object spawn locations at this location."""
        self.children = []
        if "locations" in self.metadata:
            for loc_data in self.metadata["locations"]:
                if "name" in loc_data:
                    name = f"{self.name}_{loc_data['name']}"
                else:
                    name = f"{self.name}_loc{len(self.children)}"
                os = ObjectSpawn(name, loc_data, self)
                self.children.append(os)


    def __repr__(self):
        """Returns printable string."""
        return f"Location: {self.name}"

    def print_details(self):
        """Prints string with details."""
        print(f"Location: {self.name} in {self.parent}\n\t{self.pose}")


class ObjectSpawn:
    """Representation of an object spawn in the world."""

    def __init__(self, name, metadata, parent=None):
        """
        Creates an object spawn instance.

        :param name: Name of the location.
        :type name: str, optional
        :param metadata: Metadata dictionary for the object spawn
        :type metadata: dict
        :param parent: Parent of the location (typically a :class:`pyrobosim.core.locations.Location`)
        :type parent: Entity
        """
        self.name = name
        self.category = parent.category
        self.parent = parent
        self.children = []
        self.graph_nodes = []

        self.metadata = metadata
        if "color" in self.metadata:
            self.viz_color = self.metadata["color"]
        else:
            self.viz_color = self.parent.viz_color

        self.set_pose_from_parent()

    def set_pose_from_parent(self):
        """Updates the object spawn's pose from its parent's pose."""
        # Get the footprint and height data
        if "footprint" not in self.metadata:
            self.metadata["footprint"] = {"type": "parent"}
        self.polygon, self.height = polygon_and_height_from_footprint(
            self.metadata["footprint"],
            pose=self.parent.pose,
            parent_polygon=self.parent.polygon if self.parent is not None else None,
        )
        if self.height is None:
            self.height = self.parent.height

        self.update_visualization_polygon()
        self.centroid = list(self.polygon.centroid.coords)[0]
        self.pose = Pose(
            x=self.centroid[0], y=self.centroid[1], z=0.0, q=self.parent.pose.q
        )

        # If navigation poses were specified, add them. Else, use the parent poses.
        # Of course, only add these if they are collision-free.
        if "nav_poses" in self.metadata:
            self.nav_poses = []
            if "offset" in self.metadata["footprint"]:
                p_off = self.metadata["footprint"]["offset"]
            else:
                p_off = (0, 0)
            for p in self.metadata["nav_poses"]:
                rot_p = rot2d(
                    (p[0] + p_off[0], p[1] + p_off[1]), self.parent.pose.get_yaw()
                )
                yaw = p[2] + self.parent.pose.get_yaw()
                nav_pose = Pose(
                    x=rot_p[0] + self.parent.pose.x,
                    y=rot_p[1] + self.parent.pose.y,
                    z=self.parent.pose.z,
                    yaw=yaw,
                )
                if self.parent.parent.is_collision_free(nav_pose):
                    self.nav_poses.append(nav_pose)
        else:
            self.nav_poses = self.parent.nav_poses

    def get_room_name(self):
        """
        Returns the name of the room containing the object spawn.

        :return: Room name.
        :rtype: str
        """
        return self.parent.get_room_name()

    def is_inside(self, pose):
        """
        Checks if a pose is inside the object spawn polygon.

        :param pose: Pose to check.
        :type pose: :class:`pyrobosim.utils.pose.Pose`/(float, float)
        :return: True if pose is inside the polygon, else False.
        :rtype: bool
        """
        if isinstance(pose, Pose):
            x, y = pose.x, pose.y
        else:
            x, y = pose[0], pose[1]
        return intersects_xy(self.polygon, x, y)

    def update_visualization_polygon(self):
        """Updates the visualization polygon for the object spawn."""
        self.viz_patch = patch_from_polygon(
            self.polygon,
            facecolor=None,
            edgecolor=self.parent.viz_color,
            linewidth=1,
            fill=None,
            ls="--",
            zorder=2,
        )

    def add_graph_nodes(self):
        """Creates graph nodes for searching."""
        self.graph_nodes = [Node(p, parent=self) for p in self.nav_poses]

    def __repr__(self):
        """Returns printable string."""
        return f"Object spawn: {self.name}"

    def print_details(self):
        """Prints string with details."""
        print(f"Object spawn: {self.name} in {self.parent.name}\n\t{self.pose}")
