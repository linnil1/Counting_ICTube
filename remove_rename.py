import os
import shutil

# remove
dirs = sorted(os.listdir())
jsons_jpg = [i[:-5] + '.jpg' for i in dirs if i.endswith('.json')]
print(jsons_jpg)

for i in dirs:
    if i.endswith('.jpg') and i not in jsons_jpg:
        os.remove(i)
    else:
        print("OK", i)

# rename
dirs = sorted(os.listdir())
names = [i[:-5] for i in dirs if i.endswith('.json')]
ind = 0

for i in names:
    name = "web_{:03}".format(ind)
    ind += 1
    print(name)
    shutil.copyfile(i + '.jpg', name + '.jpg')
    shutil.copyfile(i + '.json', name + '.json')
