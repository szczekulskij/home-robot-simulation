import warnings
from .room import Room
import itertools

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

        # Counters
        self.num_rooms = 0
        self.num_locations = 0
        self.num_objects = 0
        self.location_instance_counts = {}
        self.object_instance_counts = {}

        # World bounds, will be set by update_bounds()
        self.x_bounds = None # list of [xmin, xmax], automatically updated by update_bounds() whenever a room is added or removed
        self.y_bounds = None # list of [ymin, ymax], automatically updated by update_bounds() whenever a room is added or removed

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
        room = Room(room_coordinates, room_color=room_color)

        # Check if the room collides with any other rooms or hallways
        # is_valid_pose = True
        # for other_loc in self.rooms + self.hallways:
        #     if room.external_collision_polygon.intersects(
        #         other_loc.external_collision_polygon
        #     ):
        #         is_valid_pose = False
        #         break
        # if not is_valid_pose:
        #     warnings.warn(f"Room {room.name} in collision. Cannot add to world.")
        #     return None

        self.rooms.append(room)
        self.name_to_entity[room.name] = room
        self.num_rooms += 1
        self.update_bounds(entity=room)

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
    

    def update_bounds(self, entity, remove=False):
        """
        Updates the X and Y bounds of the world.

        :param entity: The entity that is being added or removed
        :type entity: :class:`pyrobosim.core.room.Room`/:class:`pyrobosim.core.hallway.Hallway`
        :param remove: Specifies if the update is due to removal of an entity.
        :type remove: bool
        """
        if isinstance(entity, (Room)):
            (xmin, ymin, xmax, ymax) = entity.polygon.bounds

            if not self.x_bounds:
                # When adding the first room
                self.x_bounds = [xmin, xmax]
                self.y_bounds = [ymin, ymax]
                return

            if remove:
                sets_x_bounds = (self.x_bounds[0] == xmin) or (self.x_bounds[1] == xmax)
                sets_y_bounds = (self.y_bounds[0] == ymin) or (self.y_bounds[1] == ymin)
                is_last_room = len(self.rooms) == 0 and isinstance(entity, Room)
                # Only update if the Room/Hallway being removed affects the bounds
                if sets_x_bounds or sets_y_bounds:
                    for other_entity in itertools.chain(self.rooms, self.hallways):
                        (xmin, ymin, xmax, ymax) = other_entity.polygon.bounds
                        self.x_bounds[0] = min(self.x_bounds[0], xmin)
                        self.x_bounds[1] = max(self.x_bounds[1], xmax)
                        self.y_bounds[0] = min(self.y_bounds[0], ymin)
                        self.y_bounds[1] = max(self.y_bounds[1], ymax)
                if is_last_room:
                    # When last room has been deleted
                    self.x_bounds = None
                    self.y_bounds = None
            else:
                # Adding a Room/Hallway
                self.x_bounds[0] = min(self.x_bounds[0], xmin)
                self.x_bounds[1] = max(self.x_bounds[1], xmax)
                self.y_bounds[0] = min(self.y_bounds[0], ymin)
                self.y_bounds[1] = max(self.y_bounds[1], ymax)
        else:
            warnings.warn(
                f"Updating bounds with unsupported entity type {type(entity)}"
            )