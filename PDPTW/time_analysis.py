import pandas as pd

def ifRepair(x):
    if 'Insertion' in x:
        return 'Insertion'
    elif 'Removal' in x:
        return 'Removal'
    else:
        return x

data = pd.read_csv('time_output.csv')
data['method'] = data['func_name'].apply(ifRepair)
repair = data[data['method'] == 'Insertion']
destroy = data[data['method'] == 'Removal']
print('repair')
print(repair.iloc[:,1].sum())
print('destroy')
print(destroy.iloc[:,1].sum())
