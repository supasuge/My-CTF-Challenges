from PIL import Image
import numpy as np

def bin_to_message(binary):
    message = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if byte == "11111110":
            break
        message += chr(int(byte, 2))
    return message

def decode_image(image_path):
    image = Image.open(image_path)
    pixels = np.array(image)
    binary_message = ""

    for row in pixels:
        for pixel in row:
            for i in range(3):  # RGB values
                binary_message += str(pixel[i] & 1)

    return bin_to_message(binary_message)

decoded_message = decode_image("../src/encoded_image.png")
print(f"Decoded Message: {decoded_message}")