import math 
import random
import warnings

from .polygonUtils import boxToCoords, checkIfPolygonsOverlap, inflatePolygon, sampleFromPolygon  
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
        self.name = name

        # Connected apps 
        self.hasGui = False
        self.gui = None

        # Robots
        self.robots = []

        # World entities (rooms, locations, objects, etc.)
        self.nameToEntity = {}
        self.rooms = []
        self.tables = []
        self.objects = []

        # Counters 
        self.numRooms = 0
        self.numTables = 0
        self.numObjects = 0
       
        self.objectInstanceCounts = {}

        # World bounds, will be set by updateBounds()
        self.xBounds = None 
        self.yBounds = None 


    def addRoom(self, roomCoordinates, roomName = None, roomColor=None):
        
        room = Room(roomCoordinates, name = roomName, color=roomColor)
        self.rooms.append(room)
        self.nameToEntity[room.name] = room
        self.numRooms += 1
        self.updateBounds(entity=room)
        return room

    def addTable(self, tableCoordinates = None, parent=None, name=None, color=None):
       
        if parent is None:  
            warnings.warn("Location instance or parent must be specified.")
            return None
        if tableCoordinates is None:
            warnings.warn("Location pose must be specified.")
            return None
        else: 
            table = Table(name=name, coordinates = tableCoordinates, parent=parent, color=color)

        self.tables.append(table)
        self.numTables += 1
        self.nameToEntity[table.name] = table
        return table
    
    def addRandomTable(
            self,
            roomName,
            parent = None,
            name = None, 
            color = None,
            minDistanceBetweenTables = 0.5,
            tableSize=None,  
            rotationAngle=None,  
            maxIter = 50000):
        
        tableCoords = self.generateRandomTableCoords(
            roomName, 
            minDistanceBetweenTables,  
            tableSize,     
            rotationAngle,   
            maxIter       
            )
        
        return self.addTable(tableCoordinates = tableCoords, parent=parent, name=name, color=color)

    def generateRandomTableCoords(
            self,
            roomName,
            minDistanceBetweenTables = 0.5, 
            tableSize=None,  
            rotationAngle=None, 
            maxIter = 50000
            ):
       
        if roomName is None: raise ValueError('roomName must be specified')
       
        if tableSize == None: tableSize = (random.randint(4,10), random.randint(2,5))
        elif tableSize == 'small': tableSize = (1,2) 
        elif tableSize == 'medium': tableSize = (1,3)
        elif tableSize == 'large': tableSize = (2,4)
        elif isinstance (tableSize, (tuple, list)) and len(tableSize) == 2: pass
        else: raise ValueError('tableSize must be "small", "medium", "large" or a tuple of two numbers')

        if rotationAngle == None: rotationAngle = random.randint(0,360) 
        elif isinstance(rotationAngle, (float, int)): pass
        else: raise ValueError('rotationAngle must be an integer')
        rotationAngle = math.radians(rotationAngle)

        roomPolygon = self.getRoomByName(roomName).polygon        
        otherTablesPolygons = [i.polygon for i in self.tables]
       
        i = 0
        while True and i < maxIter:
            i += 1
            tableCoords = sampleRandomTableCoords(roomPolygon, tableSize, rotationAngle)
            if checkIfTableIsValid(roomPolygon, tableCoords, otherTablesPolygons, minDistanceBetweenTables):
                return tableCoords

    def addObject(self, centroid, size, parent, name=None, color=None):
       
        obj = Object(centroid=centroid, size=size, parent=parent, name=name, color=color)

        self.objects.append(obj)
        self.nameToEntity[obj.name] = obj
        self.numObjects += 1
        return obj


    def updateBounds(self, entity, remove=False):
       
        if isinstance(entity, Room):
            (xmin, ymin, xmax, ymax) = entity.polygon.bounds

            if not self.xBounds:
              
                self.xBounds = [xmin, xmax]
                self.yBounds = [ymin, ymax]
                return

            if remove:
              
                setsXBounds = (self.xBounds[0] == xmin) or (self.xBounds[1] == xmax)
                setsYBounds = (self.yBounds[0] == ymin) or (self.yBounds[1] == ymin)
                isLastRoom = len(self.rooms) == 0 and isinstance(entity, Room)
               
                if setsXBounds or setsYBounds:
                    for otherEntity in itertools.chain(self.rooms):
                       
                        self.xBounds[0] = min(self.xBounds[0], xmin)
                        self.xBounds[1] = max(self.xBounds[1], xmax)
                        self.yBounds[0] = min(self.yBounds[0], ymin)
                        self.yBounds[1] = max(self.yBounds[1], ymax)
                if isLastRoom:
                   
                    self.xBounds = None
                    self.yBounds = None
            else:

                self.xBounds[0] = min(self.xBounds[0], xmin)
                self.xBounds[1] = max(self.xBounds[1], xmax)
                self.yBounds[0] = min(self.yBounds[0], ymin)
                self.yBounds[1] = max(self.yBounds[1], ymax)
        else:
            warnings.warn(
                f"Updating bounds with unsupported entity type {type(entity)}"
            )

    def getRoomByName(self, name):
       
        if name not in self.nameToEntity:
            warnings.warn(f"Room not found: {name}")
            return None

        entity = self.nameToEntity[name]
        if not isinstance(entity, Room):
            warnings.warn(f"Entity {name} found but it is not a Room.")
            return None

        return entity
    
######################## HELPER FUNCTIONS ##############################

def sampleRandomTableCoords(roomPolygon, tableSize = None, rotationAngle = None):
    
    originCoords = sampleFromPolygon(roomPolygon)
    
    tableCoords = boxToCoords(tableSize, originCoords, rotationAngle)
    return tableCoords

def checkIfTableIsValid(roomPolygon, tableCoords, otherTablesPolygons, minDistanceBetweenTables):

    if not roomPolygon.contains(Polygon(tableCoords)): return False
    
    for otherTablePoly in otherTablesPolygons:
        if checkIfPolygonsOverlap(Polygon(tableCoords), otherTablePoly): return False
       
        if checkIfPolygonsOverlap(inflatePolygon(Polygon(tableCoords), minDistanceBetweenTables), otherTablePoly): return False
    
    return True
