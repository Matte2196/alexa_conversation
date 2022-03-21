#!/usr/bin/env python3

import requests
# import rospy
# from std_msgs.msg import String

def talker():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)

if __name__ == '__main__':

    print('Il codice sta funzionando. Inizio.')
    pload = {'username':'UR10','pass':'Python'}                  #Definisco il payload che posto 
    headers2 = {'Content-Type': 'application/json'}
    import json

    rw = requests.get('http://localhost:5000')            

    print('Il codice ha funzionato.')

#**********TEST SCRITTURA JSON*************

    import json
    data = {"Robot": {      #In realtà devo importare "template.json" e modificare i parametri
        "Status": {
            "Is_Working": 'true',
            "Task_Selected": 0,
            "Protective_Stop": 'false',
            "Is_Gripper_Closed": 'false'
                }
        }
        }
    with open("WritingTEST_PY.json", "w") as outfile:
            json.dump(data, outfile)
