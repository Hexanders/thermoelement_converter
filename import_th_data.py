import _pickle as pickle
import pandas as pd
from scipy.interpolate import interp1d 
import matplotlib.pyplot as plt
from numpy import arange, loadtxt
path = 'Temperatureichung_Manipulator_1.csv'
# data = pd.read_csv('Temperatureichung_Manipulator_1.csv', delimiter = '\t')
# x = data[data.columns[0]]
# y = data[data.columns[1]] 
# plot = data.plot(x= 0, y= 1,style=['o','rx'])

data = loadtxt(path, skiprows =1)
x = data[:,0]
y = data[:,1]
xint = arange(0.04,20.92, 0.01)
yint = interp1d(x,y)
info = 'Temperature data (mv vs C°) of the manipulator of deep temperature STM. Measured in saturation in vacuum but at room temperature.'
# print(x,y)
print(xint,yint(xint))
print(x.min(),x.max())
plt.scatter(xint,yint(xint), s =2)
plt.scatter(x,y, s =1 , alpha = 0.5)
# with open(r"interpolated_data/tu-do-mani.pkl", "wb") as output_file:
#     pickle.dump([info,yint], output_file)
plt.show()
