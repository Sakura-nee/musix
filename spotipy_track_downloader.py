from __future__ import unicode_literals
import youtube_dl
from youtube_search import YoutubeSearch
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
import requests
from pprint import pprint
from mutagen.easyid3 import EasyID3, ID3
from mutagen.id3 import APIC as AlbumCover, USLT, COMM as Comment

class MyLogger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		print(msg)


def my_hook(d):
	if d['status'] == 'finished':
		print('Done downloading, now converting ...')


def download_yt(url, name):
	ydl_opts = {
		'format': 'bestaudio/best',
		'outtmpl': name + '.%(ext)s',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		'logger': MyLogger(),
		'progress_hooks': [my_hook],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])

def _set_id3_mp3(converted_file_path, url):
	audio_file = EasyID3(converted_file_path)
	audio_file = embed_cover(audio_file, converted_file_path, url)
	audio_file.save(v2_version=3)
	
def embed_cover(audio_file, file, imgurl):
	audio_file = ID3(file)
	rawAlbumArt = requests.get(imgurl).content
	audio_file["APIC"] = AlbumCover(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=rawAlbumArt)
	return audio_file

urn = 'spotify:track:3D8dMWN3O6hbIlts9FXi9Z'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="af2a4d3485b64a0597be745b8ce5ffe2", client_secret="441a934a78844eecb438b129edb3f626"))

track = sp.track(urn)
artist = track['album']['artists']
if len(artist) == 1 or len(artist) < 1:
	artists_name = artist[0]['name']
else:
	artists_name = ''
	for artist_name in artist:
		name = artist_name['name']
		artists_name += name + ', '
	if artists_name.endswith(', '):
		artists_name = artists_name[:-2]

album_art = track['album']['images'][0]['url']
track_name = track['name'] + ' - ' + artists_name

get_youtube_info = YoutubeSearch(track_name, max_results=1).to_dict()[0]
youtube_url = 'https://www.youtube.com' + get_youtube_info['url_suffix']
duration = get_youtube_info['duration']
download_yt(youtube_url, track_name)
_set_id3_mp3(track_name + '.mp3', album_art)
