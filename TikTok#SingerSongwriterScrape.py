#!/usr/bin/env python
# coding: utf-8

# In[61]:


# # SingerSongwriter Scrape

import pandas as pd
import re
from tikapi import TikAPI, ValidationException, ResponseException
from datetime import datetime, timedelta
from openpyxl import load_workbook
import os

# Initialize TikAPI
api = TikAPI("API KEY HERE")

# Function to convert Unix timestamp to a readable format
def unix_to_readable(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Get today's date and calculate the date two months ago
today = datetime.today()
two_months_ago = today - timedelta(days=60)

# Create a filename with the format 'SingerSongwriterMM.DD.YY.xlsx'
file_path = f'/Users/jw/Downloads/SingerSongwriter{today.strftime("%m.%d.%y")}.csv'

# List to hold all the extracted data
data = []

# Variable to track the last cursor value
last_cursor = None

try:
    # Fetch posts by hashtag (example: 'singersongwriter')
    response = api.public.hashtag(name="singersongwriter")
    
    # Extract the hashtag ID
    hashtagId = response.json()['challengeInfo']['challenge']['id']
    
    # Fetch the posts under that hashtag
    response = api.public.hashtag(id=hashtagId)

    # Loop through posts in the response
    while response:
        # Check if 'itemList' exists in the response
        response_json = response.json()
        if 'itemList' in response_json:
            # If there are no posts, break the loop
            if not response_json['itemList']:
                break

            # Extract the post data
            for item in response_json['itemList']:
                author = item['author']
                author_stats = item['authorStats']
                stats = item['statsV2']
                music = item['music']

                # Extract relevant data with default values to avoid NoneType errors
                unique_id = author.get('uniqueId', '')
                nickname = author.get('nickname', '')
                nickname = re.sub(r'[^A-Za-z0-9 ~]', '', nickname)
                bio = author.get('signature', '')
                like_count = stats.get('diggCount', 0)
                follower_count = author_stats.get('followerCount', 0)
                create_time = item.get('createTime', 0)
                create_time_dt = datetime.utcfromtimestamp(create_time)
                sec_uid = author.get('secUid', '')
                total_likes = author_stats.get('heartCount', 0)
                total_videos = author_stats.get('videoCount', 0)
                play_count = stats.get('playCount', 0)
                comment_count = stats.get('commentCount', 0)
                share_count = stats.get('shareCount', 0)
                sound_id = music.get('id', 0)

                if create_time_dt > two_months_ago:
                    likes_per_video = total_likes / total_videos if total_videos > 0 else 0
                    likes_per_follower = total_likes / follower_count if follower_count > 0 else 0
                    millions_of_likes = total_likes / 1_000_000
                    engagement_rate_per_post = (int(like_count) + int(comment_count) + int(share_count)) / int(play_count) if int(play_count) > 0 else 0
                    engagement_to_follower_ratio = (int(like_count) + int(comment_count) + int(share_count)) / int(follower_count) if int(follower_count) > 0 else 0

                    data.append([unique_id, nickname, bio, like_count, follower_count, sec_uid, total_likes, 
                                 total_videos, play_count, comment_count, share_count, likes_per_video, 
                                 likes_per_follower, millions_of_likes, engagement_rate_per_post, 
                                 engagement_to_follower_ratio, create_time_dt, sound_id])

        cursor = response_json.get('cursor')
        if cursor:
            if cursor == last_cursor:
                print(f"Cursor stuck at {cursor}. Breaking the loop.")
                break
            print(f"Getting next items with cursor: {cursor}")
            last_cursor = cursor
            response = api.public.hashtag(id=hashtagId, cursor=cursor)
        else:
            break

except ValidationException as e:
    print(e, e.field)
except ResponseException as e:
    print(e, e.response.status_code)

# Convert the list of data to a DataFrame
df_new = pd.DataFrame(data, columns=['uniqueId', 'nickname', 'bio', 'LikeCount', 'followerCount', 'secUid', 'totalLikes', 
                                 'totalVideos', 'playCount', 'commentCount', 'shareCount', 'likesPerVideo', 
                                 'likesPerFollower', 'millionsOfLikes', 'engagementRatePerPost', 
                                 'engagementToFollowerRatio', 'createTime', 'sound_id'])

# Check if the file already exists
if os.path.exists(file_path):
    # Load the existing data
    df_existing = pd.read_csv(file_path)
    # Append the new data to the existing data
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
else:
    # If the file doesn't exist, use the new data as the combined data
    df_combined = df_new

# Write the combined DataFrame to the CSV file
df_combined.to_csv(file_path, index=False)

print(f"Data appended to {file_path}")

# Read the CSV file
data = pd.read_csv(file_path)

# Get rows and columns
rows, columns = data.shape

print(f"Rows: {rows}, Columns: {columns}")


import pandas as pd
from datetime import datetime

# Get today's date in the format YYYY-MM-DD
today = datetime.today().strftime('%m.%d.%y')

# Define file paths with today's date
file_path = f'/Users/jw/Downloads/SingerSongwriter{today}.csv'
output_path = f'/Users/jw/Downloads/SingerSongwriter{today}.csv'

# Load the Excel file
df = pd.read_csv(file_path)

# Drop duplicate rows based on the 'sound_id' column
df_cleaned = df.drop_duplicates(subset='sound_id')

# Save the cleaned data back to a new Excel file
df_cleaned.to_csv(output_path, index=False)

print(f"Duplicate rows removed and saved to {output_path}")


import pandas as pd
from datetime import datetime
import os

# Define today's date
today = datetime.today().strftime('%m.%d.%y')

# Load Data
file_path = f'/Users/jw/Downloads/SingerSongwriter{today}.csv'
df = pd.read_csv(file_path)

# Ensure sound_id is treated as a string
df['sound_id'] = df['sound_id'].astype(str).str.strip()

# TikAPI logic
results = []
invalid_ids = []

for sound_id in df['sound_id']:
    try:
        # Use the sound_id directly as in the original code
        response = api.public.musicInfo(id=sound_id)
        data = response.json()
        
        # Extract desired fields
        music_info = data.get('musicInfo', {})
        author = music_info.get('author', {})
        music_dict = music_info.get('music', 'N/A')
        nickname = music_dict.get('authorName', 'N/A')
        stats = music_info.get('stats', {})
        video_count = stats.get('videoCount', 'N/A')
        
        # Append results
        results.append({'sound_id': sound_id, 'nickname': nickname, 'video_count': video_count})
    except ValidationException as e:
        invalid_ids.append(sound_id)
        print(f"Validation error for sound_id {sound_id}: {e}")
    except Exception as e:
        print(f"Unexpected error for sound_id {sound_id}: {e}")

# Log invalid IDs for further inspection
print("Invalid sound IDs:", invalid_ids)

# Save results to Excel (not CSV)
output_file = f'/Users/jw/Downloads/SoundInfoResults{today}SS.csv'
pd.DataFrame(results).to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
print(f"Results saved to {output_file}")


# In[ ]:




