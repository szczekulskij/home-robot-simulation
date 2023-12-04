from warnings import warn
class World:
    """Core world modeling class."""

    def __init__(
        self, name="world"
    ):
        """
        Creates a new world model instance.

        :param name: Name of world model.
        :type name: str
        :param inflation_radius: Inflation radius around entities (locations, walls, etc.), in meters.
        :type inflation_radius: float, optional
        :param object_radius: Buffer radius around objects for collision checking, in meters.
        :type object_radius: float, optional
        :param wall_height: Height of walls, in meters, for 3D model generation.
        :type wall_height: float, optional
        """
        self.name = name

        # Connected apps
        self.has_gui = False
        self.gui = None

        # Robots
        self.robots = []

        # World entities (rooms, locations, objects, etc.)
        self.name_to_entity = {}
        self.rooms = []
        self.locations = []
        self.objects = []
        self.set_metadata()

        # Counters
        self.num_rooms = 0
        self.num_locations = 0
        self.num_objects = 0
        self.location_instance_counts = {}
        self.object_instance_counts = {}

        # World bounds, will be set by update_bounds()
        self.x_bounds = None
        self.y_bounds = None

    def add_room(self, room_coordinates, room_color=None):
        r"""
        Adds a room to the world.
        :param room_coordinates: List of (x, y) coordinates describing the room footprint.
        :param room_color: Color of the room, as an (R, G, B) tuple ????in the range (0.0, 1.0).???
        :return: room object if successfully created, else None.
        :rtype: :class:`pyrobosim.core.room.room`
        """

        # If it's a room object, get it from the "room" named argument.
        # Else, create a room directly from the specified arguments.
        room = room(room_coordinates, room_color=room_color)

        # Check if the room collides with any other rooms or hallways
        is_valid_pose = True
        for other_loc in self.rooms + self.hallways:
            if room.external_collision_polygon.intersects(
                other_loc.external_collision_polygon
            ):
                is_valid_pose = False
                break
        if not is_valid_pose:
            warnings.warn(f"Room {room.name} in collision. Cannot add to world.")
            return None

        self.rooms.append(room)
        self.name_to_entity[room.name] = room
        self.num_rooms += 1
        self.update_bounds(entity=room)

        # Update the room collision polygon based on the world inflation radius
        room.update_collision_polygons(self.inflation_radius)

        room.add_graph_nodes()
        return room

    def remove_room(self, room_name):
        """
        Removes a room from the world by name.

        :param room_name: Name of room to remove.
        :type room_name: str
        :return: True if the room was successfully removed, else False.
        :rtype: bool
        """
        room = self.get_room_by_name(room_name)
        if room is None:
            warnings.warn(f"No room {room_name} found for removal.")
            return False

        # Remove hallways associated with the room
        while len(room.hallways) > 0:
            self.remove_hallway(room.hallways[-1])

        # Remove locations in the room
        while len(room.locations) > 0:
            self.remove_location(room.locations[-1])

        # Remove the room itself
        self.rooms.remove(room)
        self.name_to_entity.pop(room_name)
        self.num_rooms -= 1
        self.update_bounds(entity=room, remove=True)

        return True