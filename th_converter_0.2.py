from thermocouples_reference import thermocouples
from PySimpleGUI import Menu, Text, Exit, Input, InputCombo, Window, Column, Popup, Button, Frame, RELIEF_SUNKEN
from matplotlib.pyplot import plot, show, ion, draw, pause, legend, grid, xlabel, ylabel
from numpy import arange
import configparser, os
from _pickle import load
from scipy.optimize import newton

config = configparser.ConfigParser()
config.read_file(open('config/default.cfg'))

default_thType = config.get('DEFAULT','default_type')
types = config.get('DEFAULT','types').split(',')

menu_def = [['Help', 'About...'],]  
column1 = [[Text('mV'), Input(default_text = '1', do_not_clear=True, key = 'mV'), Button('Convert mV -> C°', bind_return_key = True)],\
            [Text('C°'), Input(default_text = '47', do_not_clear=True, key = 'Celsius'), Button('Convert C° -> mV')]]
layout = [[Menu(menu_def, )],
          [Text('Type'),InputCombo((types), auto_size_text =True, default_value = default_thType, key = 'th_type'), Text('Reference T[C°]'), Input(do_not_clear=True, key = 'Tref', default_text = '23'),],\
          [Column(column1)],\
          [Frame(layout=[      
              [Text('Min mV'),Input(default_text = '1',do_not_clear=True, key = 'mVxmin',size =(20,20)), Text('Max mV'),\
               Input(default_text = '5', do_not_clear=True, key = 'mVxmax',size =(20,20)),],\
              [Text('Step in mV'), Input(default_text = '1', do_not_clear=True, key = 'step', size =(17,20)),],\
              [Button('Plot', bind_return_key = True)]],\
                 title='Graph mV VS C°',title_color='blue', font=("Helvetica", 16),\
                 relief=RELIEF_SUNKEN, tooltip='Plots the mVs VS C°'),],
          [Exit()]]

window = Window('Convert mV <--> C°',return_keyboard_events=True).Layout(layout)     
th_type = None
externalDataTrigger = False

def externalData(mvValue, dataName, inverse = False):
    path = config.get('DEFAULT' , 'externalDataPath') + dataName + '.pkl'
    data = load( open( path, "rb" ) )
    if inverse:
        findeX = lambda x: data[1](x) - mvValue
        thInfo, thData = data[0], newton(findeX, 0.04)
    else:
        thInfo, thData = data[0], data[1](mvValue) 
    return thInfo, thData

while True:
    externalDataTrigger = False
    event, values = window.Read()
    try:
        th_type = thermocouples[values['th_type']]
    except:
        externalDataTrigger = True
        th_type = values['th_type']
    if event is None or event == 'Exit':
        break
    if event == 'About...':
        # print('Ok')
        Popup('Simple GUI for thermoelement converter\n\n GUI Autohor: Alexander Kononv\n 2018 \n Ther real work was done by User:Nanite @ wikipedia in thermocouples_reference.py\n https://pypi.python.org/pypi/thermocouples_reference')
    try:
        if event == 'Plot':
            ion()
            show()
            grid(True)
            xlabel('mV')
            ylabel('C°')
            x = []
            y = []
            for i in arange(float(values['mVxmin']),float(values['mVxmax']),float(values['step'])):
                x.append( i )
                if externalDataTrigger:
                    y.append(externalData(i, th_type)[1])
                else:
                    y.append( th_type.inverse_CmV( i, Tref=float( values['Tref'] ) ) )
            plot(x,y,'o-', linewidth=1, markersize=2.3, label = r'$T_{ref}$: '+values['Tref']+'C°'+' Typ: '+values['th_type'])
            legend()
            draw()
        if event == 'Convert mV -> C°':
            if externalDataTrigger:
                window.FindElement('Celsius').Update(externalData(float(values['mV']), th_type)[1])
            else:
                window.FindElement('Celsius').Update(th_type.inverse_CmV(float(values['mV']), Tref=float(values['Tref'])))
        elif event == 'Convert C° -> mV':
            if externalDataTrigger:
                window.FindElement('mV').Update(externalData(float(values['Celsius']), th_type, inverse =True)[1])
            else:
                window.FindElement('mV').Update(th_type.emf_mVC(float(values['Celsius']), Tref=float(values['Tref'])))
    except ValueError:
        Popup('Error','Please choose a suitable value. Only the numbers are allowed.\n Or maybe is the range of plot is aut of boundaries.',font=("Helvetica", 16))
    #print(event, values)
    #print(typeK.inverse_CmV(float(values['mV'])))

window.Close()
