# Rumor has it soundcloud is hemoraging money and will
# shut down by Dec 2017 at the latest
# http://www.musicbusinessworldwide.com/soundcloud-may-run-out-of-cash-this-year-as-it-posts-e51m-loss/
# This is my backup plan.

# script accepts a username
# and downloads all tracks "liked" by the user as mp3s to the same directory

#    .-+-.
#   / RIP \
#   |     |
#  \\     |//

# RIP Soundcloud, I will seriously miss you <3

import argparse
import urllib2
import json
import io
import os

# if this API key stops working
# it's very easy to find another on github
# just search for "soundcloud client id"
# https://github.com/search?q=soundcloud+client+id&type=Code

API_KEY = '955a528f998da6dd6a40b57db962ab06'
ROOT_URL = 'https://api.soundcloud.com'


def get_username_from_args():
    # Parse arguments to get username
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='soundcloud username')
    args = parser.parse_args()
    if not args.username:
        raise Exception('Must provide username')
    return args.username


def get_user_id_from_username(username):
    # Request user info from API by username
    api_url = '{root_url}/users/{username}?client_id={api_key}'.format(root_url=ROOT_URL, username=username, api_key=API_KEY)
    api_response = urllib2.urlopen(api_url).read()
    user_json = json.loads(api_response)
    return user_json.get('id')


def download_users_favorite_tracks(user_id):
    # Download a list of the users favorite tracks by user id
    # Max limit of 200 results per page
    total_downloaded = 0
    next_url = '{root_url}/users/{user_id}/favorites?client_id={api_key}&linked_partitioning=1&page_number=0&page_size=200'.format(root_url=ROOT_URL, user_id=user_id, api_key=API_KEY)
    while next_url:
        api_response = urllib2.urlopen(next_url).read()
        favorites_json = json.loads(api_response)
        total_downloaded += download_tracks_from_response_json(favorites_json)
        next_url = favorites_json.get('next_href')
    return total_downloaded


def download_tracks_from_response_json(response_json):
    download_count = 0
    for item in response_json.get('collection'):
        if item.get('stream_url'):
            filename = generate_safe_filename('{artist} - {title}'.format(artist=item['user'].get('username').encode('utf-8'), title=item.get('title').encode('utf-8')))
            print 'Downloading "{}"'.format(filename)
            download_track(filename, item.get('stream_url'))
            download_count += 1
    return download_count


def generate_safe_filename(filename):
    return filename.replace('/', '-').replace(':', '-')


def download_track(filename, url):
    # if the file does not exist, download it
    if not os.path.isfile('{}.mp3'.format(filename)):
        api_url = '{track_url}?client_id={api_key}'.format(track_url=url, api_key=API_KEY)
        api_response = urllib2.urlopen(api_url, timeout=3600).read()
        with io.FileIO('{}.mp3'.format(filename), 'w') as file:
            file.write(api_response)
    return filename


if __name__ == '__main__':
    username = get_username_from_args()
    user_id = get_user_id_from_username(username)
    download_users_favorite_tracks(user_id)
