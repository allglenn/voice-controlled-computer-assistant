from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
from services.computer_control import ComputerControl, OpenAppRequest, VolumeRequest, ScreenshotRequest
from openai import OpenAI
import os
import json

class CommandType(Enum):
    OPEN_APP = "open_app"
    VOLUME = "volume"
    SCREENSHOT = "screenshot"
    CONVERSATION = "conversation"

class Command(BaseModel):
    type: CommandType
    content: dict

class NagatoResponse(BaseModel):
    message: str
    action_taken: Optional[str] = None
    success: bool = True

class NagatoAgent:
    def __init__(self):
        self.computer = ComputerControl()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def process_command(self, text: str) -> NagatoResponse:
        """Process natural language command and execute appropriate action"""
        try:
            # Use LLM to parse the command and determine intent
            parsed = self.parse_command(text)
            
            if parsed.type == CommandType.OPEN_APP:
                request = OpenAppRequest(**parsed.content)
                result = self.computer.open_application(request.app_name)
                return NagatoResponse(
                    message=f"Sure! {result}",
                    action_taken=f"Opened {request.app_name}",
                    success=True
                )
                
            elif parsed.type == CommandType.VOLUME:
                request = VolumeRequest(**parsed.content)
                result = self.computer.adjust_volume(request.level)
                return NagatoResponse(
                    message=f"Alright, {result}",
                    action_taken=f"Adjusted volume to {request.level}%",
                    success=True
                )
                
            elif parsed.type == CommandType.SCREENSHOT:
                request = ScreenshotRequest(**parsed.content)
                result = self.computer.take_screenshot(request.filename)
                return NagatoResponse(
                    message=f"Done! {result}",
                    action_taken="Took screenshot",
                    success=True
                )
                
            else:
                return NagatoResponse(
                    message="I'm not sure how to help with that yet.",
                    success=False
                )
                
        except Exception as e:
            return NagatoResponse(
                message=f"Sorry, I encountered an error: {str(e)}",
                success=False
            )

    def parse_command(self, text: str) -> Command:
        """Use LLM to parse the command and determine the intent"""
        
        function_descriptions = {
            "functions": [
                {
                    "name": "open_application",
                    "description": "Open an application on the computer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "Name of the application to open"
                            }
                        },
                        "required": ["app_name"]
                    }
                },
                {
                    "name": "adjust_volume",
                    "description": "Adjust the system volume",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "Volume level (0-100)",
                                "minimum": 0,
                                "maximum": 100
                            }
                        },
                        "required": ["level"]
                    }
                },
                {
                    "name": "take_screenshot",
                    "description": "Take a screenshot of the screen",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Optional filename for the screenshot"
                            }
                        }
                    }
                }
            ]
        }

        try:
            # Ask LLM to understand the command
            response = self.client.chat.completions.create(
                model=os.getenv('LLM_MODEL', 'gpt-4'),
                messages=[
                    {"role": "system", "content": """You are a command parser for a computer control system. 
                    Analyze user commands and map them to the appropriate function call. 
                    For volume commands, understand relative terms (louder/quieter) and convert them to appropriate levels.
                    Respond only with the function call, no other text."""},
                    {"role": "user", "content": text}
                ],
                functions=function_descriptions["functions"],
                function_call="auto"
            )

            # Extract the function call
            if response.choices[0].message.function_call:
                func_name = response.choices[0].message.function_call.name
                func_args = json.loads(response.choices[0].message.function_call.arguments)

                # Map to appropriate command type
                if func_name == "open_application":
                    return Command(
                        type=CommandType.OPEN_APP,
                        content={"app_name": func_args["app_name"]}
                    )
                elif func_name == "adjust_volume":
                    return Command(
                        type=CommandType.VOLUME,
                        content={"level": func_args["level"]}
                    )
                elif func_name == "take_screenshot":
                    return Command(
                        type=CommandType.SCREENSHOT,
                        content={"filename": func_args.get("filename")}
                    )

            return Command(
                type=CommandType.CONVERSATION,
                content={}
            )

        except Exception as e:
            print(f"Error parsing command: {str(e)}")
            return Command(
                type=CommandType.CONVERSATION,
                content={}
            )

# Create singleton instance
nagato_agent = NagatoAgent() 