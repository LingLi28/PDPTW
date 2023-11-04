import random
import xlsxwriter
import time

import numpy as np

from pdptw import PDPTW
from alns import ALNS


class ScenarioAnalysis:

    # Constant parameters
    nDestroyOps = 8
    nRepairOps = 3
    nIterations = 1000
    minSizeNBH = 1

    # Define instances

    INSTANCES = ["Instances/c202C16.txt",
                 "Instances/lc102.txt",
                 "Instances/lc108.txt",
                 "Instances/lc207.txt",
                 "Instances/lr112.txt",
                 "Instances/lr205.txt",
                 "Instances/lrc104.txt",
                 "Instances/lrc206.txt",
                 "Instances/r102C18.txt",
                 "Instances/rc204C16.txt"]

    EXECUTIONS_PER_INSTANCE = 1

    # Define ranges of parameter values to test
    MAX_PERCENTAGES = [] # [5, 6, 7, 8, 9, 10]
    TAU = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    COOLING_RATES = [0.9990, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995, 0.9996, 0.9997, 0.9998, 0.9999]
    REACTION_FACTORS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    NOISE_FACTORS = [0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040]

    def __init__(self, maxPercentageNHB, tau, coolingRate, decayParameter, noise):
        self.maxPercentageNHB = maxPercentageNHB
        self.tau = tau
        self.coolingRate = coolingRate
        self.decayParameter = decayParameter
        self.noise = noise
        self.current_scenario_nr = 1
        self.total_scenarios = len(self.MAX_PERCENTAGES) + len(self.TAU) + len(self.COOLING_RATES) + len(
            self.REACTION_FACTORS) + len(self.NOISE_FACTORS)
        self.start_time = time.time()

    def findBestPercentage(self):

        '''
        Tuning percentage neighborhood parameter
        '''

        workbook = xlsxwriter.Workbook('tune_percentage.xlsx')
        worksheet = workbook.add_worksheet()

        self.average_solution_per_percentage = []
        for index_perc, percentage in enumerate(self.MAX_PERCENTAGES):

            print(
                f'\nCurrent percentage: {percentage}/{self.MAX_PERCENTAGES[-1]}\t\t\t\t\tScenario number: '
                f'{self.current_scenario_nr}/{self.total_scenarios} after '
                f'{round(time.time() - self.start_time, 3)} seconds\n')
            self.current_scenario_nr += 1

            worksheet.write(index_perc, 0, percentage)
            self.average_solution_per_instance = []
            for index_instance, instance in enumerate(self.INSTANCES):

                print(f'\t\tCurrent instance: {index_instance + 1}/{len(self.INSTANCES)}')

                self.solutions_per_execution = []
                self.iteration_nr = 1
                problem = PDPTW.readInstance(instance)
                for _ in range(self.EXECUTIONS_PER_INSTANCE):

                    alns = ALNS(problem, self.nDestroyOps, self.nRepairOps, self.nIterations, self.minSizeNBH,
                                percentage, self.tau, self.coolingRate, self.decayParameter, self.noise)
                    alns.randomGen = random.Random(self.iteration_nr)
                    alns.execute()
                    self.iteration_nr += 1

                    # Cache data
                    self.solutions_per_execution.append(alns.bestSolution.distance)

                self.average_solution_per_instance.append(np.mean(self.solutions_per_execution))

                # Write average solution per index to excel
                worksheet.write(index_perc, index_instance + 1, np.mean(self.solutions_per_execution))

            self.average_solution_per_percentage.append(np.mean(self.average_solution_per_instance))
        workbook.close()
        lowest_average_index = self.average_solution_per_percentage.index(min(self.average_solution_per_percentage))

        self.optimal_percentage = self.MAX_PERCENTAGES[lowest_average_index]
        self.maxPercentageNHB = self.optimal_percentage

    def findBestTau(self):

        '''
        Tuning tau parameter
        '''

        workbook = xlsxwriter.Workbook('tune_tau.xlsx')
        worksheet = workbook.add_worksheet()

        self.average_solution_per_tau = []
        for index_tau, tau in enumerate(self.TAU):

            print(
                f'\nCurrent tau: {tau}/{self.TAU[-1]}\t\t\t\t\tScenario number: {self.current_scenario_nr}/'
                f'{self.total_scenarios} after {round(time.time() - self.start_time, 3)} seconds\n')
            self.current_scenario_nr += 1

            worksheet.write(index_tau, 0, tau)
            self.average_solution_per_instance = []
            for index_instance, instance in enumerate(self.INSTANCES):

                print(f'\t\tCurrent instance: {index_instance + 1}/{len(self.INSTANCES)}')

                self.solutions_per_execution = []
                self.iteration_nr = 1
                problem = PDPTW.readInstance(instance)
                for _ in range(self.EXECUTIONS_PER_INSTANCE):

                    alns = ALNS(problem, self.nDestroyOps, self.nRepairOps, self.nIterations, self.minSizeNBH,
                                self.maxPercentageNHB, tau, self.coolingRate, self.decayParameter, self.noise)
                    alns.randomGen = random.Random(self.iteration_nr)
                    alns.execute()
                    self.iteration_nr += 1

                    # Cache data
                    self.solutions_per_execution.append(alns.bestSolution.distance)

                self.average_solution_per_instance.append(np.mean(self.solutions_per_execution))

                # Write average solution per index to excel
                worksheet.write(index_tau, index_instance + 1, np.mean(self.solutions_per_execution))

            self.average_solution_per_tau.append(np.mean(self.average_solution_per_instance))
        workbook.close()
        lowest_average_index = self.average_solution_per_tau.index(min(self.average_solution_per_tau))

        self.optimal_tau = self.TAU[lowest_average_index]
        self.tau = self.optimal_tau

    def findBestCoolingFactor(self):

        '''
        Tuning cooling factor
        '''

        workbook = xlsxwriter.Workbook('tune_c.xlsx')
        worksheet = workbook.add_worksheet()

        self.average_solution_per_c = []
        for index_c, c in enumerate(self.COOLING_RATES):

            print(
                f'\nCurrent cooling factor: {c}/{self.COOLING_RATES[-1]}\t\t\t\t\tScenario number: '
                f'{self.current_scenario_nr}/{self.total_scenarios} after '
                f'{round(time.time() - self.start_time, 3)} seconds\n')
            self.current_scenario_nr += 1

            worksheet.write(index_c, 0, c)
            self.average_solution_per_instance = []
            for index_instance, instance in enumerate(self.INSTANCES):

                print(f'\t\tCurrent instance: {index_instance + 1}/{len(self.INSTANCES)}')

                self.solutions_per_execution = []
                self.iteration_nr = 1
                problem = PDPTW.readInstance(instance)
                for _ in range(self.EXECUTIONS_PER_INSTANCE):

                    alns = ALNS(problem, self.nDestroyOps, self.nRepairOps, self.nIterations, self.minSizeNBH,
                                self.maxPercentageNHB, self.tau, c, self.decayParameter, self.noise)
                    alns.randomGen = random.Random(self.iteration_nr)
                    alns.execute()
                    self.iteration_nr += 1

                    # Cache data
                    self.solutions_per_execution.append(alns.bestSolution.distance)

                self.average_solution_per_instance.append(np.mean(self.solutions_per_execution))

                # Write average solution per index to excel
                worksheet.write(index_c, index_instance + 1, np.mean(self.solutions_per_execution))

            self.average_solution_per_c.append(np.mean(self.average_solution_per_instance))
        workbook.close()
        lowest_average_index = self.average_solution_per_c.index(min(self.average_solution_per_c))

        self.optimal_c = self.COOLING_RATES[lowest_average_index]
        self.coolingRate = self.optimal_c

    def findBestReactionFactor(self):

        '''
        Tuning reaction factor
        '''

        workbook = xlsxwriter.Workbook('tune_r.xlsx')
        worksheet = workbook.add_worksheet()

        self.average_solution_per_r = []
        for index_r, r in enumerate(self.REACTION_FACTORS):

            print(
                f'\nCurrent reaction factor: {r}/{self.REACTION_FACTORS[-1]}\t\t\t\t\tScenario number: '
                f'{self.current_scenario_nr}/{self.total_scenarios} after '
                f'{round(time.time() - self.start_time, 3)} seconds\n')
            self.current_scenario_nr += 1

            worksheet.write(index_r, 0, r)
            self.average_solution_per_instance = []
            for index_instance, instance in enumerate(self.INSTANCES):

                print(f'\t\tCurrent instance: {index_instance + 1}/{len(self.INSTANCES)}')

                self.solutions_per_execution = []
                self.iteration_nr = 1
                problem = PDPTW.readInstance(instance)
                for _ in range(self.EXECUTIONS_PER_INSTANCE):

                    alns = ALNS(problem, self.nDestroyOps, self.nRepairOps, self.nIterations, self.minSizeNBH,
                                self.maxPercentageNHB, self.tau, self.coolingRate, r, self.noise)
                    alns.randomGen = random.Random(self.iteration_nr)
                    alns.execute()
                    self.iteration_nr += 1

                    # Cache data
                    self.solutions_per_execution.append(alns.bestSolution.distance)

                self.average_solution_per_instance.append(np.mean(self.solutions_per_execution))

                # Write average solution per index to excel
                worksheet.write(index_r, index_instance + 1, np.mean(self.solutions_per_execution))

            self.average_solution_per_r.append(np.mean(self.average_solution_per_instance))
        workbook.close()
        lowest_average_index = self.average_solution_per_r.index(min(self.average_solution_per_r))

        self.optimal_r = self.REACTION_FACTORS[lowest_average_index]
        self.decayParameter = self.optimal_r

    def findBestNoise(self):

        '''
        Tuning noise parameter
        '''

        workbook = xlsxwriter.Workbook('tune_noise.xlsx')
        worksheet = workbook.add_worksheet()

        self.average_solution_per_noise = []
        for index_noise, noise in enumerate(self.NOISE_FACTORS):

            print(
                f'\nCurrent noise: {noise}/{self.NOISE_FACTORS[-1]}\t\t\t\t\tScenario number: '
                f'{self.current_scenario_nr}/{self.total_scenarios} after '
                f'{round(time.time() - self.start_time, 3)} seconds\n')
            self.current_scenario_nr += 1

            worksheet.write(index_noise, 0, noise)
            self.average_solution_per_instance = []
            for index_instance, instance in enumerate(self.INSTANCES):

                print(f'\t\tCurrent instance: {index_instance + 1}/{len(self.INSTANCES)}')

                self.solutions_per_execution = []
                self.iteration_nr = 1
                problem = PDPTW.readInstance(instance)
                for _ in range(self.EXECUTIONS_PER_INSTANCE):

                    alns = ALNS(problem, self.nDestroyOps, self.nRepairOps, self.nIterations, self.minSizeNBH,
                                self.minSizeNBH, self.tau, self.coolingRate, self.decayParameter, noise)
                    alns.randomGen = random.Random(self.iteration_nr)
                    alns.execute()
                    self.iteration_nr += 1

                    # Cache data
                    self.solutions_per_execution.append(alns.bestSolution.distance)

                self.average_solution_per_instance.append(np.mean(self.solutions_per_execution))

                # Write average solution per index to excel
                worksheet.write(index_noise, index_instance + 1, np.mean(self.solutions_per_execution))

            self.average_solution_per_noise.append(np.mean(self.average_solution_per_instance))
        workbook.close()
        lowest_average_index = self.average_solution_per_noise.index(min(self.average_solution_per_noise))

        self.optimal_noise = self.NOISE_FACTORS[lowest_average_index]
        self.noise = self.optimal_noise


starting_maxPercentageNHB = 5
starting_tau = 0.05
starting_coolingRate = 0.9990
starting_decayParameter = 0.10
starting_noise = 0.020

scenario_ana = ScenarioAnalysis(starting_maxPercentageNHB, starting_tau, starting_coolingRate, starting_decayParameter,
                                starting_noise)

# print(f'\n\n\n\n#####   FIND BEST PERCENTAGE NBH   #####\n')
# scenario_ana.findBestPercentage()

print(f'\n\n\n\n#####   FIND BEST TAU   #####\n')
scenario_ana.findBestTau()

print(f'\n\n\n\n#####   FIND BEST COOLING FACTOR   #####\n')
scenario_ana.findBestCoolingFactor()

print(f'\n\n\n\n#####   FIND BEST REACTION FACTOR   #####\n')
scenario_ana.findBestReactionFactor()

print(f'\n\n\n\n#####   FIND BEST NOISE   #####\n')
scenario_ana.findBestNoise()

print('\n###################################################')

print(f'\n\nOptimal parameter values found:\n')
print(f'\tPercentage NBH: {scenario_ana.maxPercentageNHB}')
print(f'\tTau: {scenario_ana.tau}')
print(f'\tCooling rate: {scenario_ana.coolingRate}')
print(f'\tReaction factor: {scenario_ana.decayParameter}')
print(f'\tNoise: {scenario_ana.noise}')