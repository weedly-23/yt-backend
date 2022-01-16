from helpers.db_helpers import best_sources_channels
from YT_functions import proper_video_id, playlist_query, plyalists_stats

db_best_query = best_sources_channels()

playlist_dict = playlist_query(['PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj'])

d = 'https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj'
a = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCzZ1I1j--g9sFVB-6-1yzWw'
b = 'https://www.youtube.com/playlist?list=UUBG-L0a5pkLE_OOrXHOx9hw'
c = 'UUBG-L0a5pkLE_OOrXHOx9hw'
e = 'https://www.youtube.com/channel/UCkaUg9b9LplVoJdx1JwwyOg/videos'
f = 'PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj'

playlist_id = "_NdGGUXDN3s"
a_video_id = proper_video_id(playlist_id)

a = plyalists_stats(playlist_id)



print('Hello world')