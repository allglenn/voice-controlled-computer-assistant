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
            # Use Nagato agent to process the command
            from services.nagato_agent import nagato_agent
            
            response = nagato_agent.process_command(command_text)
            
            if response.success:
                if response.action_taken:
                    return f"{response.message}\n{response.action_taken}"
                return response.message
            else:
                # Fall back to conversational response if command fails
                return self._get_conversation_response(command_text)
                
        except Exception as e:
            print(f"Error processing command: {str(e)}")
            return f"Sorry, I couldn't process that command: {str(e)}"

    def _get_conversation_response(self, command_text):
        """Get conversational response when command processing fails"""
        system_message = """You are Nagato, a friendly and capable assistant. 
        Respond naturally to commands about controlling the computer, without mentioning 
        that you're an AI. Keep responses conversational and direct, as if you're 
        having a casual chat."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": command_text}
            ],
            temperature=0.7,
            max_tokens=150
        )

        return response.choices[0].message.content

# Create singleton instance
command_processor = CommandProcessor()