import os

path = '/users/arpit.bahety/trees_test_videos/GH017801/clipped_videos/'
dirs = os.listdir( path )
count = 0
for item in dirs:
    if item.endswith('.mp4'):
        os.system('python detect.py --source ' + path + item + ' --weights runs/train/exp7/weights/best.pt')

