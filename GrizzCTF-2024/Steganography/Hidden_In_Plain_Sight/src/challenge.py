from PIL import Image
import numpy as np
import json
import sys

def message_to_bin(message):
    return ''.join([format(ord(char), '08b') for char in message])

def encode_image(image_path, message):
    image = Image.open(image_path)
    binary_message = message_to_bin(message) + '1111111111111110'
    pixels = np.array(image)
    index = 0

    for row in pixels:
        for pixel in row:
            for i in range(3):  # RGB values
                if index < len(binary_message):
                    pixel[i] = pixel[i] & ~1 | int(binary_message[index])
                    index += 1
            if index >= len(binary_message):
                break
    encoded_image = Image.fromarray(pixels)
    encoded_image.save("encoded_image.png")


def main():
    flag = "GrizzCTF{0m6_y0u_f0un9_th3_l2b}"
    secret_message = flag
    encode_image(sys.argv[1], secret_message)
if __name__ == '__main__':
    main()