#!/usr/bin/env python3

import requests
# import rospy
# from std_msgs.msg import String

def talker():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)

if __name__ == '__main__':

    
    
    #*****___INIZIO TEST PER HTTP___*****        
    #r =requests.get('https://httpbin.org/get')            #Se faccio print(r), mi restituisce <Response [200]>
    #testo = r.headers
    #print('Ecco quello che ho letto:',testo)
    #ploads = {'things':2,'total':25}                      #Se uso questo "ploads" mi aggiunge della roba nel campo "args:"
    #r = requests.get('https://httpbin.org/get',params=ploads)
    #print(r.text)                                         #Questo restituisce tutto quello che vedo nella pagina selezionata (è formattata in JSON)
    #print(r.url)                                          #Questo restituisce l'url 
    #print(r.json())                                       #Questo mi restituisce un Python dictionary dalla JSON response ottenuta dal sito 'httpbin'

    #*****___Converting JSON to Python dictionary and storing in a variable___*****

    print('Il codice sta funzionando. Inizio.')
    pload = {'username':'UR10','pass':'Python'}                  #Definisco il payload che posto 
    headers2 = {'Content-Type': 'application/json'}
    import json

    #r = requests.post('http://localhost:5000/',data = json.dumps(pload), headers = headers2)      #Posto il pload definito prima all'http scelto
    #print (r.headers)
    #r_dictionary = r.json()                                         #Creo la variabile r_dictionary e gli associo quello che leggo da r (convertito da json a dictionary)
    #print(r_dictionary['form']['password'])                                     #Stampo il contenuto di r_dictionary con la chiave "form"
    
    rw = requests.get('http://localhost:5000')            
    #rw_dict = rw.json()
    #print (rw.text)
    #numeroIdpass = input('Which user you need? ')
    #numeroId = int (numeroIdpass)-1
    #print ('Your user is', rw_dict['data'][numeroId]['first_name'], rw_dict['data'][numeroId]['last_name'])

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
#Funziona, ma "true/false" non li vede se li metto come booleani (senza apici)
#In ogni caso salva un JSON, non male!
#Devo provare a vedere se riesco, come in JS, a usare come "data" di 
#esempio il "database.json" e a modificarne un campo.