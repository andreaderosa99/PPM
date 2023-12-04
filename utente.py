from flask import Flask,request
import redis
from rq import Queue
import json,requests
import cv2,time
import matplotlib.pyplot as plt
from datetime import datetime

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, DDIMScheduler
from IPython.display import display


app = Flask(__name__)
r=redis.Redis()
q=Queue(connection=r)

image_with_time_string=""

def background_task(prompt,directory,target_text):

  model_path='path'+directory

  scheduler = DDIMScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear", clip_sample=False,
                            set_alpha_to_one=False)
  pipe = StableDiffusionPipeline.from_pretrained(model_path, scheduler=scheduler, torch_dtype=torch.float16).to("cuda")
  target_embeddings = torch.load(os.path.join(model_path, "target_embeddings.pt")).to("cuda")
  optimized_embeddings = torch.load(os.path.join(model_path, "optimized_embeddings.pt")).to("cuda")
  g_cuda = None

  g_cuda = torch.Generator(device='cuda')
  seed = -1
  g_cuda.manual_seed(seed)

  num_samples = 1
  guidance_scale = 5
  num_inference_steps = 100
  height = 512
  width = 512

  pipe.safety_checker = None
  pipe.requires_safety_checker = False

  with autocast("cuda"), torch.inference_mode():
    images = pipe(
      target_text + " " + prompt,
      height=height,
      width=width,
      num_images_per_prompt=num_samples,
      num_inference_steps=num_inference_steps,
      guidance_scale=guidance_scale,
      generator=g_cuda
    ).images

  image_with_time_string=datetime.now().strftime('%Y-%m-%d %H:%M:%S')+".jpg"
  #aggiungo la data con i secondi in modo che il nome dell'immagine generata sia univoco

  plt.imshow(images[0])
  plt.axis("off")
  plt.savefig(image_with_time_string)

  return


@app.route('/', methods=['GET', 'POST'])
def handle_request():

  prompt=str(request.args.get('prompt')) #?prompt=
  directory=str(request.args.get('directory'))
  target_text=str(request.args.get('target_text'))

  if request.args.get("prompt"):
    job = q.enqueue(background_task, request.args.get("prompt"), request.args.get("directory"),request.args.get("target_text"))

    #finché non è stata creata l'immagine rimane in attesa nella coda
    while (image_with_time_string==""):
      time.sleep(3)

  #ritorna il nome dell'immagine, che poi verrà scaricata tramite la chiamata rest
  return time_string


if __name__ == '__main__':
    app.run()