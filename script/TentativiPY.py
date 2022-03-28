import requests
import json
import rospy
import time
import ast


if __name__ == '__main__':

    """ stringa = "[10, 20, 30]"
    Intero = eval(stringa)

    #print (stringa)
    print (Intero)
    tipo = type(Intero[1])
    print (tipo)
    DUE = Intero[1] + 1
    print (DUE)
    

    Px = input ('Leggi x da UR: ')
    Py = input ('Leggi y da UR: ')
    Pz = input ('Leggi z da UR: ')

    vecty = [Px, Py, Pz]

    DBjson = str(vecty)
    print (DBjson)
    NiceTRY = eval(DBjson)
    TRE = type (NiceTRY[2])
    print (TRE) """
    

"""     def DB_Reader ():
        DBjson = json.load(open("database.json"))   #Creo la variabile leggendo il json
        return(DBjson)                              #Restituisce la variabile creata

    JSON = DB_Reader()

    NUM = input ("EHI")
    #"Is_Working":false,
    #"Task_Selected":99,
    #"Protective_Stop":false,
    #"Is_Gripper_Closed":false
    Selected = JSON['Robot']['Status'][NUM]
    print (Selected) """

TargetPOS = [1,3,4,-62,7,1,9]
CurrentPOS = [2,5,6,13,7,22,22]
delta = 0

for i in range(7):
        diff = abs(TargetPOS[i] - CurrentPOS[i])
        print (diff)
        if (diff > delta):
            delta = diff
print ("MAX =", delta)

