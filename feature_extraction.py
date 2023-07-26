import os
import cv2
import torch
from lightglue import DISK
from tqdm import tqdm
import numpy as np

torch.set_grad_enabled(False)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
extractor = DISK(max_num_keypoints=2048).eval().to(device)  # load the extractor

img_dir = './ystad_kloster/'
images = sorted( filter( lambda x: os.path.isfile(os.path.join(img_dir, x)), os.listdir(img_dir) ) )

text_file = open("output/img_list.txt", "wt")

all_feats = []
all_points = []

for i in tqdm(range(len(images))):
    if images[i].split('.')[-1] in ['JPG', 'jpg', 'PNG', 'png', 'RAW', 'raw', 'TIF', 'tif']:
        text_file.write(images[i] + '\n')
        img = cv2.imread(img_dir + images[i])
        if img.shape[1] < img.shape[0]:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        img_ = img.transpose((2, 0, 1))
        img_tensor = torch.tensor(img_ / 255., dtype=torch.float)
        feats = extractor.extract(img_tensor.to(device))
        feats_ = feats['descriptors'].cpu().detach().numpy()
        points = feats['keypoints'].cpu().detach().numpy()
        all_points.append(points[0])
        all_feats.append(feats_[0])

all_descriptors = np.stack(all_feats)
all_points = np.stack(all_points)

text_file.close()
np.save('output/all_descriptors.npy', all_descriptors)
np.save('output/all_points.npy', all_points)



