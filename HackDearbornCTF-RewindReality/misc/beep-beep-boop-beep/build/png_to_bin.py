import base64


def binary_to_bytes(binary_str):
    """
    Converts a binary string to bytes.
    
    Args:
        binary_str (str): The binary string to convert.
        
    Returns:
        bytes: The corresponding bytes.
        
    Raises:
        ValueError: If the binary string's length is not a multiple of 8.
    """
    if len(binary_str) % 8 != 0:
        raise ValueError("The binary string's length is not a multiple of 8.")
    
    byte_array = bytearray()
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        byte_array.append(int(byte, 2))
    return bytes(byte_array)

def convert_binary_to_png(binary_img, output_filename="recovered_flagqr.png"):
    """
    Converts a binary string back to a PNG file.
    
    Args:
        binary_img (str): The binary string representing the Base64-encoded PNG.
        output_filename (str): The filename for the recovered PNG.
        
    Returns:
        None
    """
    try:
        # Step 1: Convert binary string to Base64 bytes
        base64_bytes = binary_to_bytes(binary_img)
        
        # Step 2: Decode Base64 to get original PNG binary data
        png_binary = base64.b64decode(base64_bytes)
        
        # Step 3: Write the binary data to a PNG file
        with open(output_filename, "wb") as f:
            f.write(png_binary)
        
        print(f"PNG file has been successfully recovered as '{output_filename}'.")
        
    except ValueError as ve:
        print("ValueError:", ve)
    except base64.binascii.Error as be:
        print("Base64 Decoding Error:", be)
    except Exception as e:
        print("An unexpected error occurred:", e)

# Example usage
if __name__ == "__main__":
    # Replace this string with your actual binary_img string
    with open("flagqr.png", "rb") as f:
        data = base64.b64encode(f.read())
    binary_img = ''.join([format(n, '08b') for n in data])
    print(binary_img)    
    convert_binary_to_png(binary_img, "recovered_flagqr.png")


    #print(data)

# https://stackoverflow.com/questions/67231669/convert-png-to-a-binary-base-2-string-in-python




