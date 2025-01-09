
import os
import random
import qrcode
FLAG = open("flag.txt").read().strip()
qqr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
qqr.add_data(FLAG)
qqr.make(fit=True)
img = qqr.make_image(fill_color="black", back_color="white")
img.save("flagqr.png")


