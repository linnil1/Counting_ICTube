import cv2
import numpy as np
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

# [0,4,5,8,10,16]
# [6,15]
# for name in [6,15]: #[0,4,5,8,10,16]:
name = 0
ori_img = cv2.imread("RectImage/0{:02}.jpg".format(name))
img = imgReshape(ori_img)
blur = cv2.GaussianBlur(img, (15,15), 0)
for i in range(3):
    blur = cv2.GaussianBlur(blur, (15,15), 0)
hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
target = hsv[:,:,0]

## get target range
lower_blue = np.array([110,50,50])
upper_blue = np.array([130,255,255])
mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

# Background removing
mask_blue_di = cv2.dilate(mask_blue, diskCreate(101)) # be fatter
mask_blue_contour = maxContourFind(mask_blue_di)
mask_blue_hull = cv2.convexHull(mask_blue_contour)
extract_hsv = np.dstack([contourMask(hsv[:,:,0], mask_blue_hull),
                         contourMask(hsv[:,:,1], mask_blue_hull),
                         contourMask(hsv[:,:,2], mask_blue_hull)])

# Green Target
lower_green = np.array([75,100,50])
upper_green = np.array([95,255,255])
extract_target = cv2.inRange(extract_hsv, lower_green, upper_green)

# one by one watershed
num_marker, markers = cv2.connectedComponents(extract_target)
oldmarkers =markers.copy()
num = 0

for i in range(1, num_marker):
    ind = np.where(oldmarkers == i)
    if len(ind[0]) < 500:
        continue

    border_width = (np.max(ind[0]) - np.min(ind[0])) // 5
    sx = np.min(ind[0]) - border_width
    ex = np.max(ind[0]) + border_width
    sy = np.min(ind[1]) - border_width
    ey = np.max(ind[1]) + border_width

    # distance transform
    one_comp = oldmarkers[sx:ex, sy:ey] == i
    compon_dis = cv2.distanceTransform(one_comp.astype(np.uint8), cv2.DIST_L2, 5)
    _, dis_peak = cv2.threshold(compon_dis, 0.75 * compon_dis.max(), 255, 0)

    # watershed
    ret, new_markers = cv2.connectedComponents(dis_peak.astype(np.uint8))
    new_markers = new_markers + 1
    new_markers[(one_comp == True) & (new_markers == 1)] = 0
    water = cv2.watershed(img[sx:ex, sy:ey], new_markers.copy())

    # draw
    # plt.imshow(new_markers)
    # plt.show()
    for j in range(2, ret + 1):
        c = cv2.findContours(np.uint8(water == j), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        if len(c):
            c = c[0]
        else:
            continue
        c[:,0,0] += sy
        c[:,0,1] += sx
        cv2.drawContours(img, [c], -1, (0, 0, 255), 5)
        cv2.putText(img, str(num), (int(c[:,0,0].mean()), int(c[:,0,1].mean())), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 5)
        num = num + 1
    for j in range(2, ret + 2):
        markers[sx:ex, sy:ey][np.where(water == j)] = j

plt.subplot(221)
plt.imshow(hsv)
plt.subplot(222)
plt.imshow(markers)
plt.subplot(223)
plt.imshow(oldmarkers)
plt.subplot(224)
plt.imshow(img)
cv2.imwrite("image37.jpg", img)
plt.show()
