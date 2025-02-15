import os
import subprocess
import time
from typing import Optional
from pydantic import BaseModel, Field

class ComputerControl:
    def open_application(self, app_name: str) -> str:
        """Open an application"""
        try:
            if os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['open', '-a', app_name])
                return f"Opened {app_name}"
            elif os.name == 'nt':  # Windows
                subprocess.Popen(app_name)
                return f"Opened {app_name}"
        except Exception as e:
            return f"Failed to open {app_name}: {str(e)}"

    def adjust_volume(self, level: int) -> str:
        """Adjust system volume (0-100)"""
        try:
            if os.name == 'posix':  # macOS
                level = max(0, min(100, level))
                os.system(f"osascript -e 'set volume output volume {level}'")
                return f"Volume set to {level}%"
            # Add Windows implementation if needed
            return "Volume control not implemented for this OS"
        except Exception as e:
            return f"Failed to adjust volume: {str(e)}"

    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot"""
        try:
            if filename is None:
                # Create screenshots directory if it doesn't exist
                os.makedirs("screenshots", exist_ok=True)
                filename = f"screenshots/screenshot_{int(time.time())}.png"
            
            if os.name == 'posix':  # macOS
                os.system(f"screencapture '{filename}'")
                return f"Screenshot saved as {filename}"
            elif os.name == 'nt':  # Windows
                # Add Windows implementation using pyautogui or similar
                return "Screenshot not implemented for Windows yet"
            return "Screenshot not implemented for this OS"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"

# Create tools using Pydantic models
class OpenAppRequest(BaseModel):
    app_name: str = Field(..., description="Name of the application to open")

class VolumeRequest(BaseModel):
    level: int = Field(..., description="Volume level (0-100)", ge=0, le=100)

class ScreenshotRequest(BaseModel):
    filename: Optional[str] = Field(None, description="Optional filename for the screenshot") 