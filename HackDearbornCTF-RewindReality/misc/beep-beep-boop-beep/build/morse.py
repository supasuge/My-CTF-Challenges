import base64
import os
from pydub import AudioSegment
from pydub.generators import Sine

# ---------------------------
# Configuration Parameters
# ---------------------------

# Morse Code Timing Definitions (in milliseconds)
DOT_DURATION = 100        # Duration of a dot
DASH_DURATION = 300       # Duration of a dash
SYMBOL_SPACE = 100        # Space between symbols (dots and dashes)
LETTER_SPACE = 300        # Space between letters (if applicable)
WORD_SPACE = 700          # Space between words (if applicable)

# Audio Frequency (in Hz)
FREQUENCY = 1000          # Frequency of the tone

# Output Audio File
OUTPUT_FILENAME = "morse_code_audio.wav"

# ---------------------------
# Binary to Morse Code Mapping
# ---------------------------

def binary_to_morse(binary_str):
    """
    Converts a binary string to a Morse code string.
    Each '0' is converted to '.', and each '1' is converted to '-'.
    
    Args:
        binary_str (str): The binary string to convert.
        
    Returns:
        str: The corresponding Morse code string.
    """
    morse = ''.join(['.' if bit == '0' else '-' for bit in binary_str])
    return morse

# ---------------------------
# Morse Code to Audio Generation
# ---------------------------

def generate_morse_audio(morse_code, output_file):
    """
    Generates a Morse code audio file from a Morse code string.
    
    Args:
        morse_code (str): The Morse code string to convert to audio.
        output_file (str): The filename for the output audio file.
        
    Returns:
        None
    """
    audio = AudioSegment.silent(duration=0)  # Start with silence

    # Define the audio segments for dot and dash
    dot = Sine(FREQUENCY).to_audio_segment(duration=DOT_DURATION).fade_out(10)
    dash = Sine(FREQUENCY).to_audio_segment(duration=DASH_DURATION).fade_out(10)
    symbol_space = AudioSegment.silent(duration=SYMBOL_SPACE)
    letter_space = AudioSegment.silent(duration=LETTER_SPACE)
    word_space = AudioSegment.silent(duration=WORD_SPACE)

    for symbol in morse_code:
        if symbol == '.':
            audio += dot
        elif symbol == '-':
            audio += dash
        else:
            # Handle unexpected symbols
            print(f"Warning: Unexpected Morse symbol '{symbol}' encountered.")
            continue
        # Add space between symbols
        audio += symbol_space

    # Optional: Add a final silence at the end
    audio += word_space

    # Export the final audio
    audio.export(output_file, format="wav")
    print(f"Morse code audio has been saved as '{output_file}'.")

# ---------------------------
# Main Function
# ---------------------------

def main():
    # Replace this binary string with your actual binary string
    with open("flagqr.png", "rb") as f:
        data = base64.b64encode(f.read())
    binary_img = ''.join([format(n, '08b') for n in data])
    
    # Ensure the binary string is valid
    if not all(c in '01' for c in binary_img):
        print("Error: The binary string contains characters other than '0' and '1'.")
        return
    
    # Convert binary to Morse code
    morse_code = binary_to_morse(binary_img)
    print(f"Morse Code: {morse_code}")
    
    # Generate Morse code audio
    generate_morse_audio(morse_code, OUTPUT_FILENAME)

if __name__ == "__main__":
    main()
