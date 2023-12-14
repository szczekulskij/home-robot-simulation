import math
import random
import warnings

from .polygon_utils import box_to_coords, check_if_polygons_overlap, inflate_polygon, sample_from_polygon
from shapely.geometry import Polygon
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
        room = Room(room_coordinates, name = room_name, color=room_color)
        self.rooms.append(room)
        self.name_to_entity[room.name] = room
        self.num_rooms += 1
        self.update_bounds(entity=room)
        return room


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
        if parent is None : 
            warnings.warn("Location instance or parent must be specified.")
            return None
        if table_coordinates is None:
            warnings.warn("Location pose must be specified.")
            return None
        else: 
            table = Table(name=name, coordinates = table_coordinates, parent=parent, color=color,)

        self.tables.append(table)
        self.num_tables += 1
        self.name_to_entity[table.name] = table
        return table
    

    def add_random_table(
            self,
            room_name,
            parent = None,
            name = None,
            color = None,
            min_distance_between_tables = 0.5, 
            table_size=None, 
            rotation_angle=None, 
            max_iter = 50000):
        
        table_coords = self.generate_random_table_coords(
            room_name,
            min_distance_between_tables = min_distance_between_tables, 
            table_size = table_size, 
            rotation_angle = rotation_angle, 
            max_iter = max_iter
            )
        
        return self.add_table(table_coordinates = table_coords, parent=parent, name=name, color=color)

    def generate_random_table_coords(
            self, 
            room_name,
            min_distance_between_tables = 0.5, 
            table_size=None, 
            rotation_angle=None, 
            max_iter = 50000
            ):
        # 1. Handle input
    match room_name:
    case None:
        raise ValueError('room_name must be specified')
    
    match table_size:
        case None:
            table_size = (random.randint(4, 10), random.randint(2, 5))
        case 'small':
            table_size = (1, 2)
        case 'medium':
            table_size = (1, 3)
        case 'large':
            table_size = (2, 4)
        case isinstance(table_size, (tuple, list)) and len(table_size) == 2:
            pass
        case _:
            raise ValueError('table_size must be "small", "medium", "large" or a tuple of two numbers')

        if rotation_angle == None: rotation_angle = random.randint(0,360)
        elif isinstance(rotation_angle, (float, int)): pass
        else : raise ValueError('rotation_angle must be an integer')
        rotation_angle = math.radians(rotation_angle) # transfer to radians

        room_polygon = self.get_room_by_name(room_name).polygon
        other_tables_polygons = [i.polygon for i in self.tables]
        
        # 2. Iterate until a valid table is found
        i = 0
        while True and i < max_iter:
            i += 1
            table_coords = sample_random_table_coords(room_polygon, table_size, rotation_angle)
            if check_if_table_is_valid(room_polygon, table_coords, other_tables_polygons, min_distance_between_tables): 
                return table_coords


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

    def get_room_by_name(self, name):
        """
        Gets a room object by its name.

        :param name: Name of room.
        :type name: str
        :return: Room instance matching the input name, or ``None`` if not valid.
        :rtype: :class:`pyrobosim.core.room.Room`
        """
        if name not in self.name_to_entity:
            warnings.warn(f"Room not found: {name}")
            return None

        entity = self.name_to_entity[name]
        if not isinstance(entity, Room):
            warnings.warn(f"Entity {name} found but it is not a Room.")
            return None

        return entity
    


######################## HELPER FUNCTIONS ##############################
def sample_random_table_coords(room_polygon, table_size = None, rotation_angle = None):
    # 1. Generate random origin point
    origin_coords = sample_from_polygon(room_polygon)
    # 2. generate random coordinates for the table
    table_coords = box_to_coords(table_size, origin_coords, rotation_angle)
    return table_coords


def check_if_table_is_valid(room_polygon, table_coords, other_tables_polygons, min_distance_between_tables):
    # check if the table is inside the room
    if not room_polygon.contains(Polygon(table_coords)): return False
    # check if table is not overlapping (or too close) to other tables
    for other_table_poly in other_tables_polygons:
        if check_if_polygons_overlap(Polygon(table_coords), other_table_poly): return False # this line probs unnecessary
        if check_if_polygons_overlap(inflate_polygon(Polygon(table_coords), min_distance_between_tables), other_table_poly): return False
    return True
