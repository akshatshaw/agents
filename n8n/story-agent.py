import streamlit as st
import requests
import uuid
import os
from datetime import datetime

# Constants
# WEBHOOK_URL = "https://akshatshaw.app.n8n.cloud/webhook-test/c5ce3d8c-8ffb-459b-8105-3946467ce1cd"
WEBHOOK_URL    =     "https://akshatshaw.app.n8n.cloud/webhook/c5ce3d8c-8ffb-459b-8105-3946467ce1cd"
BEARER_TOKEN = "admin123"

def generate_session_id():
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')
        
        if 'audio' in content_type or 'mp3' in content_type or 'wav' in content_type:
            return {"type": "audio", "content": response.content}
        else:
            try:
                return {"type": "text", "content": response.json()["output"]}
            except:
                return {"type": "audio", "content": response.content}
    else:
        return {"type": "text", "content": f"Error: {response.status_code} - {response.text}"}

def main():
    st.title("Chat with LLM")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()
    if "audio_counter" not in st.session_state:
        st.session_state.audio_counter = 0

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.write(message["content"])
            elif message["type"] == "audio":
                st.audio(message["content"])

    # User input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "type": "text", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Get LLM response
        llm_response = send_message_to_llm(st.session_state.session_id, user_input)

        # Add LLM response to chat history
        with st.chat_message("assistant"):
            if llm_response["type"] == "text":
                st.write(llm_response["content"])
                st.session_state.messages.append({
                    "role": "assistant", 
                    "type": "text", 
                    "content": llm_response["content"]
                })
            elif llm_response["type"] == "audio":
                # Try to display the audio directly
                try:
                    st.audio(llm_response["content"])
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "type": "audio", 
                        "content": llm_response["content"]
                    })
                except Exception as e:
                    # If direct display fails, save the audio file
                    st.session_state.audio_counter += 1
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_filename = f"audio_{timestamp}_{st.session_state.audio_counter}.mp3"
                    
                    # Create audio directory if it doesn't exist
                    os.makedirs("audio", exist_ok=True)
                    audio_path = os.path.join("audio", audio_filename)
                    
                    # Save the audio file
                    with open(audio_path, "wb") as f:
                        f.write(llm_response["content"])
                    
                    st.write(f"Audio saved to {audio_path}")
                    # Add a download button for the saved audio
                    with open(audio_path, "rb") as file:
                        btn = st.download_button(
                            label="Download Audio",
                            data=file,
                            file_name=audio_filename,
                            mime="audio/mp3"
                        )
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "type": "text", 
                        "content": f"Audio saved to {audio_path}"
                    })

if __name__ == "__main__":
    main()
