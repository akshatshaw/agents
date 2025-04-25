import requests
import os
from dotenv import load_dotenv
import time
load_dotenv()
import boto3
VOICE_API = os.getenv("VOICE_API") 

AWS_KEY_ID = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ID = os.getenv("AWS_SECRET_KEY")

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key= AWS_SECRET_ID
)

def tts_tool(text: str)-> None:
    """
    Converts the given text to speech using the Dubverse TTS API and saves the output as a .wav file.
    Args:
        text (str): The text to convert to speech.
        output_filename (str): The name of the .wav file to save the audio output. Default is 'output.wav'.

    Returns:
        str: Path to the saved .wav file if successful, else raises an exception.
    """
    url = "https://audio.dubverse.ai/api/tts"
    payload = {
        "text": text,
        "speaker_no": 1252,
        "config": {
            "use_streaming_response": False,
        },
    }
    headers = {
        "X-API-KEY": VOICE_API,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    output_filename = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp3"
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        print("File saved!!")
        
        bucket_name = "story-agent"

        # Upload to S3
        s3_key = f"Dubverse/{output_filename}"
        s3.upload_file(output_filename, bucket_name, s3_key, ExtraArgs={'ACL': 'public-read'})

        # Make file public
        s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=s3_key)

        # Generate public URL
        url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        print("Public File URL:", url)
        return url
    else:
        print("Error!")
        

import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def text_to_speech_file(text: str) -> None:
    """
    Converts the given text to speech using the Dubverse TTS API and saves the output as a .wav file.
    Args:
        text (str): The text to convert to speech.
    Returns:
        str: Path to the saved .wav file if successful, else raises an exception.
    """
    response = client.text_to_speech.convert(
        voice_id="MF4J4IDTRo0AxOO4dpFR", 
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    # Generating a unique file name for the output MP3 file
    output_filename = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp3"

    # Writing the audio to a file
    with open(output_filename, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    bucket_name = "story-agent"

    # Upload to S3
    s3_key = f"ElevenLabs/{output_filename}"
    s3.upload_file(output_filename, bucket_name, s3_key)

    # Make file public
    s3.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=s3_key)

    # Generate public URL
    url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    print("Public File URL:", url)
    return url

    # Return the path of the saved audio file
    # return save_file_path
