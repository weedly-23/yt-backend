import sqlite3
from sqlite3 import Error

def get_db():
    sql = sqlite3.connect('db/repertoire.db')
    sql.row_factory = sqlite3.Row
    return sql

def select_query(query_string, fetchall=True):
    db = get_db()
    cur = db.execute(query_string)
    if fetchall:
        result_query = cur.fetchall()
    else:
        result_query = cur.fetchone()
    return result_query



def chart_2_dict(chart, Nones_Excluded=True):
    headers = chart[0][1:]
    body = chart[1:]
    final_dict = {}
    index = 1
    for row in body:
        if row[0]:
            cnl_id = row[0]
        else:
            cnl_id = index
            index+=1
        row_dict = dict(zip(headers,row[1:]))
        if Nones_Excluded:
            #There will be no particular ker in the final dict if the value of the key is None
            #That is needed in order not to substitute non-empty values with None values.
            row_dict = {k:v for k, v in row_dict.items() if v}
        final_dict[cnl_id] = row_dict
    return final_dict

def chart_2_list_of_dicts(chart, Nones_Excluded=True, nones_convert_to_empty_str=False):
    final_list = []
    headers = chart[0]
    for row in chart[1:]:
        row_dict = dict(zip(headers, row))
        if Nones_Excluded:
            final_row = {k:v for k, v in row_dict.items() if v!=None}
        elif nones_convert_to_empty_str:
            for key in row_dict:
                if row_dict[key] == None:
                    row_dict[key] = ""
            final_row = row_dict
        else:
            final_row = row_dict
        final_list.append(final_row)
    return final_list


def db_update_query(dict):
    return



def main_select_channels():
    db = get_db()
    cur = db.execute("""
    select 
    channel_id
    from yt_channels 
    where 
    priority = 'TOP' 
    or 
    priority = 'OK'
    or 
    priority is NULL
    ORDER BY
    total_views DESC;""")
    data_obj = cur.fetchall()
    ids = [i['channel_id'] for i in data_obj]
    return ids

def best_sources_channels():
    db = get_db()
    cur = db.execute("""
    SELECT 
        *
    FROM
        yt_channels 
    WHERE
        dri = 'VK'
    AND
        (priority = 'TOP' 
            OR
        priority = 'OK')
    AND
        (metadata_quality = '1')
    AND
        (country <> "IN")
    AND
        live_status = "live"
    AND
        source_type = "channel"
    ORDER BY
        dri ASC,
        country DESC,
        priority DESC,
        metadata_quality ASC,
        total_views DESC
    LIMIT
        10
    ;""")
    data_obj = cur.fetchall()
    ids = {
        i['source_id']: [i['source_title'], i['priority'], i['genre'], i['dri'], i['metadata_quality'], i['country']] for i in data_obj
    }
    return ids

def explore_channels():
    db = get_db()
    cur = db.execute("""
    SELECT 
        *
    FROM
        yt_channels 
    WHERE
        dri = 'VK'
    AND
        (country <> "IN" AND country <> "BR" and country <> "MX")
    AND
        live_status = "live"
    AND
        source_type = "channel"
    AND
        priority is null
    AND
        videos_count > 150
    ORDER BY
        total_views DESC
    LIMIT 10;""")
    data_obj = cur.fetchall()
    ids = {
        i['source_id']: [i['source_title'], i['priority'], i['genre'], i['dri'], i['metadata_quality'], i['country']] for i in data_obj
    }
    return ids



def processed_videos_list():
    db = get_db()
    videos_processed_cur = db.execute("""select video_id from videos_processed""")
    videos_processed = videos_processed_cur.fetchall()
    videos_processed_list = [i["video_id"] for i in videos_processed]
    return videos_processed_list


processed_videos_list_from_db = processed_videos_list()


def playlists_db_query():
    db = get_db()
    cur = db.execute("""
    SELECT *
    FROM yt_channels
    WHERE source_type <> "channel";    
    """)
    data_obj = cur.fetchall()
    ids = {
        i['source_id']: {
            "source title": i['source_title'],
            "source_id": i['source_id'],
            "metadata_quality": i['metadata_quality'],
            "genre": i['genre'],
            "priority": i['priority'],
            "country": i['country'],
            "dri": i['dri']
        } for i in data_obj
    }
    return ids

if __name__ == '__main__':
    playlists_db_query()