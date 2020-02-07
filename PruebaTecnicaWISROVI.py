import bs4 as BeautifulSoup
import requests
import cv2
import numpy as np
import base64

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

nameFile = "captcha.png"  

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

    image = cv2.imread(nameFile)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    neg = 255-gray
    ret,thresh = cv2.threshold(neg, 245,-1,cv2.THRESH_TOZERO_INV)
    ret,thresh = cv2.threshold(thresh,100,255,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)  # find contours
    contours = [contour for idx, contour in enumerate(contours) if hierarchy[0, idx, 3]==-1]   # remove contours that are not on top of the hierarchy
    contours = [contour for contour in contours if cv2.boundingRect(contour)[3]>8]  # remove too small contours to ignore dots (i and j)
    
    res=[]
    REPRSIZE = 20
    CONTOURIMAGEFILE = 'contour.png'
    for idx, contour in enumerate(contours):
        # straight bounding rectangle
        x,y,w,h = cv2.boundingRect(contour)
 
        # translate contour
        n = contour.shape[0]
        transcontour=contour-np.array([[[x, y]]]*n)
 
        # create normalized representation for alphanumeric character
        representation = np.zeros((h, w))
        cv2.fillPoly(representation, [transcontour], color=255)
 
        # resize alphanumeric character
        representation = cv2.resize(representation, (REPRSIZE, REPRSIZE), interpolation = cv2.INTER_LINEAR)
       
        # write contour
        tmp = image.copy()
        #cv2.drawContours(tmp, [contour], 0, (0,255,0), 1)
        cv2.imwrite(CONTOURIMAGEFILE, tmp)
 
        # inputsample for classifiers
        inputsample = np.float32(representation.reshape(1,REPRSIZE*REPRSIZE))
 
        # predict with knn
        ret, results, neighbours, dist = knn.find_nearest(inputsample, 3)
 
        # append prediction with x coordinate
        res.append((chr(results[0, 0]), x))
 
    # reorder letters
    res=sorted(res, key=lambda x: x[1])
    res="".join([x[0] for x in res])
 
    print( 'trial', i+1, res)
    
    
    
    
    
    
    
    result = pytesseract.image_to_string(image) 

    payload = {'cametu': result}
    d = s.post('http://challenge01.root-me.org/programmation/ch8/', data=payload)

    if not d.text.find("retente"):
        break
    else:
        cv2.imwrite("imagenes/" + result + ".png", image)        
        if not result.find(" "):
            print("OK")
        else:
            print(result, end="")
