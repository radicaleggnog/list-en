######################################################
# List-en creates public playlists based on monthly 
# top posts in musical subreddits
#
######################################################
import sys
#Reddit wrapper
import praw
#Spotify wrapper
import spotipy
import spotipy.util as util

if len(sys.argv) < 2:
	sys.exit("Usage: python list-en.py username subreddit")

#Spotify username
username = sys.argv[1]

#Spotify setup
scope = 'playlist-modify-public'
token = util.prompt_for_user_token(username, scope)
if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
else:
    print("Can't get token for", username)

#useragent stuff
user_agent = ("Best of music subreddits by /u/radicaleggnog")
r = praw.Reddit(user_agent=user_agent)

#Get the subreddit
subreddit = sys.argv[2]
try:
    submissions = r.get_subreddit(subreddit, fetch="true").get_top_from_month(limit=99)
#If getting the subreddit fails, exit cleanly
except praw.errors.InvalidSubreddit:
    sys.exit("Invalid subreddit!")

#List of sites likely to have songs on spotify
acceptable_sites = ("youtube","soundcloud", "bandcamp")

#track to add
tracks = []
#Playlist to use
playlist_id = ""

#Function to get the playlist id. Returns the ID
def getPlaylistID():
    #Get all playlists
    playlists = sp.user_playlists(username)
    #Find the right one
    for playlist in playlists['items']:
        if(playlist['name'] == subreddit):
            #We found it! Now return it!
            return str(playlist['id'])

#Try to get the playlist id
playlist_id = getPlaylistID()

#if that failed, make a new playlist for it
if not playlist_id:
    #make the playlist
    sp.user_playlist_create(username, subreddit, public=True)
    #get the playlist id for the new playlist
    playlist_id = getPlaylistID()

#The heavy lifting
for x in submissions:
    #Convert to a string so we can compare it to the filters above
    str(x)
    #If it's from an acceptable site
    if any(s in x.url.lower() for s in acceptable_sites):
        #Search for it
        results = sp.search(x.title, 1)
        for i, t in enumerate(results['tracks']['items']):
            #add it to the list of tracks to add
            tracks.append(t['id'])                                  

#Add the tracks
sp.user_playlist_replace_tracks(username, playlist_id, tracks)
