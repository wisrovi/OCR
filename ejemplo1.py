from PIL import Image
import subprocess
import requests
import re
import base64
s = requests.Session()
base = "http://challenge01.root-me.org//programmation/ch8/ch8.php"
s.cookies.update({
    "spip_session": "NO!",
    "PHPSESSID": "MAYBE..."
})
d = s.get(base).text
im = re.match(r".*base64,(.*?)\".*", d)
im = im.group(1)
with open("im.png", "wb") as f:
    f.write(base64.b64decode(im))
 
img = Image.open("im.png") # delete all the noise ;)
width, height = img.size
pix = img.load()
for i in range(width):
    for j in range(height):
        if pix[i, j] == (0, 0, 0):
            pix[i, j] = (255, 255, 255)
img.save("im.png")
 
# Now we have a clear image so gocr will always return a 100% valid answear
r = str(subprocess.check_output("gocr im.png -C 'a-z0-9A-Z' -u ''", shell=True)).strip()
d = s.post(base, data={"cametu": r})
print(d.text)