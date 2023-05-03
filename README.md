# Transferapy

Experimenting with few-shot learning / fine-tuning to adapt GPT-3.5 to in-person therapy style conversation. <br>

Aim of the new model: 
- To serve as communication instance for patient between in-person sessions
- To summarize the conversation content for the therapist to prepare in-person session 
- To mimick the therapists conversation style to provide patient with a familiar and trusting feeling
- NOT to therapize or give critical advice. The model has to be waterproof to circumvent questions for diagnoses, recommendations for actions, interpretations, or trauma-inducing, insensitive, harmful or stigmatizing questions.

Approach:
- Prompt GPT-3.5 with patient utterances as the query, with the respective therapist answer flagged as the correct answer. Provide query-reponse pairs in the order as the conversation was held in reality. Experiment with query-reponse lenghts: 3, 5, 10. 
- Check input data and clean problematic reponses from the therapist. 
-- Replace utterances about diagnoses with something like "your diagnosis", instead of possibly stigmatizing / reinforcing diagnosis labels.
-- Replace advice / action recommendations / potentially harmful questions with standard phrase - tbd
