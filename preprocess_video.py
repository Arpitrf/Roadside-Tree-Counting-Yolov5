import gpxpy
import pandas as pd
import haversine as hs
import pickle
import folium
import os
import webbrowser
import numpy as np

def process_gpx_to_df(filename, path, save_path):
	gpx = gpxpy.parse(open(path+filename)) 
	#(1)make DataFrame
	track = gpx.tracks[0]
	segment = track.segments[0]
	# Load the data into a Pandas dataframe (by way of a list)
	data = []
	segment_length = segment.length_3d()
	for point_idx, point in enumerate(segment.points):
		data.append([point.longitude, point.latitude,point.elevation,
		point.time, segment.get_speed(point_idx)])
		columns = ['Longitude', 'Latitude', 'Altitude', 'Time', 'Speed']
		gpx_df = pd.DataFrame(data, columns=columns)

	#2(make points tuple for line)
	points = []
	for track in gpx.tracks:
		for segment in track.segments: 
			for point in segment.points:
				points.append(tuple([point.latitude, point.longitude]))

	# Saving df and points to a file
	gpx_df.to_pickle(save_path + 'data.pickle')
	with open(save_path + 'points.txt', 'wb') as file:
		pickle.dump(points, file)

	return gpx_df, points

def generate_clipped_videos(df, points, time_range, filename, path_for_os, save_path, save_path_for_macOS):
	input_video_filename = path_for_os + filename
	filename = filename.split('.')[0]
	# Create new folder: "clipped_videos" inside save_path
	os.system('mkdir ' + save_path_for_macOS + 'clipped_videos/')
	steps = int(df.shape[0] / time_range)
	start_time = 0
	end_time = 0
	# dictionary of keys: segmented video filename & value: list of GPS coordinates of that segment
	dict_split = {}
	for i in range(steps):
		# Getting the split in the df and points list
		start = i * time_range
		end = (i + 1) * time_range
		points_split = points[start:end]
		df_split = df[start:end]

		#trim video and save
		duration_split = df_split.iloc[-1]['Time'] - df_split.iloc[0]['Time']
		duration_split = duration_split / np.timedelta64(1,'s')
		end_time = end_time + duration_split
		output_filename = filename + '_' + str(i) + '.mp4'
		output_path = save_path_for_macOS + 'clipped_videos/' + output_filename
		print(output_filename)
		os.system('ffmpeg -i ' + input_video_filename + ' -ss ' + str(start_time) + ' -to ' + str(end_time) + ' -c:v copy -c:a copy ' + output_path)

		#filename and add to dict
		dict_split[output_filename] = points_split
		start_time = end_time

	# In case the legnth of df.shape[0] is not perfectly divisible by time_range
	if int(df.shape[0] / time_range) != df.shape[0] / time_range:
	    # Getting the split in the df and points list
	    start = (i + 1) * time_range
	    end = len(points)
	    points_split = points[start:end]
	    df_split = df[start:end]
	    
	    #trim video and save
	    duration_split = df_split.iloc[-1]['Time'] - df_split.iloc[0]['Time']
	    duration_split = duration_split / np.timedelta64(1,'s')
	    end_time = end_time + duration_split
	    output_filename = filename.split('.')[0] + '_' + str(i+1) + '.mp4'
	    output_path = save_path_for_macOS + 'clipped_videos/' + output_filename
	    print(output_filename)
	    os.system('ffmpeg -i ' + input_video_filename + ' -ss ' + str(start_time) + ' -to ' + str(end_time) + ' -c:v copy -c:a copy ' + output_path)
	    
	    #filename and add to dict
	    dict_split[output_filename] = points_split
	    start_time = end_time
  
	print(dict_split.keys()) 
	with open(save_path + 'dict.txt', 'wb') as file:
		pickle.dump(dict_split, file)
		# print("Last: ", df_split.shape, len(points_split))


# -- Hyperparameters & Initializations Start --

# time of the clipped videos: 120 seconds or 2 mins
clipped_time = 120000
# time between each GPS measurement in GoPro
interval = 55
# time_range: length of the segment in the gpx df or points list will cover 120 seconds
time_range = int(clipped_time / interval)

# Path to the folder which contains the video
video_path = '/Volumes/My Passport/treeCountingVideos/trip4/Main Video/'
# This is only needed because certain folder names have spaces. If in case there are no spaces in your folder names, keep this the same as video_path
video_path_for_macOS = '/Volumes/My\ Passport/treeCountingVideos/trip4/Main\ Video/'

gpx_filename = 'GH017756.gpx'
video_filename = 'GH017756.MP4'

# -- Hyperparameters & Initializations End --

# Make directory with the same name as the video file. i.e. if video file = GH101.mp4 then folder name is GH101
os.system('mkdir ' + video_path_for_macOS + video_filename.split('.')[0])
save_path = video_path + video_filename.split('.')[0] + '/'
save_path_for_macOS = video_path_for_macOS + video_filename.split('.')[0] + '/'

# Step 1: Put information in the gpx file into a gpx_df and points
print("Starting step 1")
if not os.path.exists(save_path + 'points.txt'):
	gpx_df, points = process_gpx_to_df(gpx_filename, video_path, save_path)

# Step 2: Clip videos into smaller equal time videos. the duration of the smaller video is given by "clipped_time" variable
print("Starting step 2")
df = pd.read_pickle(save_path + 'data.pickle')
with open (save_path + 'points.txt', 'rb') as file:
	points = pickle.load(file)
	generate_clipped_videos(df, points, time_range, video_filename, video_path_for_macOS, save_path, save_path_for_macOS)
	# distance = calculate_distance(points)
	# display(df, points, distance, tree_count)





