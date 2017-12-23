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

print("Processing ", "123")
# easy 0 10 12 13 18 19 20
# hard 1 2 4 6 9 11 8
# small 7 17
ori_img = cv2.imread("DotImage/17.jpg")
img = imgReshape(ori_img)
hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
target = hsv[:,:,2]
plt.subplot(231)
plt.imshow(target)

# clean background
bg = cv2.GaussianBlur(target, (151,151), 0)
no_bg = cv2.subtract(target, bg)
plt.subplot(232)
plt.imshow(bg)

# remove border
blur = cv2.GaussianBlur(no_bg, (15,15), 0)
th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                           cv2.THRESH_BINARY_INV, 15, 1)
th_di = cv2.dilate(th, diskCreate(3))
border_remove = cv2.subtract(blur, np.uint8(th_di / 255 * 100))
plt.subplot(233)
plt.imshow(border_remove)

# binarize
blur = cv2.GaussianBlur(border_remove, (15,15), 0)
remove_small = cv2.morphologyEx(blur, cv2.MORPH_OPEN, diskCreate(7))
tar_gray = cv2.equalizeHist(remove_small)
# ret, thresh = cv2.threshold(sub, 0, 255, cv2.THRESH_OTSU)
ret, thresh = cv2.threshold(tar_gray, 243, 255, cv2.THRESH_BINARY)

# filter
filt = []
ret, markers = cv2.connectedComponents(thresh)
plt.subplot(234)
plt.imshow(markers)
for i in range(1, ret):
    dot_size = np.sum(markers == i)
    if dot_size < 200 or dot_size > 1000:
        markers[markers == i] = 0
    else:
        ind = np.where(markers == i)
        sx = np.min(ind[1])
        ex = np.max(ind[1])
        sy = np.min(ind[0])
        ey = np.max(ind[0])
        if 1.5 >= (ex-sx) / (ey-sy) >= 0.5:
            filt.append([i, ind])
            # cv2.rectangle(img, (sx,sy), (ex,ey), (0,255,0), 2)
        else:
            markers[ind] = 0

# convolution
fl_bg = np.array(target, dtype=np.float)
ss = []
for i, ind in filt:
    border_width = (np.max(ind[0]) - np.min(ind[0])) // 2
    sx = np.min(ind[0]) - border_width
    ex = np.max(ind[0]) + border_width
    sy = np.min(ind[1]) - border_width
    ey = np.max(ind[1]) + border_width

    # pix_all = fl_bg[sx:ex, sy:ey].flatten()
    # s = (np.sum(pix_all) - np.sum(fl_bg[ind])) / (len(pix_all) - len(ind[0])) - np.sum(fl_bg[ind]) / len(ind[0])
    ret, test_ostu = cv2.threshold(target[sx:ex, sy:ey], 0, 255, cv2.THRESH_OTSU)
    s = np.sum(test_ostu == 255) / len(ind[0])
    print(i)
    print(s)
    if 0 < s < 3:
        cv2.rectangle(img, (sy,sx), (ey,ex), (0,255,0), 2)
    ss.append(s)

plt.subplot(235)
plt.hist(ss)

plt.subplot(236)
plt.imshow(img)


plt.show()
sys.exit()
