import crop as cp
import os

f = []
count = 1

for (path, subdirs, filenames) in os.walk('data'):
    for filename in filenames:
        if filename.startswith('large1000'):
            imagefile = os.path.join(path, filename)
            print "processing " + imagefile
            cp.compare_crop(imagefile, 'compare/' + str(count)+'.png')
            print '\n'
            count += 1



