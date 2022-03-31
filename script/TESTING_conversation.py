#!/usr/bin/env python3

import requests
import json
import rospy
import time
import ast
from geometry_msgs.msg import PoseStamped, Pose
from sensor_msgs.msg import ChannelFloat32
import rospkg

rospack = rospkg.RosPack()
package_path = rospack.get_path('alexa_conversation')

#Per l'UR10e (guarda anche link seguenti)
# https://sdurobotics.gitlab.io/ur_rtde/examples/examples.html
# https://sdurobotics.gitlab.io/ur_rtde/api/api.html#rtde-receive-interface-api
#import rtde_control     #ModuleNotFoundError: No module named 'rtde_control'
#import rtde_receive     #ModuleNotFoundError: No module named 'rtde_receive'

# from std_msgs.msg import String

rospy.init_node('Alexa_Conversation')           #Può dare qualche errore se lancio da terminale VS Code (anche la linea sotto)
rate = rospy.Rate(1000) # 1000hz        

actual_pose = PoseStamped()
tf_transformation = Pose()

pose_received = False
tf_received = False


def talker():
    hello_str = "hello world %s" % rospy.get_time()
    rospy.loginfo(hello_str)
    pub.publish(hello_str)

def actual_pose_callback(data):
    
    global actual_pose
    global pose_received
    actual_pose = data
    pose_received = True

def tf_callback(data):
    
    global tf_transformation
    global tf_received
    tf_transformation = data
    tf_received = True

watch_pub = rospy.Publisher('GearSDataVibration', ChannelFloat32, queue_size=1)    
UR_pub = rospy.Publisher('des_pose', PoseStamped, queue_size=1)

rospy.Subscriber("/act_pose", PoseStamped, actual_pose_callback)
rospy.Subscriber("/tf_URBase_RightWrist", Pose, tf_callback)
rospy.sleep(2)

while (pose_received == False or tf_received == False):
    rospy.logwarn_throttle(5,'Wait for Calbacks')

#Legge il JSON ogni tot millisecondi e vede se ci sono variazioni sul task selected
def TASK_Selector ():
    
    #Legge da json
    DBjson = DB_Reader()

    if (DBjson['Robot']['Status']['Protective_Stop'] == True):
        DBjson['Robot']['Status']['Task_Selected'] = 101    #Se sono in protective stop, mi manda nello stato 101
    
    task = DBjson['Robot']['Status']['Task_Selected']       #Il Task_Selected lo cambio da server

    if (task == 0):
        print ("WhatHappenedAPI")   #Restituisce il JSON aggiornato (gestire da server?)
        #setta a false lo "is_working" dello smartwatch e a "0" il pattern
        DBjson['Smartwatch']['Is_working'] = False
        DBjson['Smartwatch']['SelectedP'] = 0
    
    elif (task == 1):
        print ("Handover_API")
        
        EEposition = Read_UR_Position (DBjson)                              #Aggiorno la posizione attuale sul Database
        DBjson['Robot']['Positions']['Current'] = EEposition 

        #Ho già preso l'oggetto?
        if (DBjson['Tasks']['Handover']['Is_Target_Taken'] == False):       #Oggetto non ancora preso
            GrabbingOBJ = DBjson['Objects']['SelectedObject']      
            PositionOBJ = DBjson['Objects'][GrabbingOBJ]['GrabPosition']
            MultipleOBJ = DBjson['Objects'][GrabbingOBJ]['MultipleObj']
            IsTakenOBJ = DBjson['Objects'][GrabbingOBJ]['IsTaken']
            DBjson['Robot']['Positions']['Destination'] = PositionOBJ    #Devo dargli la posizione dell'oggetto
            #Settare la velocità
            #Settare l'Epsilon
            Move_UR(DBjson)
            if (ReachedGoal(DBjson) == True):
                if (MultipleOBJ == True):
                    DBjson['Smartwatch']['SelectedP'] = 1                       #Pattern 1 Orologio
                    DBjson['Smartwatch']['Is_working'] = True
                    Vibrate_Watch (DBjson)
                    DBjson['Robot']['Status']['Task_Selected'] = 102            #Oggetto multiplo
                else:
                    if (IsTakenOBJ == True):
                        DBjson['Smartwatch']['SelectedP'] = 1                       #Pattern 1 Orologio
                        DBjson['Smartwatch']['Is_working'] = True
                        Vibrate_Watch (DBjson)
                        DBjson['Robot']['Status']['Task_Selected'] = 103            #Oggetto mancante
                    else:
                        DBjson['Robot']['Status']['Is_Gripper_Closed'] = True      #Chiude il gripper
                        Gripper_IO(DBjson)
                        DBjson['Tasks']['Handover']['Is_Target_Taken'] = True
        else:                                                               #Oggetto già preso
            
            #Prima porto l'UR su di 20cm 

            DBjson['Robot']['Positions']['Destination'] = Opti_read(DBjson)                #Gli invio la posizione del polso come destinazione
            #Settare la velocità
            #Settare l'Epsilon
            Move_UR(DBjson)                                                 #Muovo l'UR verso il polso

            if (ReachedGoal(DBjson) == True):
                #DBjson['Robot']['Positions']['Destination'] = DBjson['Robot']['Positions']['Current']
                #Move_UR(DBjson)
                DBjson['Robot']['Status']['Is_Gripper_Closed'] = False      #Apre il gripper
                Gripper_IO(DBjson)
                DBjson['Tasks']['Handover']['Is_Target_Taken'] = False
                DBjson['Smartwatch']['SelectedP'] = 3                       #Pattern 3 Orologio
                DBjson['Smartwatch']['Is_working'] = True
                Vibrate_Watch (DBjson)
                DBjson['Robot']['Status']['Task_Selected'] = 99
          
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
            DBjson['Smartwatch']['Is_working'] = True
            DBjson['Smartwatch']['SelectedP'] = 3
            DBjson['Smartwatch']['Is_working'] = True
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
    DBjson = json.load(open(package_path + '/script/' + 'database.json'))   #Creo la variabile leggendo il json
    return(DBjson)                              #Restituisce la variabile creata

#Aggiorna il database - POST REQUEST
#(Anche qui in realtà posso non usare POST REQUEST e lavoro in locale)
def DB_Updater (UpdatingJSON):
    with open(package_path + '/script/' + "database.json", "w") as outfile:
        json.dump(UpdatingJSON, outfile, indent=4)
        UpdatedJSON = UpdatingJSON
    return(UpdatedJSON)


#Legge la posizione dell'end effector del robot 
def Read_UR_Position (DBjson):

    global actual_pose
    pos = [actual_pose.pose.position.x, 
           actual_pose.pose.position.y,
           actual_pose.pose.position.z, 
           actual_pose.pose.orientation.x,
           actual_pose.pose.orientation.y,
           actual_pose.pose.orientation.z,
           actual_pose.pose.orientation.w]


    DBjson['Robot']['Positions']['Current'] = str(pos)     #ATTENZIONE! Non converte il vettore in stringa ma solo quello che c'è dentro!

    EEposition = DBjson['Robot']['Positions']['Current']
    
    #EEposition = getActualTCPPose() #return = coordinate cartesiane del tool
    # (x,y,z,rx,ry,rz), where rx, ry and rz is a rotation vector representation of the tool orientation 
    return (EEposition)

#Invia le coordinate al robot
def Move_UR (DBjson):
    
    if (DBjson['Tasks']['Handover']['GoingUP'] == True):
        EEactual = eval (DBjson['Robot']['Positions']['Current'])
        EEactual[2] = EEactual[2]+0.2       #Prima lo sposta di 20 cm in alto
        EEdestination = EEactual
        DBjson['Tasks']['Handover']['GoingUP'] = False
    else:
        EEdestination = eval(DBjson['Robot']['Positions']['Destination'])
    
    #EEspeed = DBjson['Robot']['Positions']['Speed']
    EEdestination2 = PoseStamped()
    EEdestination2.pose.position.x = EEdestination[0]
    EEdestination2.pose.position.y = EEdestination[1]
    EEdestination2.pose.position.z = EEdestination[2]
    EEdestination2.pose.orientation.x = EEdestination[3]
    EEdestination2.pose.orientation.y = EEdestination[4]
    EEdestination2.pose.orientation.z = EEdestination[5]
    EEdestination2.pose.orientation.w = EEdestination[6]
    UR_pub.publish(EEdestination2)
    print (EEdestination)
    #print (EEspeed)
    return ()
        
#Legge le coordinate della mano dall'optitrack 
def Opti_read (DBjson):

    global tf_transformation

    HandOverEEdestination = eval(DBjson['Robot']['Positions']['Destination'])

    tf_transformation.orientation.x = HandOverEEdestination[3]
    tf_transformation.orientation.y = HandOverEEdestination[4]
    tf_transformation.orientation.z = HandOverEEdestination[5]
    tf_transformation.orientation.w = HandOverEEdestination[6]

    transVett = [tf_transformation.position.x,
                 tf_transformation.position.y,
                 tf_transformation.position.z,
                 tf_transformation.orientation.x,
                 tf_transformation.orientation.y,
                 tf_transformation.orientation.z,
                 tf_transformation.orientation.w]

    HandPosition = str (transVett)
    
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
    if (DBjson['Smartwatch']['Is_working'] == True):
        EventType = DBjson['Smartwatch']['SelectedP']
        viber = ChannelFloat32()
        #viber.values = [2000,500,1000,500,2000]         #QUESTO POI VA TOLTO - SOLO PER TEST!
        if (EventType == 1):
            print (DBjson['Smartwatch']['Pattern']['P01'])
            viber.values = eval(DBjson['Smartwatch']['Pattern']['P01'])
        elif (EventType == 2):
            print (DBjson['Smartwatch']['Pattern']['P02'])
            viber.values = eval(DBjson['Smartwatch']['Pattern']['P02'])
        elif (EventType == 3):
            print (DBjson['Smartwatch']['Pattern']['P03'])
            viber.values = eval(DBjson['Smartwatch']['Pattern']['P03'])
        else:
            print ("Error! This patter does not exist.")
        
        watch_pub.publish(viber)
        DBjson['Smartwatch']['Is_working'] = False

    #Invece dei print ci metterò i publisher
    return()

def ReachedGoal (DBjson):
    #Questa funzione controlla se la posizione attuale è vicina alla posizione finale
    #if (EEposition - DBjson['Robot']['Positions']['Destination'] < 1):

    CurrP = eval (DBjson['Robot']['Positions']['Current'])
    TargP = eval (DBjson['Robot']['Positions']['Destination'])
    eps = DBjson['Robot']['Positions']['Epsilon']     #DA DEFINIRE MEGLIO, NON SO SE E' UN VALORE SENSATO
    
    Delta = [0, 0, 0]
    Delta[0] = abs(TargP[0] - CurrP[0])
    Delta[1] = abs(TargP[1] - CurrP[1])
    Delta[2] = abs(TargP[2] - CurrP[2])
    deltaMax = max(Delta)

    if (deltaMax < eps):
        
        return True
    else:
        return False

    """ deltaP = input ('Posizione raggiunta: Delta = ')
    delta2 = int(deltaP)
    if (delta2 < 2):
        return True
    else:
        return False """

def Vectorizer (StringVector):
    Vectorized = eval(StringVector)
    return Vectorized


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