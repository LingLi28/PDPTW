from route import Route

class Solution:
    """
    Method that represents a solution to the PDPTW

    Attributes
    ----------
    problem : PDPTW
        the problem that corresponds to this solution
    routes : List of Routes
         Routes in the current solution
    served : List of Requests
        Requests served in the current solution
    notServed : List of Requests
         Requests not served in the current solution 
    distance : int
        total distance of the current solution
    """

    def __init__(self, problem, routes, served, notServed):
        self.problem = problem
        self.routes = routes
        self.served = served
        self.notServed = notServed
        self.distance = self.computeDistance()

    def computeDistance(self):
        """
        Method that computes the distance of the solution
        """
        self.distance = 0
        for route in self.routes:
            self.distance += route.distance
        return self.distance

    def computeDistanceWithNoise(self, max_arc_dist, noise, randomGen):
        """
        Method that computes the distance of the solution and implements noise
        """
        self.noise_succesful = 1
        self.no_noise_succesful = 1
        self.normal_distance = 0
        for route in self.routes:
            self.normal_distance += route.distance
        maxN = noise * max_arc_dist
        random_noise = randomGen.uniform(-maxN, maxN)
        self.noise_distance = max(0, self.distance + random_noise)
        summation = self.noise_succesful + self.no_noise_succesful
        rand_number = randomGen.random()
        if rand_number < self.no_noise_succesful / summation:
            self.distance = self.normal_distance
            self.distanceType = 0  # No noise is used in the objective solution
        else:
            self.distance = self.noise_distance
            self.distanceType = 1  # Noise is used in the objective solution
        return self.distance

    def calculateMaxArc(self):
        max_arc_length = 0
        for route in self.routes:
            for i in range(1, len(route.locations)):
                first_node_ID = route.locations[i - 1].nodeID
                second_node_ID = route.locations[i].nodeID
                arc_length = self.problem.distMatrix[first_node_ID][second_node_ID]
                if arc_length > max_arc_length:
                    max_arc_length = arc_length
        return max_arc_length

    def print(self):
        """
        Method that prints the solution
        """
        nRoutes = len(self.routes)
        nNotServed = len(self.notServed)
        print('total distcance ' + str(self.distance) + " Solution with " + str(nRoutes) + " routes and " + str(
            nNotServed) + " unserved requests: ")
        for route in self.routes:
            route.print()

        print("\n\n")

    def executeRandomRemoval(self, nRemove, randomGen):
        """
        Method that executes a random removal of requests
        
        This is destroy method number 1 in the ALNS

        Parameters
        ----------
        nRemove : int
            number of requests that is removed.
                 
        Parameters
        ----------
        randomGen : Random
            Used to generate random numbers

        """
        print('nRemove = ' + str(nRemove))
        for i in range(nRemove):
            # terminate if no more requests are served
            if len(self.served) == 0:
                break
            # pick a random request and remove it from the solutoin
            req = randomGen.choice(self.served)
            self.removeRequest(req)

        self.distance = self.computeDistance()

    def removeRequest(self, request):
        """
        Method that removes a request from the solution
        """
        # iterate over routes to find in which route the request is served
        for route in self.routes:
            if request in route.requests:
                # remove the request from the route and break from loop
                route.removeRequest(request)
                break
        # update lists with served and unserved requests
        self.served.remove(request)
        self.notServed.append(request)
        # revise update distance
        # self.computeDistance()

    def addRequest(self, request, insertRoute, prevNode_index, afterNode_index):
        '''
        Method that add a request to the solution
        '''
        if insertRoute == None:
            locList = [self.problem.depot, request.pickUpLoc, request.deliveryLoc, self.problem.depot]
            newRoute = Route(locList, {request}, self.problem)
            self.routes.append(newRoute)
            self.distance += newRoute.distance
        else:
            for route in self.routes:
                if route == insertRoute:
                    res = route.addRequest(request, prevNode_index, afterNode_index)
                    if res == -1:
                        locList = [self.problem.depot, request.pickUpLoc, request.deliveryLoc, self.problem.depot]
                        newRoute = Route(locList, {request}, self.problem)
                        self.routes.append(newRoute)
                        self.distance += newRoute.distance
                    else:
                        self.distance += res
        # update lists with served and unserved requests
        self.served.append(request)
        self.notServed.remove(request)
        # update distance
        # self.computeDistance()

    def copy(self):
        """
        Method that creates a copy of the solution and returns it
        """
        # need a deep copy of routes because routes are modifiable
        routesCopy = list()
        for route in self.routes:
            routesCopy.append(route.copy())
        copy = Solution(self.problem, routesCopy, self.served.copy(), self.notServed.copy())
        copy.computeDistance()
        return copy

    def executeRandomInsertion(self, randomGen):
        """
        Method that randomly inserts the unserved requests in the solution
        
        This is repair method number 1 in the ALNS
        
        Parameters
        ----------
        randomGen : Random
            Used to generate random numbers

        """
        # iterate over the list with unserved requests
        while len(self.notServed) > 0:
            # pick a random request
            req = randomGen.choice(self.notServed)

            # keep track of routes in which req could be inserted
            potentialRoutes = self.routes.copy()
            inserted = False
            while len(potentialRoutes) > 0:
                # pick a random route
                randomRoute = randomGen.choice(potentialRoutes)

                afterInsertion, cost = randomRoute.greedyInsert(req)
                if afterInsertion == None:
                    # insertion not feasible, remove route from potential routes
                    potentialRoutes.remove(randomRoute)
                else:
                    # insertion feasible, update routes and break from while loop
                    inserted = True
                    # print("Possible")
                    self.routes.remove(randomRoute)
                    self.routes.append(afterInsertion)
                    self.distance += cost
                    break

            # if we were not able to insert, create a new route
            if not inserted:
                # create a new route with the request
                locList = [self.problem.depot, req.pickUpLoc, req.deliveryLoc, self.problem.depot]
                newRoute = Route(locList, {req}, self.problem)
                self.routes.append(newRoute)
                self.distance += newRoute.distance
            # update the lists with served and notServed requests
            self.served.append(req)
            self.notServed.remove(req)
        # self.computeDistance()
