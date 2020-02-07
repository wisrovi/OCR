import urllib.request
import urllib.parse
import requests 
import re
import base64
import subprocess
import cv2
import numpy as np
from matplotlib import pyplot as plt

#borrar +++++++++++++++++++++
#https://towardsdatascience.com/read-text-from-image-with-one-line-of-python-code-c22ede074cac
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#+++++++++++++++++++


def DescargarImagenCAPTCHA(url, nombreGuardarImagen):
    #extraer la pagina HTML    
    req = urllib.request.Request(urlServidorImagen)
    response = urllib.request.urlopen(req)
    html = response.read()
    stringHtml = html.decode("utf-8")  #necesario convertirlo a string para poder buscar en el html (formato orginal: bytes)

    #Buscar en el HTML la ruta para extraer sólo la imagen    
    regex = r'data:image/png;base64,(.*)" /><br><br>'
    result = re.search(regex, stringHtml)
    result = result.group(1)

    #Decodificar la url de la imagen y guardar la imagen    
    result = base64.b64decode(result)  #tengo la imagen en una variable
    file_handle = open(nombreGuardarImagen, 'wb')
    file_handle.write(result)   #guardo la imagen
    file_handle.close
    
    file_handle = open(nombreGuardarImagen, 'rb')
    result = subprocess.Popen(['gocr -i captcha.png'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    file_handle.close

def LimpiarImagen(nombreImagen):
    img = cv2.imread(nameFile,0)
    imagenFiltrada = cv2.threshold(img,127,255,cv2.THRESH_TOZERO_INV)[1]
    imagenFiltrada = cv2.bitwise_not(imagenFiltrada)
    return imagenFiltrada

def ReforzarColores(imagen, nombreImagen):
    cv2.imwrite(nombreImagen, imagenFiltrada)
    imagen = cv2.imread(nameFileFilter)
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    grises_bajos = np.array([232,232,232], dtype=np.uint8)
    grises_altos = np.array([0, 0, 0], dtype=np.uint8)
    mascara_negra = cv2.inRange(hsv, grises_altos, grises_bajos)
    cv2.imwrite(nombreImagen, mascara_negra)
    imagen = cv2.imread(nombreImagen)
    imagen = cv2.bitwise_not(imagen)
    cv2.imwrite(nombreImagen, imagen)
    imagen = cv2.imread(nombreImagen)
    return imagen







print("Librerias cargadas")




nameFile = 'captcha.png'
nameFileFilter = 'captcha-filtrado.png'
urlServidorImagen = "http://challenge01.root-me.org/programmation/ch8/"

opener = urllib.request.build_opener()
#opener.addheaders = [('User-agent', 'Mozilla/5.0')]
#opener.addheaders.append(('Connection', 'Keep-Alive'))


opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0')]
opener.addheaders.append(('Cookie', 'challenge_frame=1; spip_session=myspip_session; PHPSESSID=myPHPSESSID'))
#opener.addheaders.append(('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'))
opener.addheaders.append(('Accept-Language', 'en-US,en;q=0.5'))
#opener.addheaders.append(('Accept-Encoding', 'gzip, deflate'))
opener.addheaders.append(('DNT', '1'))
opener.addheaders.append(('Connection', 'Keep-Alive'))


response = opener.open(urlServidorImagen)
html = response.read()
stringHtml = html.decode("utf-8")
regex = r'data:image/png;base64,(.*)" /><br><br>'
result = re.search(regex, stringHtml)
result = result.group(1)
result = base64.b64decode(result)
file_handle = open(nameFile, 'wb')
file_handle.write(result)   #guardo la imagen
file_handle.close
file_handle = open(nameFile, 'rb')
result = subprocess.Popen(['gocr -i captcha.png'], shell=True, stdout=subprocess.PIPE).communicate()[0]
file_handle.close


#DescargarImagenCAPTCHA(urlServidorImagen, nameFile)
imagenFiltrada = LimpiarImagen(nameFile)
#imagenReforzada = ReforzarColores(imagenFiltrada, nameFileFilter)


file_handle = open(nameFile, 'rb')
result = subprocess.Popen(['gocr -i captcha.png'], shell=True, stdout=subprocess.PIPE).communicate()[0]
file_handle.close


values = {'cametu':result}
post_data = urllib.parse.urlencode(values)
post_data = post_data.encode('ascii')

#opener.addheaders.append(('Referer', urlServidorImagen))
response = opener.open(urlServidorImagen, post_data)

while True:
    html = response.read()
    stringHtml = html.decode("utf-8")
    if not('Failed' in stringHtml) and stringHtml:
        break

#file_handle = open('result.html', 'w')
#file_handle.write(html.decode("utf-8"))
#file_handle.close

print(html)


plt.imshow(imagenFiltrada,'gray')
plt.show()


""" 

imagenReforzada = cv2.imread(nameFileFilter)

result = pytesseract.image_to_string(imagenFiltrada) 
values = {'cametu':result}
print( result )

r = requests.post(url = urlServidorImagen, data = values) 
pastebin_url = r.text
print("The pastebin URL is:%s"%pastebin_url)
"""
