import numpy as np
# from timeLog import Log
# from Log.log import Log

class Destroy:
    '''
    Class that represents destroy methods

    Parameters
    ----------
    problem : PDPTW
        The problem instance that we want to solve.
    currentSolution : Solution
        The current solution in the ALNS algorithm
    randomGen : Random
        random number generator
    '''

    def __init__(self, problem, solution):
        self.problem = problem
        self.solution = solution

    '''Helper function method 2'''
    def findWorstCostRequest(self):
        cost = []
        # Making list with request ID's and their corresponding cost
        for route in self.solution.routes:
            for i in range(2, len(route.locations)):
                first_node_ID = route.locations[i - 2].nodeID
                middle_note_ID = route.locations[i - 1].nodeID
                last_node_ID = route.locations[i].nodeID
                request_ID = route.locations[i - 1].requestID
                dist = self.problem.distMatrix[first_node_ID][middle_note_ID]+self.problem.distMatrix[middle_note_ID][last_node_ID]
                cost.append([request_ID, dist])
        # Sort cost
        cost = sorted(cost, key = lambda d: d[1], reverse = True)
        chosen_request = None
        # Get request object that corresponds to worst cost 
        worst_cost_request_ID = cost[0][0]
        for req in self.solution.served:
            if req.ID == worst_cost_request_ID:
                chosen_request = req
                break
        return chosen_request

    '''Helper function method 3'''
    def findWorstTimeRequest(self):
        service_time_difference = []
        # Making list with request ID's and difference between serivce start time and the start of time window
        for route in self.solution.routes:
            route.calculateServiceStartTime()
            for location in route.locations:
                if location.typeLoc != 0:
                    difference = location.servStartTime - location.startTW
                    service_time_difference.append([location.requestID, difference])
        # Sort list with time differences
        service_time_difference = sorted(service_time_difference, key = lambda d: d[1], reverse = True)
        # Get request object that corresponds to worst cost
        worst_time_request_ID = service_time_difference[0][0]
        chosen_request = None
        for req in self.solution.served:
            if req.ID == worst_time_request_ID:
                chosen_request = req
                break
        return chosen_request

    '''Helper function method 4'''
    def findRandomRoute(self, randomGen):
        # First make a copy of the routes in the solution
        set_of_routes = self.solution.routes.copy()
        # Find select a random route that contains at least one request
        while True:
            if not set_of_routes:
                return None
            route = randomGen.choice(set_of_routes)
            # If no request can be removed from this route
            if len(route.locations) < 4:
                set_of_routes.remove(route)
            else:
                return route

    def findWorstCostRequestRandomRoute(self, randomGen):
        route = self.findRandomRoute(randomGen)
        cost = []
        # Making list with request ID's and their corresponding cost
        for i in range(2, len(route.locations)):
            first_node_ID = route.locations[i - 2].nodeID
            middle_note_ID = route.locations[i - 1].nodeID
            last_node_ID = route.locations[i].nodeID
            request_ID = route.locations[i - 1].requestID
            dist = self.problem.distMatrix[first_node_ID][middle_note_ID]+self.problem.distMatrix[middle_note_ID][last_node_ID]
            cost.append([request_ID, dist])
        # Sort cost
        cost = sorted(cost, key = lambda d: d[1], reverse = True)
        # Get request object that corresponds to worst cost 
        worst_cost_request_ID = cost[0][0]
        chosen_request = None
        for req in self.solution.served:
            if req.ID == worst_cost_request_ID:
                chosen_request = req
                break
        return chosen_request

    '''Helper functions method 5'''
    def findStartingLocationShaw(self, randomGen):
        # Choose random route
        potentialRoutes = self.solution.routes
        location = None
        # Revise.
        while potentialRoutes:
            route = randomGen.choice(potentialRoutes)
            # Might exist the situation of [depot, depot]
            if len(route.locations) > 2:
                # From this route, choose a random location which is not the depot
                location = randomGen.choice(
                    [location for location in route.locations if location.typeLoc != 0])
                break
            else:
                potentialRoutes.remove(route)
        return location

    def findNextShawRequest(self):
        # Initialize key variables and location that is currently selected
        locations, distances, start_tws, demands = [], [], [], []
        loc_i = self.last_shaw_location
        # Define values of key variables for location i
        location_i, start_tw_i, demand_i = loc_i.nodeID, loc_i.startTW, loc_i.demand
        # Find values of key variables for all other locations
        for route in self.solution.routes:
            for loc_j in route.locations:
                # Only consider locations which are not depots
                if loc_j.typeLoc != 0:
                    locations.append(loc_j)
                    location_j, start_tw_j, demand_j = loc_j.nodeID, loc_j.startTW, loc_j.demand
                    # Find difference of the two nodes in terms of the key variables
                    distance_diff = self.problem.distMatrix[location_i][location_j]
                    start_tw_diff = abs(start_tw_i-start_tw_j)
                    demand_diff = abs(demand_i-demand_j)
                    # Add differences to the lists of key variables
                    distances.append(distance_diff)
                    start_tws.append(start_tw_diff)
                    demands.append(demand_diff)
        # Normalize values
        if sum(start_tws):
            normalized_start_tws = list(map(lambda x: x / sum(start_tws), start_tws))
        else:
            normalized_start_tws = start_tws
        if sum(distances):
            normalized_distances = list(map(lambda x: x / sum(distances), distances))
        else:
            normalized_distances = distances
        if sum(demands):
            normalized_demands = list(map(lambda x: x / sum(demands), demands))
        else:
            normalized_demands = demands
        # normalized_distances = list(map(lambda x:x/sum(distances), distances))
        # normalized_start_tws = list(map(lambda x:x/sum(start_tws), start_tws))
        # normalized_demands = list(map(lambda x:x/sum(demands), demands))

        # Calculate relatednesses to each location based on the normalized values
        relatednesses = []
        for index, location in enumerate(locations):
            relatednesses.append((location,
                                  normalized_distances[index] +
                                  normalized_start_tws[index] +
                                  normalized_demands[index]))
        # Sort locations based on relatednesses and choose most related one
        relatednesses = sorted(relatednesses, key = lambda r: r[1], reverse = False)
        self.last_shaw_location = relatednesses[0][0]
        # Determine request that is related to the most related location
        chosen_request = None
        for req in self.solution.served:
            if req.ID == self.last_shaw_location.requestID:
                chosen_request = req
                break
        return chosen_request

    '''Helper function method 6'''
    def findNextProximityBasedRequest(self):
        # Initialize location that is currently selected
        loc_i = self.last_proximity_location
        closest = np.inf
        # Find closest location in terms of distance
        for route in self.solution.routes:
            for loc_j in route.locations:
                # Only consider locations which are not depots
                if loc_j.typeLoc != 0:
                    distance_diff = self.problem.distMatrix[loc_i.nodeID][loc_j.nodeID]
                    if distance_diff < closest:
                        chosen_location = loc_j
                        closest = distance_diff

        self.last_proximity_location = chosen_location
        chosen_request =None
        # Determine request that is related to the closest location
        for req in self.solution.served:
            if req.ID == self.last_proximity_location.requestID:
                chosen_request = req
                break
        return chosen_request


    '''Helper function method 7'''
    def findNextTimeBasedRequest(self):
        # Initialize location that is currently selected
        loc_i = self.last_time_based_location
        smallest_diff = np.inf

        # Find most related location in terms of start time window
        for route in self.solution.routes:
            for loc_j in route.locations:
                # Only consider locations which are not depots
                if loc_j.typeLoc != 0:
                    tw_diff = abs(loc_i.startTW - loc_j.startTW)
                    if tw_diff < smallest_diff:
                        chosen_location = loc_j
                        smallest_diff = tw_diff
        self.last_time_based_location = chosen_location
        chosen_request = None
        # Determine request that is related to the closest location
        for req in self.solution.served:
            if req.ID == self.last_time_based_location.requestID:
                chosen_request = req
                break
        return chosen_request

    '''Helper function method 8'''
    def findNextDemandBasedRequest(self):
        # Initialize location that is currently selected
        loc_i = self.last_demand_based_location
        smallest_diff = np.inf

        # Find most related location in terms of demand
        for route in self.solution.routes:
            for loc_j in route.locations:
                # Only consider locations which are not depots
                if loc_j.typeLoc != 0:
                    demand_diff = abs(loc_i.demand - loc_j.demand)
                    if demand_diff < smallest_diff:
                        chosen_location = loc_j
                        smallest_diff = demand_diff
        self.last_demand_based_location = chosen_location
        chosen_request = None
        # Determine request that is related to the closest location
        for req in self.solution.served:
            if req.ID == self.last_demand_based_location.requestID:
                chosen_request = req
                break
        return chosen_request

    '''Helper function method 9'''
    def findWorstNeighborhoodRequest(self):
        cost = []
        # Making list with request ID's and their corresponding cost
        for route in self.solution.routes:
            requests, ditstances = [], []
            total_dist = 0
            for i in range(2, len(route.locations)):
                first_node_ID = route.locations[i - 2].nodeID
                middle_note_ID = route.locations[i - 1].nodeID
                last_node_ID = route.locations[i].nodeID
                request_ID = route.locations[i - 1].requestID
                dist = self.problem.distMatrix[first_node_ID][middle_note_ID]+self.problem.distMatrix[middle_note_ID][last_node_ID]
                requests.append(request_ID)
                ditstances.append(dist)
                total_dist += dist
            for index, request in enumerate(requests):
                cost.append([request, ditstances[index]/total_dist])
        # Sort cost
        cost = sorted(cost, key = lambda d: d[1], reverse = True)
        # print(cost)
        # Get request object that corresponds to worst cost 
        worst_average_cost_request_ID = cost[0][0]
        chosen_request = None
        for req in self.solution.served:
            if req.ID == worst_average_cost_request_ID:
                chosen_request = req
                break
        return chosen_request


    '''Destroy method number 1'''

    # @Log('time_output.csv')
    def executeRandomRemoval(self, nRemove, randomGen):
        # print('nRemove = ' + str(nRemove))
        for i in range(nRemove):
            # terminate if no more requests are served
            if len(self.solution.served) == 0:
                break
            # pick a random request and remove it from the solutoin
            # print(self.solution.served)
            req = randomGen.choice(self.solution.served)
            if req != None:
                self.solution.removeRequest(req)

    '''Destroy method number 2'''

    # @Log('time_output.csv')
    def executeWorstCostRemoval(self, nRemove):
        for i in range(nRemove):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findWorstCostRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 3'''

    # @Log('time_output.csv')
    def executeWorstTimeRemoval(self, nRemove):
        for i in range(nRemove):
            if len(self.solution.served) == 0:
                break

            chosen_req = self.findWorstTimeRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 4'''

    # @Log('time_output.csv')
    def executeRandomRouteRemoval(self, nRemove, randomGen):
        for _ in range(nRemove):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findWorstCostRequestRandomRoute(randomGen)
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 5'''

    # @Log('time_output.csv')
    def executeShawRequestRemoval(self, nRemove, randomGen):
        if len(self.solution.served) == 0:
            return
        # Initialize starting location based on randomGen
        location = self.findStartingLocationShaw(randomGen)
        self.last_shaw_location = location

        # Select corresponding request
        request_ID = location.requestID
        for req in self.solution.served:
            if req.ID == request_ID:
                self.solution.removeRequest(req)
                break

        # Remove next requests based on relatednesses between locations
        for _ in range(nRemove-1):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findNextShawRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 6'''

    # @Log('time_output.csv')
    def executeProximityBasedRemoval(self, nRemove, randomGen):
        if len(self.solution.served) == 0:
            return
        # Initialize starting location
        location = self.findStartingLocationShaw(randomGen)
        self.last_proximity_location = location

        # Select corresponding request
        request_ID = location.requestID
        for req in self.solution.served:
            if req.ID == request_ID:
                self.solution.removeRequest(req)
                break

        # Remove next requests based on relatedness in terms of distance between locations
        for _ in range(nRemove-1):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findNextProximityBasedRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 7'''

    # @Log('time_output.csv')
    def executeTimeBasedRemoval(self, nRemove, randomGen):
        if len(self.solution.served) == 0:
            return
        # Initialize starting location
        location = self.findStartingLocationShaw(randomGen)
        self.last_time_based_location = location

        # Select corresponding request
        request_ID = location.requestID
        for req in self.solution.served:
            if req.ID == request_ID:
                self.solution.removeRequest(req)
                break

        # Remove next requests based on relatedness in terms of start time windows between locations
        for _ in range(nRemove-1):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findNextTimeBasedRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 8'''

    # @Log('time_output.csv')
    def executeDemandBasedRemoval(self, nRemove, randomGen):
        if len(self.solution.served) == 0:
            return
        # Initialize starting location
        location = self.findStartingLocationShaw(randomGen)
        self.last_demand_based_location = location

        # Select corresponding request
        request_ID = location.requestID
        for req in self.solution.served:
            if req.ID == request_ID:
                self.solution.removeRequest(req)
                break

        # Remove next requests based on relatedness in terms of start time windows between locations
        for _ in range(nRemove-1):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findNextDemandBasedRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

    '''Destroy method number 9'''

    # @Log('time_output.csv')
    def executeWorstNeighborhoodRemoval(self, nRemove):
        for _ in range(nRemove):
            if len(self.solution.served) == 0:
                break
            chosen_req = self.findWorstNeighborhoodRequest()
            # print("Chosen request:")
            # print(chosen_req)
            # print("\n")
            if chosen_req != None:
                self.solution.removeRequest(chosen_req)

