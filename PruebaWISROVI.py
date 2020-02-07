import bs4 as BeautifulSoup
import requests
import cv2
import numpy as np
import base64


def Comprobar(textoPredicho, image):
	import pytesseract
	pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
	result = pytesseract.image_to_string(image) 
	if textoPredicho.__eq__(result):
		return True
	else:
		return False

nameFile = "captcha.png"  

textInImageFind = ""
while True:
    s = requests.Session()
    html = s.get('http://challenge01.root-me.org/programmation/ch8/')

    soup = BeautifulSoup.BeautifulSoup(html.text)
    img = soup.find_all('img')
    pngBin = str(img).split(',')[1]
    pngBin = base64.b64decode(pngBin[:-4])
    imgfile = open(nameFile, 'wb+')
    imgfile.write(pngBin)
    imgfile.close()

	#cargamos y limpiamos la imagen 
    image = cv2.imread(nameFile)
	imagenFiltrada = cv2.threshold(img,127,255,cv2.THRESH_TOZERO_INV)[1]
    imagenFiltrada = cv2.threshold(image, 245,-1,cv2.THRESH_TOZERO_INV)[1]
    imagenFiltrada = cv2.threshold(image, 100,255,cv2.THRESH_BINARY)[1]
    imagenFiltrada = cv2.bitwise_not(imagenFiltrada)
    cv2.imwrite(nameFile, image)    
	
    file_handle = open(nameFile, 'rb')
    result = subprocess.Popen(['gocr -i captcha.png'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    file_handle.close
    
    payload = {'cametu': result}
    d = s.post('http://challenge01.root-me.org/programmation/ch8/', data=payload)

    if not d.text.find("Failed"):
		textInImageFind = result
        break
    
print(  Comprobar(textInImageFind, nameFile)  )