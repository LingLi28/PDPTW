import random, time
import xlsxwriter

import numpy as np
import pandas as pd
from numpy import log as ln
import matplotlib.pyplot as plt

from destroy import Destroy
from solution import Solution
from repair import Repair
from parameters import Parameters


class ALNS:
    """
    Class that models the ALNS algorithm. 

    Parameters
    ----------
    problem : PDPTW
        The problem instance that we want to solve.
    nDestroyOps : int
        number of destroy operators.
    nRepairOps : int
        number of repair operators.
    randomGen : Random
        random number generator
    currentSolution : Solution
        The current solution in the ALNS algorithm
    bestSolution : Solution
        The best solution currently found
    bestDistance : int
        Distance of the best solution
    """

    def __init__(self, problem, nDestroyOps, nRepairOps, nIterations, minSizeNBH, maxPercentageNHB, tau, coolingRate, decayParameter, noise):
        self.problem = problem
        self.nDestroyOps = nDestroyOps
        self.nRepairOps = nRepairOps
        self.randomGen = random.Random(Parameters.randomSeed)  # used for reproducibility

        self.wDestroy = [1 for i in range(nDestroyOps)]  # weights of the destroy operators
        self.wRepair = [1 for i in range(nRepairOps)]  # weights of the repair operators
        self.destroyUseTimes = [0 for i in range(nDestroyOps)]  # The number of times the destroy operator has been used
        self.repairUseTimes = [0 for i in range(nRepairOps)]  # The number of times the repair operator has been used
        self.destroyScore = [1 for i in range(nDestroyOps)]  # the score of destroy operators
        self.repairScore = [1 for i in range(nRepairOps)]  # the score of repair operators

        # Parameters for tuning
        self.nIterations = nIterations
        self.minSizeNBH = minSizeNBH
        self.maxPercentageNHB = maxPercentageNHB
        self.tau = tau
        self.coolingRate = coolingRate
        self.decayParameter = decayParameter
        self.noise = noise

        # Presenting results
        self.register_weights_over_time = False
        self.removal_weights_per_iteration = []
        self.insertion_weights_per_iteration = []
        
        self.register_objective_value_over_time = False
        self.list_objective_values = []

    def printWeight(self):
        print('wDestroy', end = ' ')
        for w in self.wDestroy:
            print(w, end = ' ')
        print('wRepair', end = ' ')
        for w in self.wRepair:
            print(w, end = ' ')
        print(f'\n\n Destroy score')
        print(self.destroyScore)

    def constructInitialSolution(self):
        """
        Method that constructs an initial solution using random insertion
        """
        self.currentSolution = Solution(self.problem, list(), list(), list(self.problem.requests.copy()))
        self.currentSolution.executeRandomInsertion(self.randomGen)
        self.currentSolution.computeDistance()
        self.bestSolution = self.currentSolution.copy()
        self.bestDistance = self.currentSolution.distance
        
        # Print initial solution
                
        # print('-------initial solution-----')
        # self.currentSolution.print()
        # print("Created initial solution with distance: " + str(self.bestDistance))
        
        # Define max neighborhood size
        number_of_request = len(self.problem.requests)
        self.maxSizeNBH = max(1, int(np.floor(self.maxPercentageNHB/100*number_of_request)))

        # Find starting temperature
        self.T = self.findStartingTemperature(self.tau, self.bestDistance)

    def findStartingTemperature(self, startTempControlParam, starting_solution):
        delta = startTempControlParam*starting_solution
        T = float(-delta/ln(0.5))
        return round(T, 4)
            

    def execute(self):
        """
        Method that executes the ALNS
        """
        starttime = time.time()  # get the start time
        self.starttime_best_objective = time.time()
        self.real_dist = np.inf
        
        self.constructInitialSolution()
        
        for i in range(self.nIterations):
            self.max_arc_length = self.currentSolution.calculateMaxArc()
            # Simulated annealing
            self.iteration_number = i
            self.checkIfAcceptNewSol()
            print(f'Iteration number {i}')
            # Print solution per iteration
            objective_value =  self.tempSolution.distance
            # print("Iteration " + str(i) + ": Found solution with distance: " + str(objective_value))

            
            # To plot weights of the operators over time 
            if self.register_weights_over_time:
                self.removal_weights_per_iteration.append(self.wDestroyPlot)
                self.insertion_weights_per_iteration.append(self.wDestroyPlot)
            
            # To plot objective values over time
            if self.register_objective_value_over_time:
                self.list_objective_values.append(objective_value)
                
        # print(self.wDestroy)
        # print(self.wRepair)
        endtime = time.time()  # get the end time
        cpuTime = round(endtime - starttime, 3)
        
        # Print status at termination
        print("Terminated. Final distance: " + str(self.bestSolution.distance) + ", cpuTime: " + str(cpuTime) + " seconds")
        
        time_best_objective = self.time_best_objective_found - self.starttime_best_objective
        
        print(f'Best objective value found after: {round(time_best_objective, 3)} seconds')
        
        print(f'Best objective value found after: {self.optimal_iteration_number} iterations')
        
        # print(self.repairUseTimes)

        # Plot weights of the operators over time 
        if self.register_weights_over_time:
            iterations_list = np.arange(0, self.nIterations)
                        
            weight_removal1 = [round(weight[0], 4) for weight in self.removal_weights_per_iteration]
            weight_removal2 = [round(weight[1], 4) for weight in self.removal_weights_per_iteration]
            weight_removal3 = [round(weight[2], 4) for weight in self.removal_weights_per_iteration]
            weight_removal4 = [round(weight[3], 4) for weight in self.removal_weights_per_iteration]
            weight_removal5 = [round(weight[4], 4) for weight in self.removal_weights_per_iteration]
            weight_removal6 = [round(weight[5], 4) for weight in self.removal_weights_per_iteration]
            weight_removal7 = [round(weight[6], 4) for weight in self.removal_weights_per_iteration]
            weight_removal8 = [round(weight[7], 4) for weight in self.removal_weights_per_iteration]
            weight_removal9 = [round(weight[8], 4) for weight in self.removal_weights_per_iteration]
            
            plt.plot(iterations_list, weight_removal1, label="Random request")
            plt.plot(iterations_list, weight_removal2, label="Worst-distance")
            plt.plot(iterations_list, weight_removal3, label="Worst-time")
            plt.plot(iterations_list, weight_removal4, label="Random route")
            plt.plot(iterations_list, weight_removal5, label="Shaw")
            plt.plot(iterations_list, weight_removal6, label="Promixity-based")
            plt.plot(iterations_list, weight_removal7, label="Time-based")
            plt.plot(iterations_list, weight_removal8, label="Demand-based")
            plt.plot(iterations_list, weight_removal9, label="Worst-neighborhood")
            plt.xlabel('Iteration number', fontsize=12)
            plt.ylabel('Weight', fontsize=12)
            plt.legend(loc="upper right", fontsize='small')
            plt.show()
            
            
            weight_insertion1 = [round(weight[0], 4) for weight in self.removal_weights_per_iteration]
            weight_insertion2 = [round(weight[1], 4) for weight in self.removal_weights_per_iteration]
            weight_insertion3 = [round(weight[2], 4) for weight in self.removal_weights_per_iteration]

            plt.plot(iterations_list, weight_insertion1, label="Random request")
            plt.plot(iterations_list, weight_insertion2, label="Basic greedy")
            plt.plot(iterations_list, weight_insertion3, label="Regret")
            plt.xlabel('Iteration number', fontsize=12)
            plt.ylabel('Weight', fontsize=12)
            plt.legend(loc="upper right", fontsize='small')
            plt.show()
            
        # Plot objective values over time
        if self.register_objective_value_over_time:
            iterations_list = np.arange(0, self.nIterations)
            objective_values = [int(value) for value in self.list_objective_values]
            
            df = pd.DataFrame(objective_values)
            writer = pd.ExcelWriter('Objective values.xlsx', engine='xlsxwriter')
            df.to_excel(writer, sheet_name='1', index=False)
            writer.save()
            
            plt.plot(iterations_list, self.list_objective_values)

            plt.xlabel('Iteration number', fontsize=12)
            plt.ylabel('Objective value', fontsize=12)
            plt.show()
            
    # @Log('time_output.csv')
    def checkIfAcceptNewSol(self):
        """
        Method that checks if we accept the newly found solution
        """
        # Copy the current solution
        self.tempSolution = self.currentSolution.copy()
        # print('before change ')
        # self.tempSolution.print()
        # decide on the size of the neighbourhood
        sizeNBH = self.randomGen.randint(self.minSizeNBH, self.maxSizeNBH)
        destroyOpNr = self.determineDestroyOpNr()
        # print('destroyOpNr ', destroyOpNr)
        repairOpNr = self.determineRepairOpNr()
        # print('repairOpNr ', repairOpNr)
        self.destroyAndRepair(destroyOpNr, repairOpNr, sizeNBH)

        # print('after destroy and repair ')
        # self.tempSolution.print()

        # (self.tempSolution.computeDistance())

        self.tempSolution.computeDistanceWithNoise(self.max_arc_length, self.noise, self.randomGen)

        if self.tempSolution.distance < self.currentSolution.distance:
            if self.tempSolution.distanceType == 0:
                self.tempSolution.no_noise_succesful +=1
            elif self.tempSolution.distanceType == 1:
                self.tempSolution.noise_succesful +=1
            self.currentSolution = self.tempSolution.copy()
            # we found a global best solution
            if self.tempSolution.distance < self.bestDistance:  # update best solution
                self.bestDistance = self.tempSolution.distance
                self.bestSolution = self.tempSolution.copy()
                self.destroyScore[destroyOpNr] += Parameters.w1
                self.repairScore[repairOpNr] += Parameters.w1  # the new solution is a new global best, 1.5
                new_real_dist = self.tempSolution.computeDistance()
                if new_real_dist < self.real_dist:
                    self.real_dist = new_real_dist
                    # print(f'New best global solution found: {real_dist}')
                    self.time_best_objective_found = time.time()
                    self.optimal_iteration_number = self.iteration_number
            else:
                self.destroyScore[destroyOpNr] += Parameters.w2
                self.repairScore[repairOpNr] += Parameters.w2  # the new solution is better than the current one 1.2
        else:
            if self.randomGen.random() < np.exp(
                    - (self.tempSolution.distance - self.currentSolution.distance) / self.T):
                self.currentSolution = self.tempSolution.copy()
                self.destroyScore[destroyOpNr] += Parameters.w3  # the new solution is accepted 0.8
                self.repairScore[repairOpNr] += Parameters.w3
            else:
                self.destroyScore[destroyOpNr] += Parameters.w4  # the new solution is rejected 0.6
                self.repairScore[repairOpNr] += Parameters.w4

        # Update the ALNS weights
        self.updateWeights(destroyOpNr, repairOpNr)
        # Update temperature
        self.T = self.coolingRate * self.T  

    def updateWeights(self, destroyOpNr, repairOpNr):
        """
        Method that updates the weights of the destroy and repair operators
        """
        self.destroyUseTimes[destroyOpNr] += 1
        self.repairUseTimes[repairOpNr] += 1

        self.wDestroy[destroyOpNr] = self.wDestroy[destroyOpNr] * (1 - self.decayParameter) + self.decayParameter * (
                self.destroyScore[destroyOpNr] / self.destroyUseTimes[destroyOpNr])
        
        self.wDestroyPlot = self.wDestroy.copy()

        self.wRepair[repairOpNr] = self.wRepair[repairOpNr] * (1 - self.decayParameter) + self.decayParameter * (
                self.repairScore[repairOpNr] / self.repairUseTimes[repairOpNr])
        self.wRepairPlot = self.wDestroy.copy()


    def determineDestroyOpNr(self):
        """
        Method that determines the destroy operator that will be applied. 
        Currently we just pick a random one with equal probabilities. 
        Could be extended with weights
        """
        destroyOperator = -1
        destroyRoulette = np.array(self.wDestroy).cumsum()
        r = self.randomGen.uniform(0, max(destroyRoulette))  # uniform distribution
        for i in range(len(self.wDestroy)):
            if destroyRoulette[i] >= r:
                destroyOperator = i
                break
        return destroyOperator

    def determineRepairOpNr(self):
        """
        Method that determines the repair operator that will be applied. 
        Currently we just pick a random one with equal probabilities. 
        Could be extended with weights
        """
        repairOperator = -1
        repairRoulette = np.array(self.wRepair).cumsum()
        r = self.randomGen.uniform(0, max(repairRoulette))
        for i in range(len(self.wRepair)):
            if repairRoulette[i] >= r:
                repairOperator = i
                break
        return repairOperator

    def destroyAndRepair(self, destroyHeuristicNr, repairHeuristicNr, sizeNBH):
        """
        Method that performs the destroy and repair. More destroy and/or
        repair methods can be added

        Parameters
        ----------
        destroyHeuristicNr : int
            number of the destroy operator.
        repairHeuristicNr : int
            number of the repair operator.
        sizeNBH : int
            size of the neighborhood.

        """
        # print('sizeNBH=', sizeNBH)
        # Perform the destroy
        destroySolution = Destroy(self.problem, self.tempSolution)
        if destroyHeuristicNr == 0:
            destroySolution.executeRandomRemoval(sizeNBH, self.randomGen)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 1:
            destroySolution.executeWorstCostRemoval(sizeNBH)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 2:
            destroySolution.executeWorstTimeRemoval(sizeNBH)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 3:
            destroySolution.executeRandomRouteRemoval(sizeNBH, self.randomGen)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 4:
            destroySolution.executeShawRequestRemoval(sizeNBH, self.randomGen)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 5:
            destroySolution.executeProximityBasedRemoval(sizeNBH, self.randomGen)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 6:
            destroySolution.executeTimeBasedRemoval(sizeNBH, self.randomGen)
            # print('after destroy')
            # destroySolution.solution.print()
        elif destroyHeuristicNr == 7:
            destroySolution.executeDemandBasedRemoval(sizeNBH, self.randomGen)
            # print('after destroy')
            # destroySolution.solution.print()
            
        # Last destroy method gives error somehow...
        # elif destroyHeuristicNr == 8:
        #     destroySolution.executeWorstNeighborhoodRemoval(sizeNBH)
        #     # print('after destroy')
        #     # destroySolution.solution.print()

        # Perform the repair
        repairSolution = Repair(self.problem, self.tempSolution)
        if repairHeuristicNr == 0:
            repairSolution.executeRandomInsertion(self.randomGen)
            # print('after repair')
            # self.tempSolution.print()
        elif repairHeuristicNr == 1:
            repairSolution.executeGreedyInsertion()
            # print('after repair')
            # self.tempSolution.print()
        elif repairHeuristicNr == 2:
            repairSolution.executeRegretInsertion()
            # print('after repair')
            # self.tempSolution.print()
