import h5py
import scipy.io as io
import PIL.Image as Image
import numpy as np
import os
import glob
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter
import scipy
import json
import torchvision.transforms.functional as F
from matplotlib import cm as CM
from skimage.feature import peak_local_max as plm
from image import *
from model import CSRNet
from model1 import CSRNet1
import torch
from matplotlib import cm as c
from torchvision import datasets, transforms
import cv2
from torch.autograd import Variable


transform=transforms.Compose([
                       transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
                   ])
# model = CSRNet()
# #defining the model
# model = model.cuda()
# #loading the trained weights


model = CSRNet()
# pretrained = torch.load(r"D:\renqun\share_newdas\das\csrnet_mask\new_mask.tar")
pretrained = torch.load(r"D:\renqun\share_newdas\das\mask_depth2\mask_depth.tar")
# pretrained = torch.load(r"D:\renqun\share_newdas\das\mask_depth2\0model_best.pth.tar")
model = model.cuda()
model.load_state_dict(pretrained['state_dict'])

mask_model = CSRNet1()
# pretrained = torch.load(r"D:\renqun\share_newdas\das\csrnet_mask\new_mask.tar")
pretrained = torch.load(r"D:\renqun\share_newdas\das\mask_depth2\mask_depth.tar")
# pretrained = torch.load(r"D:\renqun\share_newdas\das\mask_depth2\0model_best.pth.tar")
mask_model = mask_model.cuda()
mask_model.load_state_dict(pretrained['state_dict'])



#checkpoint = torch.load(r"/public/home/aceukas6qi/das/mask_depth/mask_depth.tar")
#model.load_state_dict(checkpoint['state_dict'])


pic_num = 30
img_path = r"D:\renqun\share_newdas\das\shanghai\part_A_final/test_data/images/IMG_{}.jpg".format(pic_num)
#img = "/home/ch/SH_A/test_data/images/IMG_1.jpg"

temp = h5py.File(img_path.replace('.jpg','.h5').replace('images','ground_truth'), 'r')

temp_1 = np.asarray(temp['density'])
print("Original Count : ",int(np.sum(temp_1)) + 1)


img1 = Image.open(img_path).convert('RGB')
img = transform(img1).cuda()
print(img.shape)
print(img.unsqueeze(0))

# output,mask = model(img.unsqueeze(0))
# num = int(output.detach().cpu().sum().numpy())

# get depth
gt_path = img_path.replace('.jpg', '.h5').replace('images', 'ground_truth')
gt_file = h5py.File(gt_path)
depth_target = np.asarray(gt_file['density'])
depth_target = np.clip(depth_target, 0, 50)
depth_target = np.min(depth_target) + np.max(depth_target) - depth_target
depth_target = depth_target  # -depth_target
depth_target = cv2.resize(np.float32(depth_target),(int(depth_target.shape[1]/8),int(depth_target.shape[0]/8)),interpolation = cv2.INTER_AREA)

depth = depth_target

model.eval()
mask_model.eval()
num = 0     #预计人数

img = img.cuda()
img = Variable(img)

output1, mask1 = mask_model(img)
# output1 = output1/10
mask1 = torch.where(mask1 > 0.01, 1, 0)
output1 = torch.where(output1 > 0.01, 1, 0)
depth = torch.Tensor(depth).type(torch.FloatTensor).unsqueeze(0).cuda() * output1

# output, mask = model(img, mask1, depth)
output, mask = model(img, depth,mask1)
# num = int((output.data.sum()/10).cpu().numpy())
num = int((output.data.sum()).cpu().numpy())


output = np.asarray(output.detach().cpu().reshape(output.detach().cpu().shape[1],output.detach().cpu().shape[2]))
print(output)

new_img = plt.imread(img_path)
plt.imshow(new_img)
# plt.show()

img_test = Image.open(img_path).convert('RGB')
img_test2 = transform(img_test)

# test_1 = output
# test_1.fill(1)
# loc_output= test_1 - output     #取反




# new_output = cv2.resize(np.float32(output),(img_position.shape[1],img_position.shape[0]),interpolation = cv2.INTER_AREA)
# new_output = cv2.resize(np.float32(output),(img_position.shape[1],img_position.shape[0]))
# local_max = plm(temp_1, min_distance=2, num_peaks=num, exclude_border=False)
local_max = plm(output, min_distance=1, num_peaks=num, exclude_border=False)
img_position = np.zeros((output.shape[0], output.shape[1], 3))
print(local_max)
# img_position = img.cpu.numpy()

# img_position = output

print(img_position.shape)
print(output.shape)
for loc in local_max:
    # for x in range(loc[0] - 9, loc[0] + 8):
    #     for y in range(loc[1] - 9, loc[1] + 8):
    for x in range(loc[0], loc[0]+1):
        for y in range(loc[1], loc[1]+1):
            # img_position[0, x, y] = 255
            # img_position[1, x, y] = 255
            # img_position[2, x, y] = 255
            img_position[x, y, 0] = 255
            img_position[x, y, 1] = 255
            img_position[x, y, 2] = 255
            # img_position[x, y] = 1.0

print(img_position)
# img_position = img_position.permute(1,2,0) #交换维度

# signedPath = '预测点标注' + '.bmp'
# cv2.imshow('预测点标注', img_position)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
print("Predicted Count : ", num)

# print(img_position.detach().cpu().shape)
# img_position = np.asarray(img_position.detach().cpu().reshape(img_position.detach().cpu().shape[1],img_position.detach().cpu().shape[2]))

plt.axis('off')
plt.imshow(img_position)

# plt.show()
plt.savefig("output_position{}.jpg".format(pic_num),dpi=300,bbox_inches='tight', pad_inches=0)


local_max = plm(temp_1, min_distance=1, num_peaks=num, exclude_border=False)
print(local_max)
# img_position = img.cpu.numpy()
img_position = np.array(img_test)
# img_position = output
img_position.fill(0)
# print(img_position)
print(img_position.shape)
print(output.shape)
for loc in local_max:
    # for x in range(loc[0] - 9, loc[0] + 8):
    #     for y in range(loc[1] - 9, loc[1] + 8):
    for x in range(loc[0]-3, loc[0]+4):
        if x > img_position.shape[0]-1:
            continue
        for y in range(loc[1]-3, loc[1]+4):
            if y > img_position.shape[1]-1:
                continue
            # img_position[0, x, y] = 255
            # img_position[1, x, y] = 255
            # img_position[2, x, y] = 255
            img_position[x, y, 0] = 255
            img_position[x, y, 1] = 255
            img_position[x, y, 2] = 255
            # img_position[x, y] = 1.0

print(img_position)
# img_position = img_position.permute(1,2,0) #交换维度

# signedPath = '预测点标注' + '.bmp'
# cv2.imshow('预测点标注', img_position)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
print("Predicted Count : ", num)

# print(img_position.detach().cpu().shape)
# img_position = np.asarray(img_position.detach().cpu().reshape(img_position.detach().cpu().shape[1],img_position.detach().cpu().shape[2]))

plt.axis('off')
plt.imshow(img_position)

# plt.show()
plt.savefig("gt_output_position{}.jpg".format(pic_num),dpi=300,bbox_inches='tight', pad_inches=0)

#img = "/home/ch/csrnet_yanmo/1.jpg"
#img1 = plt.imread(img)


# output = np.asarray(output.detach().cpu().reshape(output.detach().cpu().shape[2],output.detach().cpu().shape[3]))
# print(output.detach().cpu().shape[0])

# output = np.asarray(output.detach().cpu().reshape(output.detach().cpu().shape[1],output.detach().cpu().shape[2]))
plt.axis('off');
plt.imshow(output, cmap = c.jet)
plt.savefig("output{}.jpg".format(pic_num),dpi=300,bbox_inches='tight', pad_inches=0)


