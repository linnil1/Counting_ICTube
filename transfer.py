import glob
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from lxml import etree
import json
import os
import sys

# testing( move trainvalno5k to 5k manually)
# 006 015 020 037
# web_004 web014


def goPlot(img, txt):
    plt.imshow(img)
    cord = []

    for t in txt:
        labels = t
        h, w = img.shape[:2]
        x1 = w * (labels[1] - labels[3]/2)
        y1 = h * (labels[2] - labels[4]/2)
        x2 = w * (labels[1] + labels[3]/2)
        y2 = h * (labels[2] + labels[4]/2)
        print(labels[0], x1, y1, x2, y2)

        bbox = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
            linewidth=2, facecolor='none', edgecolor='blue')
        plt.gca().add_patch(bbox)

    plt.show()


# change format of label
xmls = os.listdir('ori')
# flist = open("trainvalno5k.txt", 'w')
flist = sys.stdout
for xml in xmls:
    name =  os.path.splitext(xml)[0]
    print(name)
    f = open('labels/' + name + '.txt', 'w')
    img = plt.imread("images/" + name + ".jpg")
    h, w = img.shape[:2]
    txt = []

    if xml.endswith('.xml'):
        tree = etree.parse('ori/' + xml)
        width = int(tree.xpath("//width")[0].text)
        height = int(tree.xpath("//height")[0].text)
        # print(width, height)
        for box in tree.xpath('//bndbox'):
            x1 = float(box.xpath('./xmin/text()')[0])
            x2 = float(box.xpath('./xmax/text()')[0])
            y1 = float(box.xpath('./ymin/text()')[0])
            y2 = float(box.xpath('./ymax/text()')[0])
            labels = [0, (x1 + x2) / 2 / w, (y1 + y2) / 2 / h, (x2 - x1) / w, (y2 - y1) / h]
            txt.append(labels)
            print("{} {:6f} {:6f} {:6f} {:6f}".format(*labels), file=f)
            # print("{} {:6f} {:6f} {:6f} {:6f}".format(*labels))

    else:  # endswith json
        tree = json.load(open('ori/' + xml))
        for box in tree['shapes']:
            x1, y1 = box['points'][0]
            x2, y2 = box['points'][1]
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            labels = [0, (x1 + x2) / 2 / w, (y1 + y2) / 2 / h, (x2 - x1) / w, (y2 - y1) / h]
            txt.append(labels)
            print("{} {:6f} {:6f} {:6f} {:6f}".format(*labels), file=f)

    if txt:
        print('/home/ubuntu/TI/images/' + name + '.jpg', file=flist)
    # goPlot(img, txt)


# show origin
"""
img = plt.imread("/home/share/yolo_coco/images/train2014/COCO_train2014_000000003040.jpg")
txt =       open("/home/share/yolo_coco/labels/train2014/COCO_train2014_000000003040.txt").readlines()
txt = list(map(lambda t: list(map(float, t.split())), txt))
goPlot(img, txt)

img = plt.imread("images/000.jpg")
txt =       open("labels/000.txt").readlines()
txt = list(map(lambda t: list(map(float, t.split())), txt))
goPlot(img, txt)
"""
