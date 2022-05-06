#!/usr/bin/env python3

import requests
import json
import rospy
import time
import ast
from std_msgs.msg import Bool
from geometry_msgs.msg import PoseStamped, Pose
from sensor_msgs.msg import ChannelFloat32
from ur_speed_control.msg import robot_status
from ur_speed_control.srv import command_gripper
import rospkg

rospack = rospkg.RosPack()
package_path = rospack.get_path('alexa_conversation')

##########TO_DO_LIST##########
#*Usare il codice fatto da Davide per il Goal Reached (creare subscriber)
#
#*Idem per settare l'epsilon (però uso un service)
# 
#*Capire perchè non funziona il codice per il protective stop (ultima cosa)
#
##############################

# from std_msgs.msg import String

rospy.init_node('Alexa_Conversation')           #Può dare qualche errore se lancio da terminale VS Code (anche la linea sotto)
rate = rospy.Rate(1000) # 1000hz        

actual_pose = PoseStamped()
tf_transformation = Pose()

pose_received = False
tf_received = False
PSstatus_received = False
goal_received = False
is_goal_reached = False

#Questo talker si può rimuovere?
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

def protective_stop_callback(data):
    global PSstatus_received
    if data.safety_mode == 3:
        PSstatus_received = True

def reached_goal(data):
    global is_goal_reached
    global goal_received
    is_goal_reached = data.data
    goal_received = True

watch_pub = rospy.Publisher('GearSDataVibration', ChannelFloat32, queue_size=1)    
UR_pub = rospy.Publisher('des_pose', PoseStamped, queue_size=1)

rospy.Subscriber("/act_pose", PoseStamped, actual_pose_callback)
rospy.Subscriber("/tf_URBase_RightWrist", Pose, tf_callback)
rospy.Subscriber("/ur_rtde/safety_status", robot_status, protective_stop_callback)
rospy.Subscriber("/cartesian_controller/trajectory_completed", Bool, reached_goal)

gripper_client = rospy.ServiceProxy('/ur_rtde/onrobot_gripper_control', command_gripper)
FAST=False
SLOW=True
OPEN=False
CLOSE=True

rospy.sleep(2)

while (pose_received == False or tf_received == False):
    rospy.logwarn_throttle(5,'Wait for Callbacks')

#Legge il JSON ogni tot millisecondi e vede se ci sono variazioni sul task selected
def TASK_Selector ():
    
    #Legge da json
    DBjson = DB_Reader()

    global PSstatus
	#DBjson['Robot']['Status']['Protective_Stop'] = PSstatus

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

        if (DBjson['Tasks']['Handover']['Is_Target_Taken'] == False):       #Oggetto non ancora preso 
            #ActPos = eval(DBjson['Robot']['Positions']['Current'])
            if (DBjson['Tasks']['Handover']['GoingUP'] == False):           #Non sono ancora andato su
                if (DBjson['Robot']['Status']['Is_Working'] == False):
                    DBjson['Robot']['Positions']['Initial'] = DBjson['Robot']['Positions']['Current']
                    #upMove = 0.15
                    EEdestUP = eval(DBjson['Robot']['Positions']['Initial'])
                    #EEdestUP[2] = EEdestUP[2]+upMove
                    EEdestUP[2] = 0.65
                    DBjson['Robot']['Positions']['Destination'] = str(EEdestUP)
                    Move_UR(DBjson)
                    DBjson['Robot']['Status']['Is_Working'] = True
                else:
                    if (ReachedGoal() == True):                             #Sono arrivato su
                        print ("Sono andato su, ora vado a prendere l'oggetto")
                        DBjson['Tasks']['Handover']['GoingUP'] = True
                        DBjson['Robot']['Status']['Is_Working'] = False
            else:                                                           #Sono già su
                GrabbingOBJ = DBjson['Objects']['SelectedObject']      
                PositionOBJ = DBjson['Objects'][GrabbingOBJ]['GrabPosition']
                MultipleOBJ = DBjson['Objects'][GrabbingOBJ]['MultipleObj']
                MissingOBJ = DBjson['Objects'][GrabbingOBJ]['IsTaken']
                if (DBjson['Robot']['Status']['Is_Working'] == False):
                    DBjson['Robot']['Positions']['Destination'] = PositionOBJ    #Devo dargli la posizione dell'oggetto
                    Move_UR(DBjson)
                    DBjson['Robot']['Status']['Is_Working'] = True
                else:
                    if (ReachedGoal() == True):
                        DBjson['Tasks']['Handover']['GoingUP'] = False
                        DBjson['Robot']['Status']['Is_Working'] = False
                        if (MultipleOBJ == True):
                            DBjson['Smartwatch']['SelectedP'] = 1                       #Pattern 1 Orologio
                            DBjson['Smartwatch']['Is_working'] = True
                            Vibrate_Watch (DBjson)
                            DBjson['Robot']['Status']['Task_Selected'] = 102            #Oggetto multiplo
                        else:
                            if (MissingOBJ == True):
                                DBjson['Smartwatch']['SelectedP'] = 1                       #Pattern 1 Orologio
                                DBjson['Smartwatch']['Is_working'] = True
                                Vibrate_Watch (DBjson)
                                DBjson['Robot']['Status']['Task_Selected'] = 103            #Oggetto mancante
                            else:
                                DBjson['Robot']['Status']['Is_Gripper_Closed'] = True      #Chiude il gripper
                                Gripper_IO(DBjson)
                                DBjson['Tasks']['Handover']['Is_Target_Taken'] = True
                                DBjson['Objects'][GrabbingOBJ]['IsTaken'] = True
        else:                                                               #Oggetto già preso
            if (DBjson['Tasks']['Handover']['GoingUP'] == False):           #Non sono ancora andato su
                if (DBjson['Robot']['Status']['Is_Working'] == False):
                    DBjson['Robot']['Positions']['Initial'] = DBjson['Robot']['Positions']['Current']
                    upMove = 0.15
                    EEdestUP = eval(DBjson['Robot']['Positions']['Initial'])
                    EEdestUP[2] = EEdestUP[2]+upMove
                    DBjson['Robot']['Positions']['Destination'] = str(EEdestUP)
                    Move_UR(DBjson)
                    DBjson['Robot']['Status']['Is_Working'] = True
                else:
                    if (ReachedGoal() == True):                             #Sono arrivato su
                        DBjson['Tasks']['Handover']['GoingUP'] = True
                        DBjson['Robot']['Status']['Is_Working'] = False
            else:                                                           #Sono già andato su
                if (DBjson['Robot']['Status']['Is_Working'] == False):
                    DBjson['Robot']['Positions']['Destination'] = Opti_read(DBjson)                #Gli invio la posizione del polso come destinazione
                    #DBjson['Robot']['Positions']['Destination'] = DBjson['Robot']['Positions']['Home']     #Per prova metto home
                    Move_UR(DBjson)                                                 #Muovo l'UR verso il polso
                    DBjson['Robot']['Status']['Is_Working'] = True
                else:
                    if (ReachedGoal() == True):
                        DBjson['Robot']['Status']['Is_Gripper_Closed'] = False      #Apre il gripper
                        Gripper_IO(DBjson)
                        DBjson['Tasks']['Handover']['Is_Target_Taken'] = False
                        DBjson['Smartwatch']['SelectedP'] = 3                       #Pattern 3 Orologio
                        DBjson['Smartwatch']['Is_working'] = True
                        Vibrate_Watch (DBjson)
                        DBjson['Robot']['Status']['Task_Selected'] = 99
                        DBjson['Tasks']['Handover']['GoingUP'] = False
                        DBjson['Robot']['Status']['Is_Working'] = False
                        DBjson['Tasks']['Handover']['GoingUP'] = False
          
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
    
    EEdestination = eval(DBjson['Robot']['Positions']['Destination'])
    
    EEdestination2 = PoseStamped()
    EEdestination2.pose.position.x = EEdestination[0]
    EEdestination2.pose.position.y = EEdestination[1]
    EEdestination2.pose.position.z = EEdestination[2]
    EEdestination2.pose.orientation.x = EEdestination[3]
    EEdestination2.pose.orientation.y = EEdestination[4]
    EEdestination2.pose.orientation.z = EEdestination[5]
    EEdestination2.pose.orientation.w = EEdestination[6]
    UR_pub.publish(EEdestination2)

    
    print (EEdestination2)
    #print (EEspeed)
    return ()
        
#Legge le coordinate della mano dall'optitrack 
def Opti_read (DBjson):

    global tf_transformation

    HandOverEEdestination = eval(DBjson['Robot']['Positions']['Destination'])

    tf_transformation.position.x =  tf_transformation.position.x + 0.1
    tf_transformation.position.z =  tf_transformation.position.z + 0.2
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

    rospy.wait_for_service('/ur_rtde/onrobot_gripper_control')

    if (DBjson['Robot']['Status']['Is_Gripper_Closed'] == True):
        service_resp = gripper_client(CLOSE, FAST)
    elif (DBjson['Robot']['Status']['Is_Gripper_Closed'] == False):
        service_resp = gripper_client(OPEN, FAST)
    return ()


#Invia il pattern allo smartwatch
#Per evitare che, ripetendo la funzione, lo smartwatch continui a vibrare costantemente, 
#posso mettere nel pattern un tempo di "riposo" molto lungo, che sarà una sorta di intervallo tra
#un pattern e l'altro.
def Vibrate_Watch (DBjson):
    if (DBjson['Smartwatch']['Is_working'] == True):
        EventType = DBjson['Smartwatch']['SelectedP']
        viber = ChannelFloat32()
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

    return()

def ReachedGoal ():
    #Questa funzione controlla se la posizione attuale è vicina alla posizione finale
    
    global is_goal_reached
    return is_goal_reached
   

def Vectorizer (StringVector):
    Vectorized = eval(StringVector)
    return Vectorized


if __name__ == '__main__':

    while not rospy.is_shutdown():

        TASK_Selector()
        time.sleep (1)
        #rate.sleep()