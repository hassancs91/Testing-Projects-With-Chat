import os
import anthropic
from typing import List, Optional
from dotenv import load_dotenv

class ClaudeBot:
    def __init__(self, system_prompt: str = None):
        # Load environment variables
        load_dotenv()
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # Set default system prompt if none provided
        default_prompt = """You are a helpful AI assistant. You provide clear, accurate, and helpful responses.
        When working with documents, you analyze them carefully and provide insights based on their content.
        If you're unsure about something, you acknowledge the uncertainty.
        If asked about events after April 2024, you acknowledge your knowledge cutoff date."""
        
        self.system_prompt = system_prompt if system_prompt else default_prompt
        
        # Initialize messages (without system prompt)
        self.messages = []
        self.loaded_documents = {}

    def load_document(self, file_path: str) -> bool:
        """Load a document from file system."""
        try:
            with open(file_path, 'r') as file:
                filename = os.path.basename(file_path)
                content = file.read()
                self.loaded_documents[filename] = content
                
                # Add document context to messages
                self.messages.append({
                    "role": "user",
                    "content": f"I'm sharing a document with you. Filename: {filename}\nContent: {content}"
                })
                self.messages.append({
                    "role": "assistant",
                    "content": f"I've received the document '{filename}' and will consider its contents in our conversation."
                })
                return True
        except Exception as e:
            print(f"Error loading document: {e}")
            return False

    def generate_response(self, user_input: str) -> str:
        """Generate response using Claude API."""
        try:
            # Add user message to history
            self.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Create the message with context
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                system=self.system_prompt,  # System prompt goes here
                messages=self.messages
            )
            
            response = message.content[0].text
            
            # Add assistant's response to history
            self.messages.append({
                "role": "assistant",
                "content": response
            })
            
            return response

        except Exception as e:
            return f"Error generating response: {e}"

    def chat(self):
        """Main chat loop."""
        print("ClaudeBot: Hello! I'm ready to help. You can:")
        print("- Chat normally")
        print("- Type 'load file: <path>' to load a document")
        print("- Type 'exit' to end the conversation")
        print("- Type 'system prompt: <new prompt>' to update the system prompt")

        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                break
                
            if user_input.lower().startswith('load file:'):
                file_path = user_input[10:].strip()
                if self.load_document(file_path):
                    print(f"ClaudeBot: Successfully loaded {os.path.basename(file_path)}")
                continue
            
            if user_input.lower().startswith('system prompt:'):
                new_prompt = user_input[13:].strip()
                self.system_prompt = new_prompt
                self.messages = []  # Clear conversation history
                print("ClaudeBot: System prompt updated. Conversation history cleared.")
                continue

            response = self.generate_response(user_input)
            print(f"\nClaudeBot: {response}")

if __name__ == "__main__":
    custom_prompt = """Your Task is to Generate Viral High Engaging Tweets For X Based on my Profile, Tweet Ideas, and Templates attached and the [draft] I will be providing.

Main Rules
-The Tweet Should be Max 280 characters.
-Don't Overuse Emojis, Add When needed.


    """
    
    bot = ClaudeBot(system_prompt=custom_prompt)
    # Or use default prompt: bot = ClaudeBot()
    bot.chat()