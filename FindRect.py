import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt
import sys

ans_num = { 0:25, 4:18, 5:18, 6:30, 8:18, 10:35, 15:18, 16:18 }
num = 0
if len(sys.argv) == 1:
    img_num = [0,4,5,6,8,10,15,16]
    showOne = False
else:
    img_num = []
    for i in range(1, len(sys.argv)):
        num = int(sys.argv[i])
        img_num.append(num)
    if len(sys.argv) == 2:
        showOne = True
    else:
        showOne = False

size_min = 666

def diskCreate(x):
    disk = np.zeros([x, x], np.uint8)
    midx = x//2
    for i in range(x):
        nowi = min(i, x - 1 - i)
        for j in range(midx - nowi, midx + nowi + 1):
            disk[i][j] = 1;
    return disk

def maxContourFind(img):
    contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    max_cont = []
    max_area = 0
    for cont in contours:
        if cv2.contourArea(cont) > max_area:
            max_cont = cont
            max_area = cv2.contourArea(cont)
    return max_cont

def contourMask(img, cont):
    convex_img = np.zeros(img.shape)#, "bool")
    cv2.drawContours(convex_img, [cont], -1, (1), -2)
    convex_img = cv2.bitwise_and(img, img, mask=convex_img.astype(np.uint8))
    return convex_img

def mainProcess(img, showOne=False):
    ## sharpen image
    lapimg = cv2.Laplacian(img, cv2.CV_8U)
    lapimg = cv2.dilate(lapimg, diskCreate(11))
    lapimg = cv2.subtract(img, lapimg)

    ## get target range
    hsv = cv2.cvtColor(lapimg, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,200,200])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    # target condition
    green_target = cv2.inRange(hsv, np.array([77,180,10 ]), np.array([97,255,250])) | \
                   cv2.inRange(hsv, np.array([77,120,110]), np.array([97,230,250]))
    mask = mask | green_target 

    ## middle range and max range of target
    mask_close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, diskCreate(31))
    mask_max = cv2.dilate(mask_close, diskCreate(121)) # be fatter
    mask_mid = cv2.dilate(mask_close, diskCreate(81))
    hull_max = cv2.convexHull(maxContourFind(mask_max))

    ## our target
    convex_max = contourMask(green_target, hull_max)
    convex_max = cv2.GaussianBlur(convex_max, (15,15), 0)
    mask_binary = green_target > 0
    


    """
    white_target = hsv[:,:,2]
    convex_max = contourMask(white_target, hull_max)
    convex_max = cv2.GaussianBlur(convex_max, (15,15), 0)
    mask_binary = convex_max > 150
    """


    ## extract it
    extract_target = cv2.bitwise_and(convex_max, convex_max, mask=mask_binary.astype(np.uint8))
    extract_close = cv2.morphologyEx(extract_target, cv2.MORPH_CLOSE, diskCreate(11))
    extract_close = cv2.morphologyEx(extract_close, cv2.MORPH_OPEN, diskCreate(41))
    extract_compon = cv2.connectedComponents(extract_close)[1].astype(np.uint8)

    ## remove unwant between middle to max contour
    convex_notwant = extract_compon - contourMask(extract_compon, maxContourFind(mask_mid))
    compon_num = np.unique(convex_notwant[convex_notwant != 0])
    compon_want = extract_compon.copy()
    for i in compon_num:
        compon_want[compon_want == i] = 0

    ## remove not rect, not convex, small sizes
    candi_cont = []
    tar_img = lapimg.copy()
    tar_contours = cv2.findContours(compon_want, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    # sizes = []
    # size_min = np.mean(sizes) - size_mult * np.std(sizes)
    for c in tar_contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.01 * peri, True)
        rect = cv2.boxPoints(cv2.minAreaRect(c))
        # len(approx) >= 4
        # check if almost convex shape and sizes
        if cv2.contourArea(c) > cv2.contourArea(rect) * 0.5 and \
           cv2.contourArea(c) > size_min:
            # sizes.append(cv2.contourArea(c))
            candi_cont.append(approx)
        else:
            cv2.drawContours(tar_img, [approx], -1, (255, 0, 0), 2)

    ## distance transform
    compon_for_dis = np.zeros(img.shape[:2], np.uint8)
    cv2.drawContours(compon_for_dis, candi_cont, -1, (1), -2)
    compon_dis = cv2.distanceTransform(compon_for_dis, cv2.DIST_L2, 5)
    _, markers = cv2.threshold(compon_dis, min(20, 0.5 * compon_dis.max()), 255, 0)
    markers = np.uint8(markers)
    compon_unknown = cv2.subtract(compon_for_dis, markers)

    ## watershed
    ret, markers = cv2.connectedComponents(markers)
    markers = markers + 1
    markers[compon_unknown == 1] = 0
    water_img = np.stack([compon_for_dis,np.zeros(img.shape[:2], dtype=np.uint8),np.zeros(img.shape[:2], dtype=np.uint8)], 2)
    water = cv2.watershed(water_img, markers)
    water_ori = water.copy()

    num = 0
    for label in range(2, ret + 1):
        mask = np.zeros(water.shape, dtype="uint8")
        mask[water == label] = 255
        c = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1][0]
        M = cv2.moments(c)
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        cv2.drawContours(tar_img, [c], -1, (0, 0, 255), 5)
        cv2.putText(tar_img, str(num), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 0), 2)
        num += 1
            # if cv2.contourArea(c) > np.mean(sizes) + (size_mult - 1) * np.std(sizes):
            #     num += 1
            #     cv2.putText(tar_img, str(num), (cX, cY + 40), cv2.FONT_HERSHEY_SIMPLEX,
            #             1, (0, 0, 0), 2)

    if showOne:
        plt.subplot(231)
        plt.imshow(img)
        plt.subplot(232)
        plt.imshow(hsv)
        plt.title("hsv")
        plt.subplot(233)
        cv2.drawContours(convex_max, [maxContourFind(mask_max)], -1, (255, 0, 0), 2)
        cv2.drawContours(convex_max, [maxContourFind(mask_mid)], -1, (255, 0, 0), 2)
        cv2.drawContours(convex_max, [maxContourFind(mask_close)], -1, (255, 0, 0), 2)
        plt.imshow(convex_max)
        plt.title("three boundary and hsv-value")
        plt.subplot(234)
        plt.imshow(extract_close)
        plt.title("closeing")
        plt.subplot(235)
        plt.imshow(water_ori)
        plt.title("watershed")
        plt.subplot(236)
        plt.imshow(tar_img, interpolation='none')
        plt.title("result")
        print("Number : ",num)
        print("Ans : ", ans_num[now_name])
        return 0,0
    else:
        return tar_img, num

for now_num, now_name in enumerate(img_num):
    print("Processing ", now_name)
    img = cv2.imread("RectImage/{:03}.jpg".format(now_name))
    normal_img = img
    # reshpae
    if img.shape[0] > img.shape[1]:
        l = np.min(img.shape[:2]) / 2
        M = cv2.getRotationMatrix2D((l, l), 90, 1)
        normal_img = cv2.warpAffine(img, M, (img.shape[0], img.shape[1]))

    normal_img = cv2.resize(normal_img, (1478, 1108))

    tar_img, num = mainProcess(normal_img, showOne)
    if not showOne:
        plt.subplot(331 + now_num)
        plt.imshow(tar_img)
        plt.axis('off')
        plt.title("{}: {} vs {}(ANS)".format(now_name, num, ans_num[now_name]))

plt.show()
