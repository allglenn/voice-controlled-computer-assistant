import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CommandProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('LLM_MODEL', 'gpt-4')

    def process_command(self, command_text):
        try:
            # Create a system message for more natural responses
            system_message = """You are Nagato, a friendly and capable assistant. 
            Respond naturally to commands about controlling the computer, without mentioning 
            that you're an AI. Keep responses conversational and direct, as if you're 
            having a casual chat. Avoid phrases like "I would" or "I can" - just do it.
            
            Example:
            User: "Open Chrome"
            Bad: "As an AI assistant, I can help you open Chrome..."
            Good: "Opening Chrome for you right away."
            
            User: "What's the weather like?"
            Bad: "I'll check the weather information for you..."
            Good: "Let me check that... It's currently 72°F and sunny outside."
            """

            # Get response from GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": command_text}
                ],
                temperature=0.7,
                max_tokens=150,
                presence_penalty=0.6,  # Encourage more varied responses
                frequency_penalty=0.3   # Reduce repetitive phrases
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error processing command: {str(e)}")
            return f"Sorry, I couldn't process that command: {str(e)}"

# Create singleton instance
command_processor = CommandProcessor()