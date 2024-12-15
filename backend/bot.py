import os
import google.generativeai as genai

class FinanceChatbotModel:
    def __init__(self, api_key):
        # Set up the environment for the Gemini API key
        os.environ["GEMINI_API_KEY"] = api_key
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Create the generative model with the configuration
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 30,
            "max_output_tokens": 1000,
            "response_mime_type": "text/plain",
        }
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
        )
        
        self.history = []

    def get_response(self, user_input):
        """Handles a conversation with the user."""
        chat_session = self.model.start_chat(history=self.history)
        response = chat_session.send_message(user_input)
        
        # Extract and return model's response
        model_response = response.text
        self.update_history(user_input, model_response)
        
        return model_response

    def update_history(self, user_input, model_response):
        """Maintains conversation history for context in the chatbot."""
        self.history.append({'role': 'user', 'parts': [user_input]})
        self.history.append({'role': 'model', 'parts': [model_response]})
