import json
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import re
from helpers.metadata_wizard import global_replace
from helpers.db_helpers import get_db, processed_videos_list_from_db
from urllib.parse import unquote
from config import yt_api_key

ytApiKey = yt_api_key
ytBaseApi = "https://youtube.googleapis.com/youtube/v3/"
yt_rss_base = "https://www.youtube.com/feeds/videos.xml?channel_id="
yt_rss_playlist_base = "https://www.youtube.com/feeds/videos.xml?playlist_id="

replace_sheet = 'Replace List'

dates = {
    "cells_date": datetime.now().date(),
    "cells_date_str": datetime.now().strftime('%d.%m.%Y'),
    "filename_date": datetime.now().strftime('%y%m%d_%H-%M'),
    "sheetname_date": datetime.now().strftime('%d %M')
}

apiBaseUrl = {
    "channel": f"{ytBaseApi}channels?part=statistics&part=contentDetails&part=snippet&maxResults=50&id=",
    "video": f"{ytBaseApi}videos?part=contentDetails&part=snippet&part=statistics&maxResults=50&id=",
    "playlist": f"{ytBaseApi}playlistItems?part=contentDetails&part=snippet&maxResults=50&playlistId=",
    "mostPopular": f"{ytBaseApi}videos?part=contentDetails&part=snippet&chart=mostPopular&videoCategoryId=10&maxResults=50&regionCode=",
    "playlistStats": f"{ytBaseApi}playlists?part=contentDetails&part=snippet&maxResults=50&id=",
    "searchQuery": f"{ytBaseApi}search?part=snippet&regionCode=RU&type=video&videoDuration=short&videoDuration=medium&maxResults=50&q="
}
#https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2 -- use these country codes, create a good dict with big countries

mostPopular_example = "https://youtube.googleapis.com/youtube/v3/videos?part=snippet&chart=mostPopular&videoCategoryId=10&maxResults=50&regionCode=ru&key="+ytApiKey

# ------------------------------------------------
# -------Functions that work with strings and modify them using several methods---------------------
def yt_time(yt_time):
   if '.' in yt_time:
      yt_time = yt_time.split('.')[0]
   else:
      yt_time = yt_time.split('Z')[0]
   try:
      time = datetime.strptime(yt_time, '%Y-%m-%dT%H:%M:%S')
      time = time.replace(tzinfo=None)#deleting UTC offset so we can calculate how old the video is
   except:
      time = yt_time
   return time


def yt_duration(yt_dur):
    """
    https://en.wikipedia.org/wiki/ISO_8601#Durations
    :param yt_dur: "P2DT3H24M5S" is a possible input, where all the D/H/M/S are all optional
    :return: duration is returned as datetime length
    """
    duration_tuple = re.findall("P(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?", yt_dur)[0]
    dur_lst = []
    for el in duration_tuple:
        el = re.split("\D", el)[0]
        if not el:
            el = 0
        dur_lst.append(int(el))
    duration = timedelta(days = dur_lst[0], hours = dur_lst[1], minutes = dur_lst[2], seconds = dur_lst[3])
    return duration


def list_divider(list, size=50):
    """
    dividing the input list into evenly sized iterable.
    a list with 263 elements gives an output of six lists: five 50-element lists and one list with 13 elements
    :param list: a=[], the list that you need to split into batches of a certain size
    :param size: what's the size of a batch?
    :return:
    """
    for i in range(0, len(list), size):
        yield list[i:i + size]
#2) f(x) that takes a list of lists as an input and converts inside lists into long strings to pass to API request


def joiner(list, sep=","):
    res_chart=[]
    for el in list:
        joined_string=sep.join(el)
        res_chart.append(joined_string)
    return res_chart
#3) f(x) that combines 2 functions above and takes a list as an input and converts that into list of strings


def ids_to_str(initial_id_list):
    chunkedList = list(list_divider(initial_id_list))
    stringsList = joiner(chunkedList)
    return stringsList


def api_items(query,nextPageToken=False):
    json_response = requests.get(query)
    response = json.loads(json_response.text)
    items = response["items"]
    if nextPageToken == False:
        return items
    else:
        if "nextPageToken" in response:
            nextPageToken = response["nextPageToken"]
        else:
            nextPageToken = None
        itemCount = response["pageInfo"]["totalResults"]
        return items, nextPageToken, itemCount


def dict_plus_dict(dict1,dict2):
    finalDict = {}
    for key in dict1:
        newValuesDict = {}
        valueDict1 = dict1[key]
        for valueKey in valueDict1:
            newValuesDict[valueKey] = valueDict1[valueKey]
        if key in list(dict2.keys()):
            valueDict2 = dict2[key]
            for valueKey in valueDict2:
                newValuesDict[valueKey] = valueDict2[valueKey]
        finalDict[key] = newValuesDict
    return finalDict


def pl_latest_video(playlistIDs):#this should be changed, so the quota is not wasted!!!
    finalDict = {}
    ids = ids_to_str(playlistIDs)
    for element in ids:
        apiQuery = f"{apiBaseUrl['playlist']}{element}&key={ytApiKey}"
        print(apiQuery)
        items = api_items(apiQuery)
        latestItem = items[0]
        latestItemDict = {
            "Video ID": latestItem["contentDetails"]["videoId"],
            "Latest Video": latestItem["contentDetails"]["videoPublishedAt"],
            "Playlist ID": latestItem["snippet"]["playlistId"]
        }
        finalDict[latestItemDict["Playlist ID"]] = latestItemDict
    return finalDict


def channel_query(ids_list):
    finalDict = {}
    ids = ids_to_str(ids_list)
    q_counter = 0
    for element in ids:
        q_counter+=1
        apiQuery = f"{apiBaseUrl['channel']}{element}&key={ytApiKey}"
        print(apiQuery)
        items = api_items(apiQuery)
        for item in items:
            snip = item["snippet"]
            stats = item["statistics"]
            playlistID = item["contentDetails"]["relatedPlaylists"]["uploads"]
            if stats["hiddenSubscriberCount"] == True:
                subscriberCount = 'Hidden'
            else:
                subscriberCount = int(stats["subscriberCount"])
            cnlDict = {
                "Official Source": "channel",
                "Channel ID": item["id"],
                "Official Title": snip["title"],
                "Official Subscribers": subscriberCount,
                "Official Created": yt_time(snip["publishedAt"]),
                "Official Video Count": int(stats["videoCount"]),
                "Official Views": int(stats["viewCount"]),
                "Official Playlist ID": playlistID,
                "Official Channel Description": snip["description"],
                "live_status": "live"
                }
            finalDict[cnlDict["Channel ID"]] = cnlDict
    finalDictIds = list(finalDict.keys())
    for id in ids_list:
        if id not in finalDictIds:
            finalDict[id] = {
                "live_status": "NOT ACTIVE"
            }
    return finalDict

#in process!
def search_query(query_list):
    final_dict = {}
    for query in query_list:
        apiQuery = f"{apiBaseUrl['searchQuery']}{query}&key={ytApiKey}"
        print(apiQuery)
        items = api_items(apiQuery)
        for item in items:
            snip = item["snippet"]
            channel_id = snip["channelId"]
            channel_title = snip["channelTitle"]
            video_title = snip["title"]
            published = yt_time(snip["publishTime"])
            video_id = item["id"]["videoId"]
            final_dict[video_id] = {
                "source_id": channel_id,
                "source_title:": channel_title,
                "published": published,
                "video_title": video_title,
                "query": unquote(query),
                "video_id": video_id,
                "url_query": query
            }
    return final_dict


def cover_remix_live(song_title_string):
    cover_remix_live = ['live', 'remix','cover']
    result = 0
    for el in cover_remix_live:
        songTitle = song_title_string.upper()
        elUpper = el.upper()
        if elUpper in songTitle:
            result = el
            return result
        else:
            continue
    if result == 0:
        return None


def video_query(ids_list):
    finalDict = {}
    missingChannels = []
    ids = ids_to_str(ids_list)
    for element in ids:
        apiQuery = f"{apiBaseUrl['video']}{element}&key={ytApiKey}"
        print(apiQuery)
        items = api_items(apiQuery)
        for item in items:
            # print(f"{item['id']}")
            snip = item["snippet"]
            details = item["contentDetails"]
            stats = item["statistics"]
            loc = snip["localized"]
            commentsCount = int(stats.get("commentCount", -1))
            likeCount = int(stats.get("likeCount", -1))
            dislikeCount = int(stats.get("dislikeCount", -1))
            originalTitle = snip["title"]
            newMetadataDict = global_replace(originalTitle)
            artist = newMetadataDict["artist"]
            track = newMetadataDict["track"]
            newMetadata = newMetadataDict["overall"]
            db = get_db()
            cur = db.execute("""
            select metadata_quality, priority, country, genre, dri
            from yt_channels 
            where source_id = ?""",[snip["channelId"]])
            cnl_db = cur.fetchone()
            if cnl_db:
                metadata_quality = cnl_db["metadata_quality"]
                genre = cnl_db["genre"]
                country = cnl_db["country"]
                priority = cnl_db["priority"]
                dri = cnl_db["dri"]
            else:
                missingChannels.append(snip["channelId"])
                metadata_quality = ""
                genre = ""
                country = ""
                priority = ""
                dri = ""
            if metadata_quality:
                try:
                    metadata_quality = int(metadata_quality)
                except:
                    print(metadata_quality)
            processed_status = (lambda x: "remove" if x in processed_videos_list_from_db else "ok")(item["id"])
            videoDict = {
                "Source": "video",
                "Video ID": item["id"],
                "Published": yt_time(snip["publishedAt"]),
                "Video Title": snip["title"],
                "New Title": newMetadata,
                "Track": track,
                "|": "|",
                "Artist": artist,
                "Artist - Track": f"{artist} - {track}",
                "Cover-Rmx-Live": cover_remix_live(snip["title"]),
                "Duration": yt_duration(details["duration"]),
                "License": details["licensedContent"],
                "Channel Name": snip["channelTitle"],
                "Channel ID": snip["channelId"],
                "Category": int(snip["categoryId"]),
                "Loc Title": loc["title"],
                "Description": snip["description"],
                "Loc Description": loc["description"],
                "Views": int(stats.get("viewCount", -1)), #-1 means data not available
                "Likes": likeCount,
                "Dislikes": dislikeCount,
                "Comments": commentsCount,
                "metadata_quality": metadata_quality,
                "genre": genre,
                "country": country,
                "priority": priority,
                "dri": dri,
                "processed_status": processed_status
            }
            finalDict[videoDict["Video ID"]] = videoDict
    return finalDict


def playlist_query(ids_list, pageLimit = None):
    finalDict = {}
    for element in ids_list:
        apiQuery = f"{apiBaseUrl['playlist']}{element}&key={ytApiKey}"
        print(apiQuery)
        nextPageToken = True
        pageIndex = 1
        if not pageLimit:
            pageLimit = 500
        while nextPageToken and pageIndex <= pageLimit:
            items, nextPageToken, itemCount = api_items(apiQuery, nextPageToken=True)
            # print(apiQuery)
            items, nextPageToken, itemCount = api_items(apiQuery, nextPageToken=True)
            for item in items:
                snip = item["snippet"]
                details = item["contentDetails"]
                playlistDict = {
                    "video_id": details["videoId"],
                    "position": snip["position"],
                    "source_type": "playlist",
                    "playlist_id": snip["playlistId"],
                    "playlist_name": snip["channelTitle"],
                    "total_video_count": itemCount
                }
                # print(playlistDict)
                finalDict[playlistDict["video_id"]] = playlistDict
            apiQuery = f"{apiBaseUrl['playlist']}{element}&pageToken={nextPageToken}&key={ytApiKey}"
            pageIndex += 1
    videosID = list(finalDict.keys())
    videoDict = video_query(videosID)

    bad_ids = {}
    for id in videosID:
        if id not in videoDict:
            bad_ids[id] = finalDict.pop(id)
    print(f"There is/are {len(bad_ids)} Bad IDs: {', '.join(list(bad_ids.keys()))}")
    finalDict = dict_plus_dict(finalDict,videoDict)
    return finalDict


def most_popular_query(country_list):
    finalDict = {}
    # countryCounter = 0
    for element in country_list:
        # countryCounter+=1
        # counter = 0
        print(f"Country: {element}")
        apiQuery = f"{apiBaseUrl['mostPopular']}{element}&key={ytApiKey}"
        nextPageToken = True
        while nextPageToken != None:
            items, nextPageToken, itemCount = api_items(apiQuery, nextPageToken=True)
            for item in items:
                snip = item["snippet"]
                details = item["contentDetails"]
                loc = snip["localized"]
                mostPopularDict = {
                    "Source": "Popular",
                    "Video ID": item["id"],
                    "Publisehd": snip["publishedAt"],
                    "Video Title": snip["title"],
                    "Channel ID": snip["channelId"],
                    "Channel Name": snip["channelTitle"],
                    "Category": snip["categoryId"],
                    "Duration": details["duration"],
                    "License": details["licensedContent"],
                    "Loc Title": loc["title"],
                    "Description": snip["description"],
                    "Loc Description": loc["description"],
                    "Video count": itemCount
                }
                finalDict[mostPopularDict["Video ID"]] = mostPopularDict
                # counter+=1
                # print(f"{countryCounter}.{counter}: {mostPopularDict['Video ID']}:::{mostPopularDict['Video Title']}, country: {element}")
            apiQuery = f"{apiBaseUrl['mostPopular']}{element}&pageToken={nextPageToken}&key={ytApiKey}"
    videosID = list(finalDict.keys())
    videoDict = video_query(videosID)
    finalDict = dict_plus_dict(finalDict, videoDict)
    return finalDict


def most_popular_query_2(country_list):
    finalDict = {}
    # countryCounter = 0
    for element in country_list:
        # countryCounter+=1
        # counter = 0
        print(f"Country: {element}")
        apiQuery = f"{apiBaseUrl['mostPopular']}{element}&key={ytApiKey}"
        nextPageToken = True
        while nextPageToken != None:
            items, nextPageToken, itemCount = api_items(apiQuery, nextPageToken=True)
            for item in items:
                snip = item["snippet"]
                details = item["contentDetails"]
                loc = snip["localized"]
                mostPopularDict = {
                    "Source": "Popular",
                    "Video ID": item["id"],
                    "Publisehd": snip["publishedAt"],
                    "Video Title": snip["title"],
                    "Channel ID": snip["channelId"],
                    "Channel Name": snip["channelTitle"],
                    "Category": snip["categoryId"],
                    "Duration": details["duration"],
                    "License": details["licensedContent"],
                    "Loc Title": loc["title"],
                    "Description": snip["description"],
                    "Loc Description": loc["description"],
                    "Video count": itemCount
                }
                finalDict[mostPopularDict["Video ID"]] = mostPopularDict
                # counter+=1
                # print(f"{countryCounter}.{counter}: {mostPopularDict['Video ID']}:::{mostPopularDict['Video Title']}, country: {element}")
            apiQuery = f"{apiBaseUrl['mostPopular']}{element}&pageToken={nextPageToken}&key={ytApiKey}"
    return finalDict


def html_soup(url,containers_html_tag=None):
    with requests.Session() as session:
        myClient = urlopen(url)
        page_html = myClient.read()
        myClient.close()
        page_soup = BeautifulSoup(page_html, "html.parser")
        if containers_html_tag == None:
            return page_soup
        else:
            try:
                items = page_soup.findAll(containers_html_tag)
            except:
                items = None
            return items


def rss_xml_main(ids_list):
    finalDict = {}
    base_rss_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
    for id in ids_list:
        id = base_rss_url+id
        videos = html_soup(id, containers_html_tag = 'entry')
        for video in videos:
            videoDict = {
                "Video ID": video.find("yt:videoid").text,
                "Channel ID": video.find("yt:channelid").text,
                "Video Title": video.find("media:title").text,
                "Video Link": video.find("link").get("href"),
                "Channel Name": video.find("name").text,
                "Channel Link": video.find("uri").text,
                "Published": video.find("published").text,
                "Description": video.find("media:description").text,
                "Views Count": video.find("media:statistics").get("views"),
                "Rating": video.find("media:starrating").get("average")
            }
            finalDict[videoDict["Video ID"]] = videoDict
            print(videoDict["Video ID"])
    videosIDs = list(finalDict.keys())
    videoExtraDict = video_query(videosIDs)
    finalDict = dict_plus_dict(finalDict, videoExtraDict)
    return finalDict

def rss_xml_main_2(ids_list):
    finalDict = {}
    base_rss_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
    for id in ids_list:
        id = base_rss_url+id
        videos = html_soup(id, containers_html_tag = 'entry')
        for video in videos:
            videoDict = {
                "Video ID": video.find("yt:videoid").text,
                "Channel ID": video.find("yt:channelid").text,
                "Video Title": video.find("media:title").text,
                "Video Link": video.find("link").get("href"),
                "Channel Name": video.find("name").text,
                "Channel Link": video.find("uri").text,
                "Published": video.find("published").text,
                "Description": video.find("media:description").text,
                "Views Count": video.find("media:statistics").get("views"),
                "Rating": video.find("media:starrating").get("average")
            }
            finalDict[videoDict["Video ID"]] = videoDict
    return finalDict

def rss_xml_main_latest_video(ids_list):
    finalDict = {}
    base_rss_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
    for id in ids_list:
        try:
            xml_url = base_rss_url + id
            videos = html_soup(xml_url, containers_html_tag='entry')
            video = videos[0]
            videoDict = {
                "Latest ID": video.find("yt:videoid").text,
                "Video Title": video.find("media:title").text,
                "Latest Date": yt_time(video.find("published").text),
            }
        except:
            videoDict = {
                "Latest ID": "NOT ACTIVE",
                "Video Title": "NOT ACTIVE",
                "Latest Date": "NOT ACTIVE",
            }
        finalDict[id] = videoDict
        print(videoDict["Latest ID"])
    return finalDict


def dict_2_list(input_dict):
    finalList = []
    mainKeyList = list(input_dict.keys())
    #print(mainKeyList)
    headers = list(input_dict[mainKeyList[0]].keys())
    #print(headers)
    finalList.append(headers)
    for mainKey in mainKeyList:
        #print(mainKey)
        valuesList = list(input_dict[mainKey].values())
        finalList.append(valuesList)
    return finalList


def video_output_template(input_dict):
    outputDict = input_dict
    outputDict["Published"] = yt_time(outputDict["Published"])

def proper_yt_id(input_string):
    """
    the function gets youtube urls, channel ids, playlist ids and converts them into the proper
    standard ID form: "UC...." or "UU...." (24 characters string); or "PL...." (34 character string)
    :param input_string:
    :return:
    """
    patterns = [re.compile(r'U[UC][^&=]{22}'),
                re.compile(r'PL[^&=]{32}'),
                re.compile(r'RD[^&=]{41}')]
    for p in patterns:
        my_search = p.search(input_string)
        if my_search:
            break
        else:
            continue
    if my_search:
        proper_yt_id = my_search.group()
        proper_yt_id = re.sub('^UU', 'UC', proper_yt_id)
        return proper_yt_id
    try:
        yt_content = requests.get(input_string.strip()).content
        soup = BeautifulSoup(yt_content, "html.parser")
        channel_url = soup.select_one("link[rel='canonical']").get("href")
        channel_id = channel_url.split('/')[-1]
        if channel_id != "null" and channel_url != input_string:
            return channel_id
        channel_tag = soup.select_one("meta[itemprop='channelId']")
        channel_id = channel_tag.get('content')
        return channel_id
    except:
        return f"Problem with INPUT: {input_string}"

def proper_video_id(input_string):
    input_string = str(input_string)
    patterns = [re.compile(r'v=[^?/=&.]{11}'), re.compile(r'[^ ?/=&.]{11}')]
    for p in patterns:
        my_search = p.search(input_string)
        if my_search:
            break
        else:
            continue
    if my_search:
        proper_video_id = my_search.group()
        proper_video_id = re.sub("v=","", proper_video_id)
        return proper_video_id
    else:
        print(f"Problem with INPUT: {input_string}")



def plyalists_stats(playlist_ids):
    finalDict = {}
    # playlist_ids = [proper_yt_id(i) for i in playlist_ids]
    ids = ids_to_str(playlist_ids)
    q_counter = 0
    for element in ids:
        q_counter+=1
        apiQuery = f"{apiBaseUrl['playlistStats']}{element}&key={ytApiKey}"
        print(apiQuery)
        items = api_items(apiQuery)
        for item in items:
            snippet = item["snippet"]
            playlist_id = item["id"]
            publishDate = snippet["publishedAt"]
            try:
                channelId = snippet["channelId"]
                channelTitle = snippet["channelTitle"]
            except:
                channelId = "Unlisted"
                channelTitle = "Unlisted"
            title = snippet["title"]
            videosCount = item["contentDetails"]['itemCount']
            playlist_row = {
                "source_type": "playlist",
                "playlist_id": playlist_id,
                "created": yt_time(publishDate),
                "playlist_title": title,
                "videos_count": videosCount,
                "channelId": channelId,
                "channelTitle": channelTitle,
                "live_status": "live"
                }
            finalDict[playlist_id] = playlist_row
    finalDictIds = list(finalDict.keys())
    for id in playlist_ids:
        if id not in finalDictIds:
            finalDict[id] = {
                "live_status": "NOT ACTIVE"
            }
    return finalDict

def deduped_list(my_list):
    deduped_list = list(set(my_list))
    return deduped_list


if __name__ == "__main__":
    # a = proper_yt_id("https://www.youtube.com/c/%D0%90%D0%BB%D0%B5%D0%BA%D1%81%D0%B5%D0%B9%D0%9D%D0%B0%D0%B2%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B9")
    b = proper_yt_id("https://www.youtube.com/watch?v=mLTsNpUDYW4")
    # print(a)
    print(b)
    print("Boom boom")