import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt

def diskCreate(x):
    disk = np.zeros([x, x], np.uint8)
    midx = x//2
    for i in range(x):
        nowi = min(i, x - 1 - i)
        for j in range(midx - nowi, midx + nowi + 1):
            disk[i][j] = 1;
    return disk

def imgReshape(img):
    normal_img = img
    # reshpae
    if img.shape[0] > img.shape[1]:
        l = np.min(img.shape[:2]) / 2
        M = cv2.getRotationMatrix2D((l, l), 90, 1)
        normal_img = cv2.warpAffine(img, M, (img.shape[0], img.shape[1]))
    normal_img = cv2.resize(normal_img, (1478, 1108))
    return normal_img

name = "5"
if True:
# for name in "1 2 4 5 6 7 9 11 14 15 17 19".split():
    ori_img = cv2.imread("DotImage/" + name + ".jpg")
    img = imgReshape(ori_img)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    target = cv2.inRange(hsv, np.array([25,180,10]), np.array([40,255,240]))
    tar_di = cv2.dilate(target, diskCreate(9))
    ret, markers = cv2.connectedComponents(tar_di)


    for i in range(1, ret):
        ind = np.where(markers == i)
        sx = np.min(ind[1])
        ex = np.max(ind[1])
        sy = np.min(ind[0])
        ey = np.max(ind[0])
        cv2.rectangle(img, (sx,sy), (ex,ey), (0,255,0), 2)

    plt.subplot(221)
    plt.imshow(hsv)
    plt.subplot(222)
    plt.imshow(hsv[:,:,0])
    plt.subplot(223)
    plt.imshow(tar_di)
    cv2.imwrite("image24.jpg", tar_di)
    plt.subplot(224)
    cv2.imwrite("image25.jpg", img)
    plt.imshow(img)
    plt.show()
