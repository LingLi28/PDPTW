import sys

class Route:
    """
    Class used to represent a route
    
    Parameters
    ----------
    locations : list of locations
        the route sequence of locations.
    requests : set of requests
        the requests served by the route
    problem : PDPTW
        the problem instance, used to compute distances.
    feasible : boolean
        true if route respects time windows, capacity and precedence # delivery after pickup
    distance : int
        total distance driven, extremely large number if infeasible
    """

    def __init__(self, locations, requests, problem):
        self.locations = locations
        self.requests = requests
        self.problem = problem
        # check the feasibility and compute the distance
        self.feasible = self.isFeasible()
        if self.feasible:
            self.distance = self.computeDistance()
        else:
            self.distance = sys.maxsize  # extremely large number

    def calculateServiceStartTime(self):
        curTime = 0
        for i in range(1, len(self.locations) - 1):
            prevNode = self.locations[i - 1]
            curNode = self.locations[i]
            dist = self.problem.distMatrix[prevNode.nodeID][curNode.nodeID]
            curTime = max(curNode.startTW, curTime + prevNode.servTime + dist)
            self.locations[i].servStartTime = curTime

    def computeDistance(self):
        """
        Method that computes and returns the distance of the route
        """
        totDist = 0

        # for i in range(1, len(self.locations) - 1):
        for i in range(1, len(self.locations)):
            prevNode = self.locations[i - 1]
            curNode = self.locations[i]
            dist = self.problem.distMatrix[prevNode.nodeID][curNode.nodeID]
            totDist += dist
        return totDist

    def computeDiff(self, preNode, afterNode, insertNode):
        '''
        Method that calculates the cost of inserting a new node
        Parameters
        ----------
        preNode: Location
        afterNode: Location
        insertNode: Location
        '''

        return self.problem.distMatrix[preNode.nodeID][insertNode.nodeID] + self.problem.distMatrix[afterNode.nodeID][
            insertNode.nodeID] - self.problem.distMatrix[preNode.nodeID][afterNode.nodeID]

    # add this method
    def compute_cost_add_one_request(self, preNode_index, afterNode_index, request):
        locationsCopy = self.locations.copy()
        locationsCopy.insert(preNode_index, request.pickUpLoc)
        # calculate the cost after inserting pickup location
        cost1 = self.computeDiff(locationsCopy[preNode_index - 1], locationsCopy[preNode_index + 1],
                                 request.pickUpLoc)
        locationsCopy.insert(afterNode_index, request.deliveryLoc)  # depot at the end
        # calculte the cost after inserting delivery location
        cost2 = self.computeDiff(locationsCopy[afterNode_index - 1],
                                 locationsCopy[afterNode_index + 1],
                                 request.deliveryLoc)
        return cost2 + cost1

    def print(self):
        """
        Method that prints the route
        """
        print("Route", end = '')
        for loc in self.locations:
            loc.print()
        print(" dist=" + str(self.distance))

    def isFeasible(self):
        """
        Method that checks feasbility. Returns True if feasible, else False
        """
        # route should start and end at the depot
        if self.locations[0] != self.problem.depot or self.locations[-1] != self.problem.depot:
            return False

        curTime = 0  # current time
        curLoad = 0  # current load in vehicle
        curNode = self.locations[0]  # current node
        pickedUp = set()  # set with all requests that we picked up, used to check precedence

        # iterate over route and check feasibility of time windows, capacity and precedence
        for i in range(1, len(self.locations) - 1):
            prevNode = self.locations[i - 1]
            curNode = self.locations[i]
            dist = self.problem.distMatrix[prevNode.nodeID][curNode.nodeID]
            # velocity = 1 dist = time
            curTime = max(curNode.startTW, curTime + prevNode.servTime + dist)

            # check if time window is respected
            if curTime > curNode.endTW:
                return False
            # check if capacity not exceeded
            curLoad += curNode.demand
            if curLoad > self.problem.capacity:
                return False
            # check if we don't do a delivery before a pickup
            if curNode.typeLoc == 1:
                # it is a pickup
                pickedUp.add(curNode.requestID)
            else:
                # it is a delivery
                # check if we picked up the request
                if curNode.requestID not in pickedUp:
                    return False
                pickedUp.remove(curNode.requestID)

        # finally, check if all pickups have been delivered
        if len(pickedUp) > 0:
            return False
        return True

    def removeRequest(self, request):
        """
        Method that removes a request from the route. 
        """
        # remove the request, the pickup and the delivery
        self.requests.remove(request)
        self.locations.remove(request.pickUpLoc)
        self.locations.remove(request.deliveryLoc)
        # the distance changes, so update
        # revise.
        # self.distance = self.computeDistance()

        # *** add this method

    def addRequest(self, request, preNode_index, afterNode_index):
        """
        Method that add a request to the route.
         """
        # add the request, the pickup and the delivery
        requestsCopy = self.requests.copy()
        locationsCopy = self.locations.copy()
        requestsCopy.add(request)
        locationsCopy.insert(preNode_index, request.pickUpLoc)
        locationsCopy.insert(afterNode_index, request.deliveryLoc)
        afterInsertion = Route(locationsCopy, requestsCopy, self.problem)
        if afterInsertion.feasible:
            self.requests.add(request)
            self.locations.insert(preNode_index, request.pickUpLoc)
            self.locations.insert(afterNode_index, request.deliveryLoc)
            cost = self.compute_cost_add_one_request(preNode_index, afterNode_index, request)
            # revise.
            # self.distance = self.computeDistance()
            return cost
        else:
            return - 1

    def copy(self):
        """
        Method that returns a copy of the route
        """
        locationsCopy = self.locations.copy()
        requestsCopy = self.requests.copy()
        return Route(locationsCopy, requestsCopy, self.problem)

    def greedyInsert(self, request):
        """
        Method that inserts the pickup and delivery of a request at the positions
        that give the shortest total distance. Returns best route. 

        Parameters
        ----------
        request : Request
            the request that should be inserted.

        Returns
        -------
        bestInsert : Route
            Route with the best insertion.

        """
        requestsCopy = self.requests.copy()
        requestsCopy.add(request)
        # print('request ', request)

        minDist = sys.maxsize  # initialize as extremely large number
        bestInsert = None  # if infeasible the bestInsert will be None
        minCost = sys.maxsize
        # iterate over all possible insertion positions for pickup and delivery

        for i in range(1, len(self.locations)):
            for j in range(i + 1, len(self.locations) + 1):  # delivery after pickup
                locationsCopy = self.locations.copy()
                locationsCopy.insert(i, request.pickUpLoc)
                locationsCopy.insert(j, request.deliveryLoc)  # depot at the end
                afterInsertion = Route(locationsCopy, requestsCopy, self.problem)
                # check if insertion is feasible
                if afterInsertion.feasible:
                    # check if cheapest
                    # revise. only calculate the cost
                    cost = self.compute_cost_add_one_request(i, j, request)
                    if cost < minCost:
                        bestInsert = afterInsertion
                        minCost = cost
        return bestInsert, minCost

