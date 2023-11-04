from pdptw import PDPTW
from alns import ALNS

testI = "Instances/lrc104.txt"
problem = PDPTW.readInstance(testI)

# Static parameters
nDestroyOps = 9
nRepairOps = 3
minSizeNBH = 1
nIterations = 2800

# Parameters to tune:
maxPercentageNHB = 5
tau = 0.03
coolingRate = 0.9990
decayParameter = 0.15
noise = 0.015

alns = ALNS(problem, nDestroyOps, nRepairOps, nIterations, minSizeNBH, maxPercentageNHB, tau, coolingRate, decayParameter, noise)
alns.execute()
