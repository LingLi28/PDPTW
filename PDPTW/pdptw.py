import numpy as np
from request import Request
from location import Location

class PDPTW:
    """
    Class that represents a pick-up and delivery problem with time windows
    Attributes
    ----------
    name : string
        name of the instance.
    requests : List of Requests
        The set containing all requests.
    depot : Location
        the depot where all vehicles must start and end.
    locations : Set of Locations
        The set containing all locations
     distMatrix : 2D array
         matrix with all distances between cities
    capacity : int
        capacity of the vehicles
    
    """

    def __init__(self, name, requests, depot, vehicleCapacity):
        self.name = name
        self.requests = requests
        self.depot = depot
        self.capacity = vehicleCapacity
        ##construct the set with all locations
        self.locations = set()
        self.locations.add(depot)
        for r in self.requests:
            self.locations.add(r.pickUpLoc)
            self.locations.add(r.deliveryLoc)

        # compute the distance matrix
        self.distMatrix = np.zeros((len(self.locations), len(self.locations)))  # init as nxn matrix
        for i in self.locations:
            for j in self.locations:
                distItoJ = Location.getDistance(i, j)
                self.distMatrix[i.nodeID, j.nodeID] = distItoJ

    def print(self):
        print(" PDPTW problem " + self.name + " with " + str(
            len(self.requests)) + " requests and a vehicle capacity of " + str(self.capacity))
        # print(self.distMatrix)
        # for i in self.requests:
        #     print(i)

    def readInstance(fileName):
        """
        Method that reads an instance from a file and returns the instancesf
        """
        servStartTime = 0
        f = open(fileName)
        requests = list()
        stations = list()
        unmatchedPickups = dict()
        unmatchedDeliveries = dict()
        nodeCount = 0
        requestCount = 1  # start with 1
        for line in f.readlines()[1:-6]:
            asList = []
            n = 13
            for index in range(0, len(line), n):
                asList.append(line[index: index + n].strip())

            lID = asList[0]
            x = int(asList[2][:-2])  # need to remove ".0" from the string
            y = int(asList[3][:-2])
            if lID.startswith("D"):
                # it is the depot
                depot = Location(0, x, y, 0, 0, 0, 0, servStartTime, 0, nodeCount)  # depot requestID=0
                nodeCount += 1

            elif lID.startswith("C"):
                # it is a location
                lType = asList[1]
                demand = int(asList[4][:-2])
                startTW = int(asList[5][:-2])
                endTW = int(asList[6][:-2])
                servTime = int(asList[7][:-2])
                partnerID = asList[8]
                if lType == "cp":
                    # it is a pick-up
                    if partnerID in unmatchedDeliveries:
                        deliv = unmatchedDeliveries.pop(partnerID)
                        pickup = Location(deliv.requestID, x, y, demand, startTW, endTW, servTime, servStartTime, 1, nodeCount)
                        nodeCount += 1
                        req = Request(pickup, deliv, deliv.requestID)
                        requests.append(req)
                    else:
                        pickup = Location(requestCount, x, y, demand, startTW, endTW, servTime, servStartTime, 1, nodeCount)
                        nodeCount += 1
                        requestCount += 1
                        # lID -> partnerID
                        unmatchedPickups[lID] = pickup
                elif lType == "cd":
                    # it is a delivery
                    if partnerID in unmatchedPickups:
                        pickup = unmatchedPickups.pop(partnerID)
                        deliv = Location(pickup.requestID, x, y, demand, startTW, endTW, servTime, servStartTime, -1, nodeCount)
                        nodeCount += 1
                        req = Request(pickup, deliv, pickup.requestID)
                        requests.append(req)
                    else:
                        deliv = Location(requestCount, x, y, demand, startTW, endTW, servTime, servStartTime, -1, nodeCount)
                        nodeCount += 1
                        requestCount += 1
                        unmatchedDeliveries[lID] = deliv

        # sanity check: all pickups and deliveries should be matched
        if len(unmatchedDeliveries) + len(unmatchedPickups) > 0:
            raise Exception("Not all matched")
        # f.close()

        # read the vehicle capacity 
        f = open(fileName)
        capLine = f.readlines()[-4]
        capacity = int(capLine[-7:-3].strip())

        return PDPTW(fileName, requests, depot, capacity)
