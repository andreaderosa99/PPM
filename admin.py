from flask import Flask,request
import redis
from rq import Queue
import json,requests
import cv2,os

#Codice per la generazione dei modelli di finetuning

app = Flask(__name__)
r=redis.Redis()
q=Queue(connection=r)

HUGGINGFACE_TOKEN = "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"
MODEL_NAME = "CompVis/stable-diffusion-v1-4"

def background_task(portrait_name,description,image):
    #image è l'immagine sottoforma di matrice, cv2.imwrite() serve per portarlo da matrice a file per poi darlo all'algoritmo

    OUTPUT_DIR="directory"

    filename=portrait_name+".jpg"
    im=cv2.imwrite(filename, image)

    INPUT_IMAGE="directory"+im

    command = 'python3 accelerate launch train_imagic.py --pretrained_model_name_or_path=$MODEL_NAME --output_dir=$OUTPUT_DIR --input_image=$INPUT_IMAGE --target_text="{TARGET_TEXT}" --seed=3434554 --resolution=512 --mixed_precision="fp16" --use_8bit_adam --gradient_accumulation_steps=1 --emb_learning_rate=1e-3 --learning_rate=1e-6 --emb_train_steps=500 --max_train_steps=1000'
    command = command.replace('MODEL_NAME', MODEL_NAME)
    command = command.replace('OUTPUT_DIR', OUTPUT_DIR)
    command = command.replace('INPUT_IMAGE', INPUT_IMAGE)
    command = command.replace('TARGET_TEXT', description)

    os.system(command)

    return



@app.route('/', methods=['GET', 'POST'])
def handle_request():

    portrait_name = str(request.args.get('portrait_name'))
    description = str(request.args.get('description'))
    image = str(request.args.get('image'))

    if request.args.get("portrait_name"):
        job = q.enqueue(background_task,request.args.get("portrait_name"), request.args.get("description"),request.args.get("image"))

        return "Richiesta messa in coda, lunghezza coda: "+len(q)

    else: return "Errore, riprovare"


if __name__ == '__main__':
    app.run()