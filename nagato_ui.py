import tkinter as tk
from tkinter import ttk
import datetime
import math
import random

class NagatoUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nagato")
        self.root.geometry("400x600")
        self.root.minsize(400, 600)
        
        # Animation variables
        self.wave_points = 8
        self.animation_running = False
        self.wave_height = 20
        self.wave_speeds = [random.uniform(0.1, 0.2) for _ in range(self.wave_points)]
        self.wave_offsets = [random.uniform(0, 2 * math.pi) for _ in range(self.wave_points)]
        self.time = 0
        
        # Pulse animation variables
        self.pulse_alpha = 1.0
        self.pulse_increasing = False
        
        # Define font families with fallbacks
        self.title_font = ("Arial", 16, "bold")  # Simplified font definition
        self.text_font = ("Arial", 12)           # Simplified font definition
        
        self.setup_ui()
        self.start_pulse_animation()
        
    def create_gradient(self, canvas, color1, color2):
        """Create a vertical gradient on the canvas"""
        height = 600
        width = 400
        for i in range(height):
            # Calculate color for each line of pixels
            r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
            r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
            
            r = int(r1 + (r2 - r1) * i / height)
            g = int(g1 + (g2 - g1) * i / height)
            b = int(b1 + (b2 - b1) * i / height)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color)
        
    def setup_ui(self):
        # Create background canvas for gradient
        self.bg_canvas = tk.Canvas(
            self.root,
            width=400,
            height=600,
            highlightthickness=0,
            bg='#1A1A2E'  # Default background color
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create gradient background (deep purple to dark blue)
        self.create_gradient(self.bg_canvas, '#2C1F4A', '#1A1A2E')
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1A1A2E')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Spacer
        tk.Frame(main_frame, height=50, bg='#1A1A2E').pack()
        
        # Create wave/circle canvas
        self.wave_canvas = tk.Canvas(
            main_frame,
            width=200,
            height=100,
            bg='#1A1A2E',
            highlightthickness=0
        )
        self.wave_canvas.pack(pady=20)
        
        # Create the pulse circle
        self.pulse_circle = self.wave_canvas.create_oval(
            70, 20, 130, 80,  # Centered circle
            outline='#007AFF',
            width=2
        )
        
        # Create the wave lines
        self.wave_lines = []
        for i in range(4):
            line = self.wave_canvas.create_line(
                0, 0, 0, 0,
                fill=f"#{50+i*20:02x}{180+i*20:02x}ff",  # Brighter blue waves
                width=2,
                smooth=True
            )
            self.wave_lines.append(line)
            self.wave_canvas.itemconfig(line, state='hidden')
        
        # Status text with glowing effect
        self.status_label = tk.Label(
            main_frame,
            text="Tap to speak",
            font=self.title_font,
            fg="#FFFFFF",
            bg='#1A1A2E'
        )
        self.status_label.pack(pady=20)
        
        # Response area
        self.response_text = tk.Label(
            main_frame,
            text="",
            font=self.text_font,
            fg="#E0E0E0",
            bg='#1A1A2E',
            wraplength=350,
            justify="left",
            anchor="w"
        )
        self.response_text.pack(pady=20, padx=25, fill=tk.BOTH, expand=True)
        
        # Bind click event
        self.root.bind("<Button-1>", self.activate_assistant)
        
        # Initialize typing animation variables
        self.current_char = 0
        self.full_response = ""
        
    def start_pulse_animation(self):
        if not self.animation_running:
            self.animate_pulse()
    
    def animate_pulse(self):
        if self.animation_running:
            # Hide pulse circle during wave animation
            self.wave_canvas.itemconfig(self.pulse_circle, state='hidden')
            return
            
        # Show and animate pulse circle
        self.wave_canvas.itemconfig(self.pulse_circle, state='normal')
        
        # Update alpha for pulsing effect
        if self.pulse_increasing:
            self.pulse_alpha += 0.2  # Faster transition
            if self.pulse_alpha >= 1.0:
                self.pulse_increasing = False
                # Wait longer at full brightness
                self.root.after(500, self.animate_pulse)
                return
        else:
            self.pulse_alpha -= 0.2  # Faster transition
            if self.pulse_alpha <= 0.2:
                self.pulse_increasing = True
                # Wait longer at dim state
                self.root.after(500, self.animate_pulse)
                return
        
        # Create color based on alpha without using alpha channel
        r = 0
        g = 122
        b = 255
        
        # Adjust brightness instead of alpha
        factor = self.pulse_alpha
        color = f'#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}'
        
        self.wave_canvas.itemconfig(
            self.pulse_circle,
            outline=color
        )
        
        # Slower pulse rate (500ms for fade + 500ms pause = 1 second cycle)
        self.root.after(100, self.animate_pulse)
        
    def animate_waves(self):
        if not self.animation_running:
            # Hide waves and show pulse
            for line in self.wave_lines:
                self.wave_canvas.itemconfig(line, state='hidden')
            self.wave_canvas.itemconfig(self.pulse_circle, state='normal')
            return
            
        # Hide pulse and show waves
        self.wave_canvas.itemconfig(self.pulse_circle, state='hidden')
        for line in self.wave_lines:
            self.wave_canvas.itemconfig(line, state='normal')
        
        self.time += 0.05  # Slower time progression
        canvas_width = 200
        canvas_height = 100
        center_y = canvas_height // 2
        
        # Create more natural wave movement
        for wave_idx, wave_line in enumerate(self.wave_lines):
            points = []
            base_amplitude = self.wave_height - (wave_idx * 4)  # Decreasing amplitude for each wave
            
            # Add multiple sine waves with different frequencies
            for i in range(self.wave_points * 2):  # Double the points for smoother waves
                x = i * canvas_width / (self.wave_points * 2 - 1)
                
                # Combine multiple sine waves
                y = center_y
                y += math.sin(self.time * 2 + x * 0.05) * base_amplitude * 0.5
                y += math.sin(self.time * 1.5 + x * 0.03) * base_amplitude * 0.3
                y += math.sin(self.time + x * 0.02) * base_amplitude * 0.2
                
                # Add small random variation
                y += random.uniform(-0.5, 0.5)
                
                points.extend([x, y])
            
            self.wave_canvas.coords(wave_line, *points)
        
        self.root.after(30, self.animate_waves)
        
    def activate_assistant(self, event=None):
        self.animation_running = True
        self.wave_height = 20
        self.status_label.config(text="Listening...")
        self.animate_waves()
        
        # Start voice recognition in a separate thread to prevent UI freezing
        self.root.after(100, self.start_voice_recognition)
        
    def start_voice_recognition(self):
        from services.vtt import vtt_service
        import threading
        
        def recognition_thread():
            try:
                command = vtt_service.get_voice_command()
                # Use after to safely update UI from thread
                self.root.after(0, self.handle_command, command)
            except Exception as e:
                error_message = f"Error: {str(e)}"
                self.root.after(0, self.handle_error, error_message)
            
        thread = threading.Thread(target=recognition_thread)
        thread.daemon = True
        thread.start()
        
    def handle_command(self, command):
        self.status_label.config(text="Processing...")
        self.wave_height = 10
        
        # Import and use the command processor
        from services.process_command import command_processor
        
        # Process the command
        try:
            response = command_processor.process_command(command)
            # Start the typing animation
            self.start_typing_animation(command, response)
        except Exception as e:
            self.root.after(1000, lambda: self.show_response(
                f"Error processing command: {str(e)}"
            ))

    def start_typing_animation(self, command, response):
        # Clear previous text
        self.response_text.config(text="")
        
        # Format the conversation
        you_text = "You: " + command + "\n\n"
        nagato_text = "Nagato: " + response
        full_text = you_text + nagato_text
        
        # Initialize typing animation
        self.current_char = 0
        self.full_response = full_text
        self.type_next_char()

    def type_next_char(self):
        if self.current_char < len(self.full_response):
            # Update text with one more character
            current_text = self.full_response[:self.current_char + 1]
            self.response_text.config(text=current_text)
            self.current_char += 1
            
            # Random delay between 10ms and 30ms for natural typing effect
            typing_delay = random.randint(10, 30)
            
            # If it's a punctuation mark, add a longer pause
            if self.current_char < len(self.full_response) and \
               self.full_response[self.current_char - 1] in '.!?':
                typing_delay = 200
            
            self.root.after(typing_delay, self.type_next_char)
        else:
            # Animation complete, reset status
            self.status_label.config(text="Tap to speak")
            self.show_response_complete()

    def show_response_complete(self):
        self.animation_running = False
        
        # Clear the waves
        for line in self.wave_lines:
            self.wave_canvas.coords(line, 0, 50, 0, 50)
            self.wave_canvas.itemconfig(line, state='hidden')
        
        # Reset and restart pulse animation
        self.pulse_alpha = 1.0
        self.pulse_increasing = False
        self.wave_canvas.itemconfig(self.pulse_circle, state='normal')
        self.animate_pulse()

    def handle_error(self, error_message):
        self.status_label.config(text="Error occurred")
        self.root.after(1000, lambda: self.show_response(f"Sorry, there was an error: {error_message}"))

def main():
    root = tk.Tk()
    app = NagatoUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
