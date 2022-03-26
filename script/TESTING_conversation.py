#!/usr/bin/env python3

import requests
import json
import rospy
import time
import ast
#Per l'UR10e (guarda anche link seguenti)
# https://sdurobotics.gitlab.io/ur_rtde/examples/examples.html
# https://sdurobotics.gitlab.io/ur_rtde/api/api.html#rtde-receive-interface-api
#import rtde_control     #ModuleNotFoundError: No module named 'rtde_control'
#import rtde_receive     #ModuleNotFoundError: No module named 'rtde_receive'

# from std_msgs.msg import String

def talker():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)

#Legge il JSON ogni tot millisecondi e vede se ci sono variazioni sul task selected
def TASK_Selector ():
    
    #Legge da json
    DBjson = DB_Reader()

    if (DBjson['Robot']['Status']['Protective_Stop'] == True):
        DBjson['Robot']['Status']['Task_Selected'] = 101    #Se sono in protective stop, mi manda nello stato 101
    
    task = DBjson['Robot']['Status']['Task_Selected']       #Il Task_Selected devo cambiarlo da server

    if (task == 0):
        print ("WhatHappenedAPI")   #Restituisce il JSON aggiornato (gestire da server?)
        #setta a false lo "is_working" dello smartwatch e a "0" il pattern
        DBjson['Smartwatch']['Is_working'] == False
        DBjson['Smartwatch']['SelectedP'] = 0
    
    elif (task == 1):
        print ("Handover_API")
        # 0) Prende i parametri che gli servono dal DB
        #       --> Presi dal DBjson
        # 1) Invia al robot la posizione finale e la velocità richieste
        # - ATTENZIONE! Posizione e velocità devo inviarle una volta sola.
        # - Per risolvere questo problema posso usare un while o un if
        if (DBjson['Robot']['Status']['Is_Working'] == False):
            Move_UR(DBjson)
            DBjson['Robot']['Status']['Is_Working'] == True        
        # 2) Nel mentre, continua ad aggiornare la posizione attuale del robot sul DB
        EEposition = Read_UR_Position (DBjson)
        DBjson['Robot']['Positions']['Current'] = EEposition #Crea problemi!! Lo vede come una stringa
        # 3) Con un "if", controlla quando il robot raggiunge la posizione desiderata.
        #    O più semplicemente, quando il robot si ferma perchè ha raggiunto la posizione
        if (DBjson['Tasks']['Handover']['Is_Target_Taken'] == False):    #Se l'oggetto non è preso, va a prenderlo
            if (ReachedGoal (DBjson) == True):      #Definire un intorno (come?)
                DBjson['Objects']['SelectedObject'] = DBjson['Objects']['Wrench']   #Come test metto wrench
                if (DBjson['Objects']['SelectedObject']['MultipleObj'] == True):     #Invece che selectedObject potrei usare Handover.Target
                    # SE MultipleObj == true 
                    # 3.2) Vibrazione orologio e fermo tutto.
                    # 3.3) Scrivo su WhatHappened che c'è un oggetto multiplo
                    DBjson['Smartwatch']['SelectedP'] = 1
                    Vibrate_Watch(DBjson)
                    DBjson['Tasks']['WhatHappened']['EventDescription'] = "Multiple object detected"
                    task = 102       #Devo impostare qualcosa di diverso, in modo che alla seconda lettura non faccia nulla
                else:
                    if (DBjson['Objects']['SelectedObject']['IsTaken'] == True):
                        # 3.2) Vibrazione orologio e fermo tutto.
                        DBjson['Smartwatch']['SelectedP'] = 1
                        Vibrate_Watch(DBjson)
                        # 3.3) Scrivo su WhatHappened che l'oggetto non c'è
                        DBjson['Tasks']['WhatHappened']['EventDescription'] = "Missing object"
                        task = 103
                    else: 
                        # SE MultipleObj == false e (dopo) IsTaken == false:
                        # 3.2) Chiudo il gripper e afferro l'oggetto
                        DBjson['Robot']['Status']['Is_Gripper_Closed'] == True
                        Gripper_IO (DBjson)
                        DBjson['Tasks']['Handover']['Is_Target_Taken'] == True
                        # 3.3) Modifico la posizione finale con quella letta dall'optitrack
                        DBjson['Robot']['Positions']['Destination'] = Opti_read()
                        # 4) A questo punto, il robot riparte per portare l'oggetto                
        
        elif (DBjson['Tasks']['Handover']['Is_Target_Taken'] == True):   #Oggetto preso: lo porto all'utente
            #DA SETTARE IL TARGET CON NUOVA ARCHITETTURA (wrist tracking)
            Move_UR (DBjson)
            # 5) IF (posizione finale raggiunta) 
            if (EEposition - DBjson['Robot']['Positions']['Destination'] < 1):
                # 5.1) Vibrazione orologio 
                DBjson['Smartwatch']['SelectedP'] = 3
                Vibrate_Watch(DBjsons)
                # 5.2) Rilascio il gripper
                DBjson['Robot']['Status']['Is_Gripper_Closed'] == False
                Gripper_IO (DBjson)
          
    elif (task == 2):
        print ("Thirsty_API")
    elif (task == 3):
        print ("Assistant_API")
    elif (task == 4):
        print ("Reposition_API")
        # 0) Prende dal DB la posizione HOME
        HomePos = DBjson['Robot']['Positions']['Home']
        # 1) Invia al robot la posizione HOME come posizione finale
        if (DBjson['Robot']['Positions']['Destination'] != HomePos):
            DBjson['Robot']['Positions']['Destination'] = HomePos
            print (HomePos)
        # 2) Continua ad aggiornare la posizione del robot sul DB
        Read_UR_Position ()
        # 3) IF (posizione finale raggiunta) --> Invia il pattern sull'orologio.
        if (EEposition == HomePos and DBjson['Smartwatch']['Is_working'] == False):
            DBjson['Smartwatch']['Is_working'] == True
            DBjson['Smartwatch']['SelectedP'] = 3
            Vibrate_Watch(DBjson) 
        #DB_Updater(UpdatingJSON = DBjson) --> LO FA ALLA FINE
        
    elif (task == 5):
        print ("Still not implemented.")
    elif (task == 99):      #Task_Selected è impostato a 99 di default quando non succede nulla
        print ("No API selected")
    elif (task == 101):
        print ("PROTECTIVE STOP")
        #Da sistemare tutta la logica del protective stop
    elif (task == 102):
        print ("MULTIPLE OBJECT")
        #Da sistemare tutta la logica del protective stop
    elif (task == 103):
        print ("MISSING OBJECT")
        #Da sistemare tutta la logica del protective stop
    else:
        print ("ERROR: this API does not exist yet.")
    
    DB_Updater(DBjson)      #Lo deve fare ogni tot millisecondi, quindi ogni volta che parte sta funzione.

    return()

#*********************FUNZIONI UTILI***********************#


#Legge il database.json e assegnarlo ad una variabile - GET REQUEST
#(In realtà non uso la GET REQUEST perchè posso leggere in locale, se salvo anche da server)
def DB_Reader ():
    # import json --> Lo faccio già di sopra
    DBjson = json.load(open("database.json"))   #Creo la variabile leggendo il json
    return(DBjson)                              #Restituisce la variabile creata

#Aggiorna il database - POST REQUEST
#(Anche qui in realtà posso non usare POST REQUEST e lavoro in locale)
def DB_Updater (UpdatingJSON):
    with open("database.json", "w") as outfile:
        json.dump(UpdatingJSON, outfile, indent=4)
        UpdatedJSON = UpdatingJSON
    return(UpdatedJSON)        
    
#Legge la posizione dell'end effector del robot 
def Read_UR_Position (DBjson):

    Px = input ('Leggi x da UR: ')
    Py = input ('Leggi y da UR: ')
    Pz = input ('Leggi z da UR: ')
    Rx = input ('Leggi rx da UR: ')
    Ry = input ('Leggi ry da UR: ')
    Rz = input ('Leggi rz da UR: ')    

    DBjson['Robot']['Positions']['Current']['x'] = int (Px) 
    DBjson['Robot']['Positions']['Current']['y'] = int(Py) 
    DBjson['Robot']['Positions']['Current']['z'] = int (Pz) 
    DBjson['Robot']['Positions']['Current']['rx'] = int (Rx) 
    DBjson['Robot']['Positions']['Current']['ry'] = int (Ry) 
    DBjson['Robot']['Positions']['Current']['rz'] = int (Rz) 
    
    EEposition = DBjson['Robot']['Positions']['Current']
    
    #EEposition = getActualTCPPose() #return = coordinate cartesiane del tool
    # (x,y,z,rx,ry,rz), where rx, ry and rz is a rotation vector representation of the tool orientation 
    return (EEposition)

#Invia le coordinate al robot
def Move_UR (DBjson):
    EEdestination = DBjson['Robot']['Positions']['Destination']
    EEspeed = DBjson['Robot']['Positions']['Speed']
    print (EEdestination)
    print (EEspeed)
    return ()
        
#Legge le coordinate della mano dall'optitrack --> Cosa succede se la mano si sposta????
#Nel messaggio vocale di output potrei dire che io porto il tool dove ha la mano attualmente.
def Opti_read ():
    #Dall'optitrack mi arrivano la posizione della base riferita al world e
    #la posizione del wrist (sempre riferita al world).
    #Devo ottenere entrambe e calcolarmi la posizione del wrist 
    #riferita alla base, che è quella che darò all'UR10
    HandPosition = input('In realtà arriva da Optitrack: ')
    return(HandPosition)

def Gripper_IO (DBjson):
    if (DBjson['Robot']['Status']['Is_Gripper_Closed'] == True):
        print ("Invia al gripper il comando di chiudersi")
    elif (DBjson['Robot']['Status']['Is_Gripper_Closed'] == False):
        print ("Invia al gripper il comando di aprirsi")
    return ()

#Invia il pattern allo smartwatch
#Per evitare che, ripetendo la funzione, lo smartwatch continui a vibrare costantemente, 
#posso mettere nel pattern un tempo di "riposo" molto lungo, che sarà una sorta di intervallo tra
#un pattern e l'altro.
def Vibrate_Watch (DBjson):
    EventType = DBjson['Smartwatch']['SelectedP']
    if (EventType == 1):
        print (DBjson['Smartwatch']['Pattern']['P01'])
    elif (EventType == 2):
        print (DBjson['Smartwatch']['Pattern']['P02'])
    elif (EventType == 3):
        print (DBjson['Smartwatch']['Pattern']['P03'])
    else:
        print ("Error! This patter does not exist.")
    #Invece dei print ci metterò i publisher
    return()

def ReachedGoal (DBjson):
    #Questa funzione controlla se la posizione attuale è vicina alla posizione finale
    #if (EEposition - DBjson['Robot']['Positions']['Destination'] < 1):
    deltaP = input ('Posizione raggiunta: Delta = ')
    delta = int(deltaP)
    if (delta < 2):
        return True
    else:
        return False


#ALTRE UTILITY VECCHIE:

""" pload = {'username':'UR10','pass':'Python'}                  #Definisco il payload che posto 
headers2 = {'Content-Type': 'application/json'}
    
rw = requests.get('http://localhost:5000')      """

if __name__ == '__main__':

    #print('Il codice sta funzionando. Inizio.')
    #print('Il codice ha funzionato.')

    while not rospy.is_shutdown():

        TASK_Selector()
        time.sleep (1)
        #rate.sleep()