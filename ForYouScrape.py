#!/usr/bin/env python
# coding: utf-8

# In[137]:


# ForYouScrape

shortlist = []
import pandas as pd
import re
import csv
import datetime
from os.path import exists
from collections import defaultdict
from tikapi import TikAPI, ValidationException, ResponseException

# Initialize TikAPI with your API key
api = TikAPI("API KEY HERE")
User = api.user(
    accountKey="ACCOUNT KEY HERE"
)

# Get today's date in MM.DD.YY format
today = datetime.datetime.today().strftime('%m.%d.%y')

# Create a filename with the format 'ForYouScrapeMM.DD.YY.csv'
filename = f'/Users/jw/Downloads/ForYouScrape{today}.csv'

try:
    # Fetch the response from TikAPI
    response = User.posts.explore()
    data = response.json()

    # Calculate the cutoff for videos from the last two months
    now = datetime.datetime.utcnow()
    two_months_ago = now - datetime.timedelta(days=60)

    # Dictionaries to count occurrences of unique IDs and sound IDs
    sound_id_counts = defaultdict(int)
    unique_id_counts = defaultdict(int)

    # Check if the file exists and read existing counts
    file_exists = exists(filename)
    if file_exists:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                sound_id = row.get('sound ID', '')
                unique_id = row.get('uniqueId', '')
                if sound_id:
                    sound_id_counts[sound_id] = int(row.get('sound count', 0))
                if unique_id:
                    unique_id_counts[unique_id] = int(row.get('unique ID count', 0))

    # Open the file in append mode
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write the header if the file is new
        if not file_exists:
            writer.writerow([
                'uniqueId', 'nickname', 'bio', 'LikeCount', 'followerCount',
                'createTime (UTC)', 'secUid', 'play count', 'total likes', 'total videos',
                'sound ID', 'sound creator', 'sound title',
                'sound count', 'unique ID count', 'likes per video',
                'likes per follower', 'millions of likes',
                'engagement rate per post', 'engagement-to-follower ratio', 'shortlist'
            ])

        # Iterate over the data
        for item in data.get('itemList', []):
            # Extract and filter by creation time
            create_time_unix = item.get('createTime', 0)
            create_time = datetime.datetime.utcfromtimestamp(create_time_unix)

            # Skip videos older than two months
            if create_time < two_months_ago:
                continue

            # Extract other relevant fields
            author = item.get('author', {})
            author_stats = item.get('authorStats', {})
            music = item.get('music', {})
            stats = item.get('statsV2', {})
            
            unique_id = author.get('uniqueId', '')
            nickname = author.get('nickname', '')

            # Remove non-alphabetical, non-numeric characters except spaces and `~`
            nickname = re.sub(r'[^A-Za-z0-9 ~]', '', nickname)

            like_count = stats.get('diggCount', 0)
            follower_count = author_stats.get('followerCount', 0)
            create_time_str = create_time.strftime('%Y-%m-%d %H:%M:%S')  # Convert to readable format
            sec_uid = author.get('secUid', '')
            bio = author.get('signature', '')
            total_likes = author_stats.get('heartCount', 0)
            total_videos = author_stats.get('videoCount', 0)
            play_count = stats.get('playCount', 0)
            comment_count = stats.get('commentCount', 0)
            share_count = stats.get('shareCount', 0)

            # Extract sound details
            sound_id = music.get('id', '')
            sound_creator = music.get('authorName', '')
            sound_title = music.get('title', '')

            # Update counts
            if sound_id:
                sound_id_counts[sound_id] += 1
            if unique_id:
                unique_id_counts[unique_id] += 1

            # Calculate additional metrics
            likes_per_video = total_likes / total_videos if total_videos > 0 else 0
            likes_per_follower = total_likes / follower_count if follower_count > 0 else 0
            millions_of_likes = total_likes / 1_000_000
            engagement_rate_per_post = (int(like_count) + int(comment_count) + int(share_count)) / int(play_count) if int(play_count) > 0 else 0
            engagement_to_follower_ratio = (int(like_count) + int(comment_count) + int(share_count)) / int(follower_count) if follower_count > 0 else 0

            # Check if the uniqueId is in the shortlist
            is_shortlisted = 1 if unique_id in shortlist else 0

            # Write the data row
            writer.writerow([
                unique_id, nickname, bio, like_count, follower_count,
                create_time_str, sec_uid, play_count, total_likes, total_videos,
                sound_id, sound_creator, sound_title,
                sound_id_counts[sound_id], unique_id_counts[unique_id],
                round(likes_per_video, 2), round(likes_per_follower, 2),
                round(millions_of_likes, 2), round(engagement_rate_per_post, 4),
                round(engagement_to_follower_ratio, 4), is_shortlisted
            ])

    print(f"Data has been written to {filename}")
    
    csv_file = f'ForYouScrape{today}.csv'
    data = pd.read_csv(csv_file)

    # Get rows and columns
    rows, columns = data.shape

    print(f"Rows: {rows}, Columns: {columns}")

except ValidationException as e:
    print("Validation Error:", e, e.field)

except ResponseException as e:
    print("Response Error:", e, e.response.status_code)
    

import pandas as pd
from datetime import datetime

# Get today's date in the format mm.dd.yy
today = datetime.today().strftime('%m.%d.%y')

# Define file paths with today's date
file_path = f'/Users/jw/Downloads/ForYouScrape{today}.csv'
output_path = f'/Users/jw/Downloads/ForYouScrape{today}.csv'

# Load the CSV file
df = pd.read_csv(file_path)

# Drop duplicate rows based on the 'sound_id' column
df_cleaned = df.drop_duplicates(subset='sound ID')

# Save the cleaned data back to a new CSV file
df_cleaned.to_csv(output_path, index=False)

print(f"Duplicate rows removed and saved to {output_path}")


import pandas as pd
from datetime import datetime

# Load data from CSV
today = datetime.today().strftime('%m.%d.%y')

# Load data
file_path = f'/Users/jw/Downloads/ForYouScrape{today}.csv'
df = pd.read_csv(file_path)

# Ensure sound_id is treated as a string
df['sound ID'] = df['sound ID'].astype(str).str.strip()

# TikAPI logic
results = []
invalid_ids = []

for sound_id in df['sound ID']:
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

# Save results to CSV
output_file = f'/Users/jw/Downloads/SoundInfoResults{today}FYS.csv'
pd.DataFrame(results).to_csv(output_file, index=False)
print(f"Results saved to {output_file}")

