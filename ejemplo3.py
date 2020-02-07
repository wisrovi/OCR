import numpy as np
import cv2
import requests
 
IMAGEFILE = 'captcha.png'
CONTOURIMAGEFILE = 'contour.png'
REQUESTURL='http://challenge01.root-me.org/programmation/ch8/'
REPRSIZE = 20
IMGSIZE = 500
CENTER = (IMGSIZE/2, IMGSIZE/2)
 
def createtrainingset(charset):
    Xtrain=[]
    ytrain=[]
   
    for char in charset:
        for charthickness in range(2,4):
            for angle in np.arange(-5, 5, 1): 
                charsize = 5
                scale = 1.0
 
                img=np.zeros((IMGSIZE, IMGSIZE))
                #cv2.putText(img, char, CENTER, cv2.FONT_HERSHEY_PLAIN, charsize, 255, charthickness)
 
                rotmat = cv2.getRotationMatrix2D(CENTER, angle, scale)
                res = cv2.warpAffine(img, rotmat, img.shape)
 
                res = res.astype('uint8')
 
                contours, hierarchy = cv2.findContours(res,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
 
                for idx, contour in enumerate(contours):
                    if hierarchy[0,idx,3]==-1:
                       
                        # straight bounding rectangle
                        x,y,w,h = cv2.boundingRect(contour)
 
                        # ignore dots (i and j)
                        if h<30: continue
 
                        # translate contour
                        n = contour.shape[0]
                        transcontour=contour-np.array([[[x, y]]]*n)
 
                        # create normalized representation for alphanumeric character
                        representation = np.zeros((h, w))
                        cv2.fillPoly(representation, [transcontour], color=255)
 
                        # resize alphanumeric character
                        representation = cv2.resize(representation, (REPRSIZE, REPRSIZE), interpolation = cv2.INTER_LINEAR)
 
                        # append representation to training set
                        Xtrain.append(np.float32(representation.reshape(REPRSIZE*REPRSIZE)))
                        ytrain.append(np.float32(ord(char)))
 
    # transform into numpy arrays
    return (np.array(Xtrain), np.array(ytrain))
 
# create training set
print( 'creating training set...')
Xtrain, ytrain = createtrainingset('QWERTYUIOPASDFGHJKLZXCVBNM123456789qwertyuiopsadfghjklzxcvbnm')
 
# create knn
print( 'training knn...')
knn = cv2.ml.KNearest_create()
knn.train(Xtrain,cv2.ml.ROW_SAMPLE,ytrain)
 
# 100 trials
for i in range(100):
   
    # request captcha
    resp = requests.get(REQUESTURL)
 
    # extract and save image
    data=resp.content.split('base64,')[1].split('"')[0]
    with open(IMAGEFILE, 'wb') as output:
        output.write(data.decode('base64'))
 
    # load image
    img = cv2.imread(IMAGEFILE)
 
    # convert to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
    # thresholding
    neg = 255-gray
    ret,thresh = cv2.threshold(neg, 245,-1,cv2.THRESH_TOZERO_INV)
    ret,thresh = cv2.threshold(thresh,100,255,cv2.THRESH_BINARY)
 
    # find contours
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
 
    # remove contours that are not on top of the hierarchy
    contours = [contour for idx, contour in enumerate(contours) if hierarchy[0, idx, 3]==-1]
 
    # remove too small contours to ignore dots (i and j)
    contours = [contour for contour in contours if cv2.boundingRect(contour)[3]>8]
 
    res=[]
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
        tmp = img.copy()
        cv2.drawContours(tmp, [contour], 0, (0,255,0), 1)
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
 
    # send payload
    payload = {'cametu': res}
    resp = requests.post(REQUESTURL, payload, cookies=resp.cookies)
    if 'flag' in resp.content:
        print(resp.content)
        break