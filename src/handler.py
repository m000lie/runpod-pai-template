""" Example handler file. """

import runpod
from inference import Inference

# If your handler runs inference on a model, load the model here.
# You will want models to be loaded into memory before starting serverless.


def handler(job):
    """Handler function that will be used to process jobs."""
    text = job["input"]  # dictionary containing prompt and voice name
    """
    {
        "id": "A_RANDOM_JOB_IDENTIFIER",
        "input": { "prompt": "value", "voice": "trump" }
    }
    """

    endpoint = "https://www.mooolie.com/handler.php"
    # create new instance to run inference
    infer = Inference(text["prompt"], job["id"], endpoint)
   
    load = infer.load_model(text["voice"])
    
    if load == "Model Loaded!":
        print(infer.run_tts(f"voices/{text['voice']}/{text['voice']}-reference.wav"))
        infer.upload_audio()
    return f"Hello"


runpod.serverless.start({"handler": handler})
