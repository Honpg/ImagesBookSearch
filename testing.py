import os, re

a = 'https://cdn0.fahasa.com/media/catalog/product/thumbnailframe/product_frame_ncc/frame_biatu-duy-trieu-phu-01.jpg'

base_a = os.path.basename(a)

if re.search("frame", base_a):
     print("fail")
else:
     print(base_a)