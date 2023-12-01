from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import openai

app = Flask(__name__)
app.static_folder = 'static'
openai.api_key = "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"


@app.route("/")
def home():
    initialize_conversation() # Inititalize conversation with start of the script
    return render_template("index.html")



# Function to query chatbot with user input
@app.route("/get")
def get_bot_response():
    """Flask function to query chatbot with user input. The function returns the chatbot's response.

    Returns:
        output_text: Text output from chatbot
    """
    
    ## Automatic update of Bot's knowledge:
    if convo_count == 0:
        update_bot()
        
    userText = request.args.get('msg')
    update_convo(userText, io = "Input")
    output_text = query_bot(conversation, text_only = True) # Important: Not only the user text is fed to the model, but the whole conversation so far, to provide context! The GPT API requires this
    update_convo(output_text, io = "Output") # Update conversation with model output

    # clean output_text, necessary due to the conversation-style input to the model
    output_text = output_text.replace("Output:", "").replace("Input:", "").replace("Answer:", "").replace("Correct Answer:", "").replace("Therapist:", "").replace("Client:", "").replace(":", "").replace("Therapist Response", "").replace("Client Response", "").lstrip('. ').lstrip(', ')
    
    return output_text



# Function to query recent therapy session summary from database and feed to model
@app.route("/update")
def update_bot(additional_input="", transcript_id = -1):
    """
    Function to query recent therapy session summary and feed to language model. 
    The function does not return the model's answer, as the sole purpose of the function is to provide the model with context.
    
    Args:
        transcript_id (int, optional): ID of the transcript to query. Defaults to -1, which corresponds to the most recent transcript.
    Returns:
        None, but updates global variable conversation with the summary of the most recent therapy session transcript
    """
    
    intro_string = """
    Please answer only to the next query. Throughout the whole conversation, act as the therapist, answer concisely in one sentence and consider the following background information: \n
    """
    
    summary_string = get_transcript_summary(transcript_id = transcript_id) # Get the summary of the most recent therapy session transcript (--> -1)
    prompt_string = additional_input + intro_string + summary_string # Concatenate intro and summary strings
    update_convo(prompt_string, io = "Input")
    


def initialize_conversation():
    """
    Function to initialize global variable conversation and convo_count, to keep track of the conversation, as well as the number of turns in the conversation
    """
    global conversation
    global convo_count
    conversation = ""
    convo_count = 0
    
    
    
def update_convo(input_string, io = "Input"):
    """
    Function to update global variable conversation

    Args:
        input_string (_type_): string to append to conversation
        io (str, optional): string that flags wether the update is user input ("Input") or model output ("Output"). Defaults to "Input".

    Returns:
        None, but updates global variable conversation and convo_count
    """
    global conversation
    global convo_count
    if conversation == "":
        conversation = io + ": " + input_string
    else:
        conversation = conversation + "\n " + io + ": " + input_string 
    convo_count += 1



def get_transcript_summary(path = "AnnoMI-full.csv", transcript_id = -1):
    """
    Function to query recent therapy session transcript to summarize it. 
    The summary is performed by querying the GPT-3 model with the following prompt:
    "Summarize this meeting transcript in bullet points: " + transcript
    
    Args:
        path (str, optional): Path to transcript database. Defaults to "AnnoMI-full.csv".
        transcript (int, optional): Transcript ID to summarize. Defaults to -1, which is the last transcript.

    Returns:
        str: summary of recent therapy session transcript
    """
    
    # Read in database and select the correct transcript
    transcript_database = pd.read_csv(path, sep = ",", on_bad_lines = "skip") #Read Transcript Database (in this case .csv file for presentation purposes)
    transcript_to_query = int(transcript_database['transcript_id'][-1:]) if transcript_id == -1 else transcript_id #Query last transcript from database
    transcript = transcript_database[transcript_database['transcript_id'] == transcript_to_query] # Query transcript from "database"
    
    # Create string from transcript
    transcript_string = ""
    for i in range(0, len(transcript)):
        if transcript['interlocutor'].iloc[i] == 'client':
            transcript_string += 'Client: %s \n' % transcript.iloc[i]['utterance_text']
        else:
            transcript_string += 'Therapist: %s\n' % transcript.iloc[i]['utterance_text']
    
    # Query GPT-3 model with transcript string
    summary = query_bot("Summarize this meeting transcript in bullet points: " + transcript_string, text_only = True)
    
    return summary


def query_bot(string, temperature = 0.2, text_only = True):
    """
    Function to query GPT with a given string.

    Args:
        string (str): Prompt to GPT model
        temperature (str): temperature parameter for GPT model
        text_only (bool, optional): Whether only text output shall be returned by the function. Defaults to True.

    Returns:
        str: The response of the GPT model
    """
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=string,
            temperature=temperature,
            max_tokens=500, # Maximum number of tokens occupied by query + response
            top_p=1, # Can limit the pool of tokens to choose from 1 = no limit, 0.5 = top 50% most probable tokens
            frequency_penalty=0, # Penalizes the occurence of a word that is already present in the text depending on its frequency
            presence_penalty=0) # Penalizes the occurence of a word that is already present in the text regardless of its frequency
    
    # Format response depending on whether only text or full response is desired
    response = response["choices"][0]["text"].strip() if text_only else response
    return response


if __name__ == "__main__":
    app.run()
    




