from YT_functions import *
from helpers.excel_helper import excel_writer
#this module extracts all the videos from the channel and writes them
#into an Excel file

filenameDate = dates["filename_date"]
cnlId = ["UC3I2GFN_F8WudD_2jUZbojA"] #KEXP

cnlData = channel_query(cnlId)
cnlPlaylistId = cnlData[cnlId[0]]['Official Playlist ID']

playlistData = playlist_query([cnlPlaylistId])
#Maybe I should set some kind of a limiter, if there are too many videos?
#this function extracts all the videos from a channel
#this way we can get all the videos from the good sources
#that has only good metadata

playlistVideoList = dict_2_list(playlistData)
excel_writer(playlistVideoList, f"playlistVideos_{filenameDate}")

