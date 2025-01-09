import os
from pydub import AudioSegment
from pydub.generators import Sine
import base64

FREQ_0 = 800    # Frequency for binary '0' in Hz
FREQ_1 = 1200   # Frequency for binary '1' in Hz

# Timing Definitions (in milliseconds)
TONE_DURATION = 200    # Duration of each tone (0 and 1)
SILENCE_DURATION = 100 # Duration of silence between tones

# Output Audio File
OUTPUT_FILENAME = "binary_fsk_audio.wav"



def binary_to_fsk_audio(binary_str, output_file):
    """
    Converts a binary string to an FSK audio file.
    
    Args:
        binary_str (str): The binary string to convert (e.g., '010101').
        output_file (str): The filename for the output audio file.
    
    Returns:
        None
    """
    # Initialize an empty audio segment
    audio = AudioSegment.silent(duration=0)
    
    # Define the tones for '0' and '1'
    tone_0 = Sine(FREQ_0).to_audio_segment(duration=TONE_DURATION).fade_out(10)
    tone_1 = Sine(FREQ_1).to_audio_segment(duration=TONE_DURATION).fade_out(10)
    
    # Define silence between tones
    silence = AudioSegment.silent(duration=SILENCE_DURATION)
    
    for index, bit in enumerate(binary_str):
        if bit == '0':
            audio += tone_0
        elif bit == '1':
            audio += tone_1
        else:
            print(f"Warning: Invalid bit '{bit}' at position {index}. Skipping.")
            continue
        # Add silence after each tone
        audio += silence
    
    # Export the final audio
    audio.export(output_file, format="wav")
    print(f"FSK audio has been saved as '{output_file}'.")



def main():
    with open("flagqr.png", "rb") as f:
        data = base64.b64encode(f.read())
    binary_img = ''.join([format(n, '08b') for n in data])
    if not all(bit in '01' for bit in binary_img):
        print("Error: The binary string contains characters other than '0' and '1'.")
        return
    
    # Convert binary to FSK audio
    binary_to_fsk_audio(binary_img, OUTPUT_FILENAME)

if __name__ == "__main__":
    main()