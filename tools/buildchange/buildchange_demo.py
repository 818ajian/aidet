import os
import cv2
import numpy as np
import mmcv
import wwtool
import pandas as pd
import argparse
import pycocotools.mask as maskUtils

from mmdet.apis import init_detector, inference_detector, show_result

def parse_args():
    parser = parser = argparse.ArgumentParser(description='DOTA Testing')
    parser.add_argument('--dataset', default='buildchange', help='dataset name')
    parser.add_argument('--dataset_version', default='v1', help='dataset name')
    parser.add_argument('--config_version', default='mask_rcnn_r50_fpn_1x_buildchange', help='version of experiments (DATASET_V#NUM)')
    parser.add_argument('--imageset', default='val_xian', help='imageset of evaluation')
    parser.add_argument('--epoch', default=12, help='epoch')
    parser.add_argument('--show', action='store_true', help='show flag')
    parser.add_argument('--save', action='store_false', help='show flag')

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    # config and result files
    config_file = './configs/{}/{}.py'.format(args.dataset, args.config_version)
    checkpoint_file = './work_dirs/{}/epoch_{}.pth'.format(args.config_version, args.epoch)
    img_dir = './data/{}/v1/{}/images'.format(args.dataset, args.imageset)
    save_path = './results/{}/{}/vis'.format(args.dataset, args.config_version)
    mmcv.mkdir_or_exist(save_path)
    
    print(config_file)
    model = init_detector(config_file, checkpoint_file, device='cuda:0')

    img_list = os.listdir(img_dir)
    prog_bar = mmcv.ProgressBar(len(img_list))

    firstfile = True
    for img_name in img_list:
        if img_name.endswith('xml'):
            continue
        print(img_name)
        img_file = os.path.join(img_dir, img_name)
        img = cv2.imread(img_file)
        if args.show:
            wwtool.show_image(img, win_name='original')
        bbox_result, segm_result = inference_detector(model, img)
        bboxes = np.vstack(bbox_result)
        if len(bboxes) == 0:
            continue
        if args.save:
            img_fn = img_name.split('.')[0]
            img_format = img_name.split('.')[1]
            out_file = os.path.join(save_path, img_fn + '_vis.' + img_format)
        else:
            out_file = None
        model.CLASSES = ('building',)
        print(out_file)
        show_result(mmcv.bgr2rgb(img), (bbox_result, segm_result), model.CLASSES, show=args.show, score_thr=0.5, out_file=out_file)
        # wwtool.imshow_bboxes(img, bbox_result[0][:, 0:-1], show=True)
