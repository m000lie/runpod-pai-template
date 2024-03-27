import tempfile
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import requests 
import os


class Inference():
    def __init__(self, prompt, id, endpoint):
        self.prompt = prompt
        self.id = id
        self.endpoint = endpoint
        

    def clear_gpu_cache(self):
        # clear the GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def load_model(self, name):
        global XTTS_MODEL
        xtts_checkpoint = f"voices/{name}/{name}.pth"
        xtts_config = f"voices/{name}/config_{name}.json"
        xtts_vocab = f"voices/{name}/vocab_{name}.json"
        self.clear_gpu_cache()

        if not xtts_checkpoint or not xtts_config or not xtts_vocab:
            return "You need to run the previous steps or manually set the `XTTS checkpoint path`, `XTTS config path`, and `XTTS vocab path` fields !!"
        config = XttsConfig()
        config.load_json(xtts_config)
        XTTS_MODEL = Xtts.init_from_config(config)
        print("Loading XTTS model! ")
        XTTS_MODEL.load_checkpoint(config, checkpoint_path=xtts_checkpoint, vocab_path=xtts_vocab, use_deepspeed=False)
        if torch.cuda.is_available():
            XTTS_MODEL.cuda()

        print("Model Loaded!")
        return "Model Loaded!"

    def run_tts(self, speaker_audio_file): # takes id from text generation
        if XTTS_MODEL is None or not speaker_audio_file:
            return "You need to run the previous step to load the model !!", None, None

        gpt_cond_latent, speaker_embedding = XTTS_MODEL.get_conditioning_latents(audio_path=speaker_audio_file, gpt_cond_len=XTTS_MODEL.config.gpt_cond_len, max_ref_length=XTTS_MODEL.config.max_ref_len, sound_norm_refs=XTTS_MODEL.config.sound_norm_refs)
        out = XTTS_MODEL.inference(
            text=self.prompt,
            language='en',
            gpt_cond_latent=gpt_cond_latent,
            speaker_embedding=speaker_embedding,
            temperature=XTTS_MODEL.config.temperature, # Add custom parameters here
            length_penalty=XTTS_MODEL.config.length_penalty,
            repetition_penalty=XTTS_MODEL.config.repetition_penalty,
            top_k=XTTS_MODEL.config.top_k,
            top_p=XTTS_MODEL.config.top_p,
        )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as fp:
            out["wav"] = torch.tensor(out["wav"]).unsqueeze(0)
            out_path = f'outputs/{self.id}.wav'
            self.out_path = out_path
            if not os.path.exists('outputs'):
                os.makedirs('outputs')

            torchaudio.save(out_path, out["wav"], 24000)

        return "Speech generated !", out_path, speaker_audio_file
    

    def upload_audio(self):
        # URL of the server where you want to send the file
        url = self.endpoint  # Modify the path if needed, for example to '/upload'

        # Path to your .wav file
        file_path = self.out_path

        # Open the file in binary mode
        with open(file_path, 'rb') as f:
            # Define the request files dictionary
            files = {'file': (file_path, f, 'audio/wav')}
            
            # Send the POST request with the file
            response = requests.post(url, files=files)

        # Print the response from the server
        print(response.text)
