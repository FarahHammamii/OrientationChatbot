import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import streamlit as st
import os
import time
import speech_recognition as sr
import pyttsx3  


offload_folder = "./offload_folder"
os.makedirs(offload_folder, exist_ok=True)

# Initializing the text-generation pipeline 
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Loading tokenizer and model
try:
    tokenizer = AutoTokenizer.from_pretrained("saifalh/frenchOrientationModel")
    model = AutoModelForCausalLM.from_pretrained("saifalh/frenchOrientationModel", 
                                                torch_dtype=torch.float16 if device == "cuda" else torch.float32, 
                                                device_map="auto", 
                                                offload_folder=offload_folder)
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )
except Exception as e:
    print(f"Error loading model or tokenizer: {e}")

# Adding a logo in the sidebar
logo_path = "ORIENTAI.png"  
st.sidebar.image(logo_path, use_column_width=True)

# Checking with the animation
if 'animations_run' not in st.session_state:
    st.session_state.animations_run = False

if not st.session_state.animations_run:
    animated_text = """Bonjour ! Je suis ORIENTAI, votre assistant IA amical et compétent, créé pour vous aider dans une large gamme de 
    tâches et répondre à vos questions, en particulier dans l'orientation universitaire en Tunisie.
    Mon objectif est de vous assister de manière efficace et précise, afin que vous receviez les meilleures informations et le soutien le plus adapté possible."""

    placeholder = st.sidebar.empty()
    current_text = ""
    for line in animated_text.split('\n'):
        for char in line:
            current_text += char
            placeholder.text_area("", current_text, height=len(current_text)//2+1)
            time.sleep(0.05)
        current_text += "\n"


    for _ in range(20):
        st.sidebar.empty()

   

    # Animating
    title_text = "OREINTAI will assist you, So feel free to ask him"
    title_placeholder = st.empty()
    current_title = ""
    for char in title_text:
        current_title += char
        title_placeholder.title(current_title)
        time.sleep(0.05)


    st.session_state.animations_run = True
else:

    animated_text = """Bonjour ! Je suis ORIENTAI, votre assistant IA amical et compétent, créé pour vous aider dans une large gamme de tâches et répondre à vos questions, en particulier dans les domaines médical et pharmaceutique.
Mon objectif est de vous assister de manière efficace et précise, afin que vous receviez les meilleures informations et le soutien le plus adapté possible.."""
    st.sidebar.text_area("", animated_text, height=len(animated_text)//2+1)

    for _ in range(20):
        st.sidebar.empty()

    

    title_text = "ORIENTAI will assist you, So feel free to ask him"
    st.title(title_text)

# Main interaction loop
if "history" not in st.session_state:
    st.session_state.history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "response" not in st.session_state:
    st.session_state.response = ""

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Recording...")
        audio = recognizer.listen(source)
        st.write("Transcribing...")
        try:
            text = recognizer.recognize_google(audio, language="fr") 
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError:
            st.error("Sorry, there was an issue with the speech recognition service.")
            return ""

import pyttsx3
def text_to_speech(text):
    engine = pyttsx3.init()
    
    # choosing French interpretor
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'fr' in voice.languages or 'French' in voice.name:
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1) 
    engine.save_to_file(text, 'output.wav')
    engine.runAndWait()

# Handling the 'Record' button click
if st.button("Record"):
    st.session_state.user_input = transcribe_audio()

# Displayingthe text input field after transcribing
user_input = st.text_input("You:", key="user_input")

# Handling the 'Send' button click
if st.button("Send"):
    if user_input:
        st.session_state.history.append({"role": "user", "content": user_input})
        messages = [
            {"role": "system", "content": "I want a detailed response to the next questions, if the message is thanking or welcome or goodbye so give a clear and direct response."},
            {"role": "user", "content": user_input},
        ]

        try:
            prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            outputs = pipe(
                prompt, 
                max_new_tokens=100,
                do_sample=True, 
                temperature=0.01, 
                top_k=1, 
                top_p=0.1
            )

            response = outputs[0]["generated_text"].split("?")[1].strip()
            response_lines = response[19:]
            st.session_state.response = response_lines
            st.session_state.history.append({"role": "bot", "content": response_lines})
            
            # Convert response to audio
            text_to_speech(response_lines)
        except Exception as e:
            st.error(f"Error generating response: {e}")

# Displaying chat history
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.text_area("You:", value=msg["content"], height=50)
    else:
        st.text_area("Bot:", value=msg["content"], height=150)
        
        # Adding copy button
        st.button("Copy Response", key=f"copy_{msg['content']}", on_click=lambda text=msg['content']: st.write(f"Response copied: {text}"))
        
        # Adding audio play button
        st.audio("output.wav", format="audio/wav")
        
        # Adding regenerate button
        if st.button("Regenerate Response", key=f"regenerate_{msg['content']}"):
            # Regenerating the response
            st.session_state.user_input = user_input
            st.session_state.response = ""
            try:
                prompt = pipe.tokenizer.apply_chat_template([
                    {"role": "system", "content": "I want a detailed response to the next questions, if the message is thanking or welcome or goodbye so give a clear and direct response."},
                    {"role": "user", "content": st.session_state.user_input},
                ], tokenize=False, add_generation_prompt=True)
                outputs = pipe(
                    prompt, 
                    max_new_tokens=100,
                    do_sample=True, 
                    temperature=0.01, 
                    top_k=1, 
                    top_p=0.1
                )
                response = outputs[0]["generated_text"].split("?")[1].strip()
                response_lines = response[19:]
                st.session_state.response = response_lines
                st.session_state.history.append({"role": "bot", "content": response_lines})
                
                # Converting response to audio
                text_to_speech(response_lines)
            except Exception as e:
                st.error(f"Error generating response: {e}")
