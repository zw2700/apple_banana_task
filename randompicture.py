import random
import os
import random
import numpy as np

pathes = './picture/'
total_list = []
for root, dirs, files in os.walk(pathes):
    # print('root', root)
    # print('dirs', dirs)
    # print('files', files)
    for f in files:
        total_list.append(root + '/' + f)
# print(total_list)
# disrupt the order
random.shuffle(total_list)


def get_picture():
    """get random picture"""
    pic = random.choice(total_list)
    while '.DS_Store' in pic:
        pic = random.choice(total_list)
    return pic


def get_position(max_w, max_h,width, height):
    if max_w < width or max_h < height:
        return 0, 0

    lst_x = [i for i in range(0, max_w-width)]
    lst_y = [i for i in range(0, max_h-height)]
    random.shuffle(lst_x)
    random.shuffle(lst_y)
    x = random.choice(lst_x)
    y = random.choice(lst_y)

    # if max_w-x < 210 and y < 40:
    #     x = 40
    #     y = 0
    if x < 40 and y < 40:
        x = 40

    return x, y
    
def generate_size(width,height):
    size_lst = [0.25, 0.5, 1, 2,3, 4, 6]
    scale = random.choice(size_lst)
    lbl_width, lbl_height = (width*scale, height*scale)
    while lbl_width<100 or lbl_width>1000 or lbl_height<100 or lbl_height>1000:
        scale = random.choice(size_lst)
        lbl_width, lbl_height = (width*scale, height*scale)
    return (int(lbl_width), int(lbl_height))



