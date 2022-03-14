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

    pload = {'username':'UR10','pass':'NuovaPassword'}                  #Definisco il payload che posto 
    r = requests.post('http://localhost:5000/',data = pload)      #Posto il pload definito prima all'http scelto
    #r_dictionary = r.json()                                         #Creo la variabile r_dictionary e gli associo quello che leggo da r (convertito da json a dictionary)
    #print(r_dictionary['form']['password'])                                     #Stampo il contenuto di r_dictionary con la chiave "form"
    
    #rw = requests.get('http://localhost:8080')            #Leggo da ngrok (che devo attivare prima e inserire qui il giusto https) --> Per ora mi dà 502 Bad Gateway
    #rw_dict = rw.json()
    #numeroIdpass = input('Which user you need? ')
    #numeroId = int (numeroIdpass)-1
    #print ('Your user is', rw_dict['data'][numeroId]['first_name'], rw_dict['data'][numeroId]['last_name'])

    print('Il codice ha funzionato.')