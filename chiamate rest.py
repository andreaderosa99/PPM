import requests as rq
import json

'''
LATO UTENTE: in pratica una volta fatta la richiesta viene generata l'immagine e una volta finito, l'immagine verrà salvata ovviamente
nella vps, perciò la richiesta al sito restituirà il nome dell'immagine, dopodiché farà un'altra richiesta per prelevare l'immagine
dalla vps e scaricarla dalla tua parte

poveva anche essere fatto restituendo l'immagine sottoforma di matrice, e poi trasformarla subito in immagine con cv2, senza ricorrere
alla seconda parte di codice dove si fa la richiesta per il download dell'immagine
'''

BASE_URL = 'http://solaris.micc.unifi.it/andreaderosa'
SUBFOLDER='/image/'

TARGET_TEXT="woman with long hair and crossed hand by leonardo da vinci" #descrizione immagine
USER_TEXT="with a mountain as background" #input utente
PORTRAIT_NAME="gioconda" #nome opera, che mi serve per aprire la cartella del finetuning

payload = {'prompt':USER_TEXT, 'portrait_name':PORTRAIT_NAME, 'target_text':TARGET_TEXT}
response = rq.get(BASE_URL, params=payload)

img_name=response.text

url=BASE_URL+SUBFOLDER+img_name
response = rq.get(url)
if response.status_code == 200:
    with open(img_name, 'wb') as f:
        f.write(response.content)
        


'''
LATO ADMIN: 
se su pycharm da errore import cv2, vai su settings->python interpreter -> installa opencv-python
cv2 mi serve per trasformare l'immagine che hai e carichi in una matrice. poi da matrice lo ritrasformo in immagine sulla vps
'''

BASE_URL = 'http://solaris.micc.unifi.it/andreaderosa'

PORTRAIT_NAME="gioconda" #nome opera
DESCRIPTION="woman with long hair and crossed hand by leonardo da vinci" #descrizione immagine che dovrà dare l'admin
IMAGE=cv2.imread('/directory/gioconda.png')#file immagine

payload = {'portrait_name':PORTRAIT_NAME, 'description':DESCRIPTION, 'image':IMAGE}
response = rq.get(BASE_URL, params=payload)

img_name=response.text