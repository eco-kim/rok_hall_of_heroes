import glob
import cv2
import numpy as np
import re
from pytesseract import *
import pandas as pd

def boxcut(image):  ##영령전 흰 박스 모서리좌표 구하는 함수
    rawG = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    ny, nx = np.shape(rawG)
    y1 = ny
    for j in range(ny-1,0,-1):
        for i in range(nx//3):
            temp = rawG[j,i:i+nx//3]
            if np.min(temp)>220:
                y1 = j
                break    
        if y1!=ny:
            break

    y0 = 0
    for j in range(0,ny):
        temp = rawG[j,i:i+nx//3]
        if np.min(temp)>220:
            y0 = j
            break    

    rawG = rawG[y0:y1,:]
    ny, nx = np.shape(rawG)

    x0 = 0
    for i in range(nx):
        for j in range(ny//2):
            temp = rawG[j:j+ny//2,i]
            if np.min(temp)>220:
                x0 = i
                break    
        if x0!=0:
            break
    x1 = nx-1
    for i in range(nx-1,-1,-1):
        for j in range(ny//2):
            temp = rawG[j:j+ny//2,i]
            if np.min(temp)>220:
                x1 = i
                break    
        if x1!=nx-1:
            break
    return image[y0:y1,x0:x1,:]

def iconcut(boximage):
    ny, nx, _ = np.shape(boximage)
    ratio = 700/nx
    boximage = cv2.resize(boximage, (0,0), fx=ratio, fy=ratio)
    ny, nx, _ = np.shape(boximage)
    totalarea = ny*nx
    ret , rawBbox = cv2.threshold(boximage[:,:,0], -1, 255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) ##Blue channel  
    contours,_=cv2.findContours(rawBbox, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  
    
    icons = []
    nums = []
    for i, cnt in enumerate(contours):
        rect = cv2.minAreaRect(cnt)  ##외접하는 가장 작은 사각형
        box = np.int0(cv2.boxPoints(rect)).transpose() ##네 꼭지점 ul, ur, lr, ll 시계방향
        x0, x1, y0, y1 = box[0].min(), box[0].max(), box[1].min(), box[1].max()
        cc = (x1-x0)/nx
        if (0.075<(x1-x0)/nx<0.095)&(cv2.contourArea(cnt)>totalarea*0.0075):
            icons.append(boximage[y0:y1,x0:x1])
            yy = np.int0((2*y0+y1)/3)+2 #1:2내분점+2 
            xx = np.int0((-x0+3*x1)/2) #3:1외분점
            if (y1-y0)/(x1-x0)<1.1:  ##특수병종이면 ny/nx 1.05정도나옴. 
                nums.append(255-rawBbox[yy:yy+23,xx:xx+95])
            else:
                nums.append(255-rawBbox[yy:yy+23,xx+7:xx+95+7]) ##일반병종이면 1.15
    return icons, nums

def tier(icon):
    global t5_template, t4_template
    icon = cv2.resize(icon, (121,134))
    match = cv2.matchTemplate(t5_template,icon[10:70,10:-10],method=cv2.TM_CCOEFF_NORMED)
    if np.max(match)>0.85:
        return 't5'
    else:
        match = cv2.matchTemplate(t4_template,icon[10:70,10:-10],method=cv2.TM_CCOEFF_NORMED)
        if np.max(match)>0.85:
            return 't4'
        else:
            return 't3'

def numread(numim):
    text = pytesseract.image_to_string(numim, lang='eng', config='--psm 7')
    text = ''.join(re.findall('\d+',text))
    return int(text)

basedir = 'C:/Users/ikho7/Desktop/projects/rok_contribution/spirits/'
datadir = 'C:/Users/ikho7/Desktop/aws/screenshots/'
datadf = pd.DataFrame(columns=['uid','t5','t4','t3under'])
subdf = pd.DataFrame(columns=['uid','main_uid','t5','t4','t3under'])
t5_template = cv2.imread(basedir+'t5_template.png')
t4_template = cv2.imread(basedir+'t4_template.png')

flist = glob.glob(basedir+'discord/screenshots/*')
baselen = len(basedir+'discord/screenshots/')
nn = len(flist)
print(f'전체 : {nn}개')

for j,f in enumerate(flist):
    fname = f[baselen:]
    if fname[0]=='s':
        s0 = fname.find('_')
        s1 = fname.find('.')
        uid = int(fname[s0+1:s1])
        mainid = int(fname[3:s0])
        cc = 1
    else:
        s1 = fname.find('.')
        uid = int(fname[:s1])
        cc = 0
    if str(f).lower().endswith('.gif'):
        gif = cv2.VideoCapture(f)
        ret, frame = gif.read()  # ret=True if it finds a frame else False.
        if ret:
            raw =frame
    else:
        raw = cv2.imread(f)
    rawbox = boxcut(raw)
    icons, nums = iconcut(rawbox)
    t5, t4, t3 = [],[],[]
    for i, icon in enumerate(icons):
        globals()[tier(icon)].append(numread(nums[i]))
    if cc == 0:
        datadf = datadf.append({'uid':uid,'t5':sum(t5),'t4':sum(t4),'t3under':sum(t3)},ignore_index=True)
    else:
        subdf = subdf.append({'uid':uid,'main_uid':mainid,'t5':sum(t5),'t4':sum(t4),'t3under':sum(t3)},ignore_index=True)
    if j%20==0:
        print(j)
        datadf.to_csv(f'{basedir}maindata.csv',encoding="utf-8-sig")
        subdf.to_csv(f'{basedir}subdata.csv',encoding="utf-8-sig")