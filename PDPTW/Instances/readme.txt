#################################
Note by Rolf van Lieshout: below you find the original description of format, which is for an electric pickup and delivery problem. 
In our problem, we ignore this data. In addition, we only read in the first depot and ignore the others. 


#################################

The instances are formatted as follows:

###For each location the instance provides:
-StringId as a unique identifier
-Type indicates the function of the location, i.e,
---d: depot
---f: recharging station
--cp: customer pickup location
--cd: customer delivery location
-x, y are coordinates (distances are assumed to be euclidean) 
-demand specifies the quantity of freight capacity required (positive at pickup, negative at delivery)
-ReadyTime and DueDate are the beginning and the end of the time window (waiting is allowed)
-ServiceTime denotes the entire time spend at pickup delivery for loading unloading operations
-PartnerId is relevant for transportation requests and provides the StringId of the partner of each pickup and delivery location

###For the electric vehicles (all identical):
-vehicle battery capacity: units of energy available
-vehicle freight capacity: units available for cargo
-battery consumption rate: reduction of battery capacity when traveling one unit of distance
-inverse recharging rate:  units of time required to recharge one unit of energy
-average velocity:         assumed to be constant on all arcs, required to calculate the travel time from distance




