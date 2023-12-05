import warnings
from .room import Room
from .table import Table
from .objects import Object
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
        self.tables = []
        self.objects = []

        # Counters
        self.num_rooms = 0
        self.num_tables = 0
        self.num_objects = 0
        # self.location_instance_counts = {}
        self.object_instance_counts = {}

        # World bounds, will be set by update_bounds()
        self.x_bounds = None # list of [xmin, xmax], automatically updated by update_bounds() whenever a room is added or removed
        self.y_bounds = None # list of [ymin, ymax], automatically updated by update_bounds() whenever a room is added or removed

    def add_room(self, room_coordinates, room_name = None, room_color=None):
        r"""
        Adds a room to the world.
        :param room_coordinates: List of (x, y) coordinates describing the room footprint.
        :param room_color: Color of the room, as an (R, G, B) tuple ????in the range (0.0, 1.0).???
        :return: room object if successfully created, else None.
        :rtype: :class:`pyrobosim.core.room.room`
        """

        # If it's a room object, get it from the "room" named argument.
        # Else, create a room directly from the specified arguments.
        room = Room(room_coordinates, name = room_name, color=room_color)

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

        # Remove locations in the room
        while len(room.tables) > 0:
            self.remove_location(room.tables[-1])

        # Remove the room itself
        self.rooms.remove(room)
        self.name_to_entity.pop(room_name)
        self.num_rooms -= 1
        self.update_bounds(entity=room, remove=True)
        return True
    


    def add_table(self, table_coordinates = None, parent=None, name=None, color=None):
        r"""
        Adds a table at the specified parent entity, (eg. in a room)
        :param room_coordinates: List of (x, y) coordinates describing the room footprint.
        :param parent: Parent of the location (a :class:`pyrobosim.core.room.Room`)
        :param name: Name of the location.
        :param color: Color of the location, as an (R, G, B) tuple in the range (0.0, 1.0).

        :return: Location object if successfully created, else None.
        :rtype: :class:`pyrobosim.core.room.Room`
        """
        # If it's a location object, get it from the "location" named argument.
        # Else, create a location directly from the specified arguments.
        if parent is None : 
            warnings.warn("Location instance or parent must be specified.")
            return None
        if table_coordinates is None:
            warnings.warn("Location pose must be specified.")
            return None
        else: 
            table = Table(name=name, coordinates = table_coordinates, parent=parent, color=color,)




        # Check that the location fits within the room and is not in collision with
        # other locations already in the room. Else, warn and do not add it.
        # is_valid_pose = table.polygon.within(table.parent.polygon)
        # if is_valid_pose:
        #     for other_tables in table.parent.locations:
        #         if table.polygon.intersects(other_tables.polygon):
        #             is_valid_pose = False
        #             break
        # if not is_valid_pose:
        #     warnings.warn(f"Location {table.name} in collision. Cannot add to world.")
        #     return None

        # Do all the necessary bookkeeping
        # table.parent.tables.append(table)
        self.tables.append(table)
        # self.location_instance_counts[table.category] += 1
        self.num_tables += 1
        self.name_to_entity[table.name] = table
        # for spawn in table.children:
        #     self.name_to_entity[spawn.name] = spawn

        return table
    
    # def remove_table(self, table_name):
    #     """
    #     Cleanly removes a location from the world.

    #     :param loc: Location instance of name to remove.
    #     :type loc: :class:`pyrobosim.core.locations.Location`/str
    #     :return: True if the location was successfully removed, else False.
    #     :rtype: bool
    #     """
    #     # Parse inputs
    #     if isinstance(table_name, str):
    #         table = self.get_location_by_name(table_name)

    #     if table in self.locations:
    #         # remove objects at the location before removing the location
    #         for spawn in table_name.children:
    #             while len(spawn.children) > 0:
    #                 self.remove_object(spawn.children[-1])
    #         # Remove location
    #         self.locations.remove(table_name)
    #         self.num_locations -= 1
    #         self.location_instance_counts[table_name.category] -= 1
    #         room = table_name.parent
    #         room.locations.remove(table_name)
    #         room.update_collision_polygons(self.inflation_radius)
    #         self.name_to_entity.pop(table_name.name)
    #         for spawn in table_name.children:
    #             self.name_to_entity.pop(spawn.name)
    #         return True
    #     return False

    def add_object(self, centroid, size, parent, name=None, color=None):
        r"""
        Adds an object to a specific location.

        :param centroid: (x, y) coordinates of the centroid of the object.
        :param size: Size of the object.
        :param parent: Parent of the object (typically a :class:`pyrobosim.core.table.Table`)
        :param name: Name of the object.
        :param color: Color of the object, as an (R, G, B) tuple in the range (0.0, 1.0).

        :return: Object instance if successfully created, else None.
        :rtype: :class:`pyrobosim.core.objects.Object`
        """
        # If it's an Object instance, get it from the "object" named argument.
        # Else, create an object directly from the specified arguments.
       
        obj = Object(centroid=centroid, size=size, parent=parent, name=name, color=color)

        # Do the necessary bookkeeping
        self.objects.append(obj)
        self.name_to_entity[obj.name] = obj
        self.num_objects += 1
        return obj

    # def update_object(self, obj, loc=None, pose=None):
    #     """
    #     Updates an existing object in the world.

    #     :param obj: Object instance or name to update.
    #     :type obj: :class:`pyrobosim.core.objects.Object`/str
    #     :param loc: Location or object spawn instance or name. If none, uses the previous location.
    #     :type loc: :class:`pyrobosim.core.locations.Location`/:class:`pyrobosim.core.locations.ObjectSpawn`/str, optional
    #     :param pose: Pose of the location. If none is specified, it will be sampled.
    #     :type pose: :class:`pyrobosim.utils.pose.Pose`, optional
    #     :return: True if the update was successful, else False.
    #     :rtype: bool
    #     """
    #     if isinstance(obj, str):
    #         obj = self.get_object_by_name(obj)
    #     if not isinstance(obj, Object):
    #         warnings.warn("Could not find object. Not updating.")
    #         return False

    #     if loc is not None:
    #         if pose is None:
    #             warnings.warn("Cannot specify a location without a pose.")

    #         # If it's a string, get the location name
    #         if isinstance(loc, str):
    #             loc = self.get_entity_by_name(loc)
    #         # If it's a location object, pick an object spawn at random.
    #         # Otherwise, if it's an object spawn, use that entity as is.
    #         if isinstance(loc, Location):
    #             obj_spawn = np.random.choice(loc.children)
    #         elif isinstance(loc, ObjectSpawn):
    #             obj_spawn = loc
    #         else:
    #             warnings.warn(
    #                 f"Location {loc} did not resolve to a valid location for an object."
    #             )
    #             return False

    #         obj.parent.children.remove(obj)
    #         obj.parent = obj_spawn
    #         obj_spawn.children.append(obj)

    #     if pose is not None:
    #         obj.set_pose(pose)
    #         obj.create_polygons()

    #     return True

    # def remove_object(self, obj):
    #     """
    #     Cleanly removes an object from the world.

    #     :param loc: Object instance of name to remove.
    #     :type loc: :class:`pyrobosim.core.objects.Object`/str
    #     :return: True if the object was successfully removed, else False.
    #     :rtype: bool
    #     """
    #     if isinstance(obj, str):
    #         obj = self.get_object_by_name(obj)
    #     if obj in self.objects:
    #         self.objects.remove(obj)
    #         self.name_to_entity.pop(obj.name)
    #         self.num_objects -= 1
    #         obj.parent.children.remove(obj)
    #         return True
    #     return False

    # def remove_all_objects(self, restart_numbering=True):
    #     """
    #     Cleanly removes all objects from the world.

    #     :param restart_numbering: If True, restarts numbering of all
    #         categories to zero, defaults to True.
    #     :type restart_numbering: bool, optional
    #     """
    #     for obj in reversed(self.objects):
    #         self.remove_object(obj)
    #     self.num_objects = 0
    #     if restart_numbering:
    #         self.object_instance_counts = {}



    def update_bounds(self, entity, remove=False):
        """
        Updates the X and Y bounds of the world.
        You can think about this function as something that gets called whenever we add a new room in the world and we might need to update the bounds of the world.

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