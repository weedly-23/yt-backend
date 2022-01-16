import re
from helpers.excel_helper import excel_reader
from helpers.db_helpers import chart_2_list_of_dicts
mainFolder = "/helpers/YoutubeMagicRSS.xlsx"

def white_title(string):
    """
    deleting excessive whitespace + if the title is all low or all UPPER changing it to proper title
    :param string:
    :return:
    """
    string = re.sub(' +', ' ', string).strip()
    if string.split('(')[0].islower() or string.split('(')[0].isupper():
        string = string.title()
    return string

def proper_case(string):
    if string.split('(')[0].islower() or string.split('(')[0].isupper():
        string = string.title()
    return string

def big_split(string, channel, split_chart):
    """
    splitting the string based on the rules for certain YT channels
    :param string: what metadata we want to change?
    :param channel: yt channel id in order to have specific "narrow" rules for concrete channels
    :param split_chart:
    :return:
    """
    for el in split_chart:
        if channel == el[0]:
            try:
                string = string.split(el[1])[el[2]]
            except:
                string = string
            break
    return string


def regex_repl(string, regex_chart):  # replacing using regex chart
    for rgx in regex_chart:
        string = re.sub(rgx[0], rgx[1], string)
    ##    print(string)
    return string

def generic_rules_cleaner():
    return None

def less_emoji(input_string):  # f(x) for deleting emojis
    EMOJI_PATTERN = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "])"
    )
    output_string = re.sub(EMOJI_PATTERN, ' ', input_string)
    return output_string

#This is the MASTER as of 13th May.
def metadata_input_check(input_string):
    if type(input_string) == dict:
        try:
            input_string = input_string["original_metadata"]
        except:
            print("Input string should be a string or dict with a key 'original metadata' or a list with 1 element")
    elif type(input_string) == list:
        if len(input_string) == 1:
            input_string = input_string[0]
    elif type(input_string) != str:
        return ("Check the type of the input!")
    return input_string

def channel_rules_fx(input_string, channel_rules):
    input_string = metadata_input_check(input_string)
    next_step_str = input_string
    log_chart = []
    for r in channel_rules:
        if r["separator"]:
            method = "separator"
            separator = str(r["separator"])
            if not r["part"]:
                part = 0
            else:
                part = r["part"]
                try:
                    if int(part) > 0:
                        part = int(part)-1
                    else:
                        part = 0
                except:
                    print("The part in the separtor method cannot be interpreted as a number")
            previous_step_str = next_step_str
            try:
                next_step_str = previous_step_str.split(separator)[part]
            except:
                next_step_str = previous_step_str.split(separator)[0]
                # print(f"We cannot separate {previous_step_str} by {separator} and take {part} from that")
            log_row = {
                "in": previous_step_str,
                "out": next_step_str,
                "method": method,
                "separator": separator,
                "part": part + 1
            }
            log_chart.append(log_row)
        if r["replace"]:
            replace_str = str(r["replace"])
            if r["with"]:
                with_str = r["with"]
            else:
                with_str = ""
            if r["regex"] == 1 or str(r["regex"])[0].lower() == 'y':
                method = "cnl_regex"
                previous_step_str = next_step_str
                next_step_str = re.sub(replace_str, with_str, previous_step_str)
                log_row = {
                    "in": previous_step_str,
                    "out": next_step_str,
                    "method": method,
                    "replace": replace_str,
                    "with": with_str
                }
                log_chart.append(log_row)
            else:
                method = "cnl_replace"
                previous_step_str = next_step_str
                next_step_str = previous_step_str.replace(replace_str, with_str)
                log_row = {
                    "in": previous_step_str,
                    "out": next_step_str,
                    "method": method,
                    "replace": replace_str,
                    "with": with_str
                }
                log_chart.append(log_row)
    new_metadata = next_step_str
    changes_chart_exclusive = [i for i in log_chart if i["in"] != i["out"]]
    final_dict = {
        "new_metadata": next_step_str,
        "changes": changes_chart_exclusive
    }
    return final_dict


def generic_rules_fx(input_string, generic_rules):
    input_string = metadata_input_check(input_string)
    for i in generic_rules:
        if not i["with"]:
            i["with"] = ""
    generic_regex_rules = [i for i in generic_rules if i['regex']]
    generic_replace_rules = [i for i in generic_rules if not i['regex']]

    next_step_str = input_string
    log_chart = []
    for r in generic_regex_rules:
        replace_str = r["replace"]
        with_str = r["with"]
        previous_step_str = next_step_str
        method = "generic_regex"
        next_step_str = re.sub(replace_str, with_str, previous_step_str)
        log_row = {
            "in": previous_step_str,
            "out": next_step_str,
            "method": method,
            "replace": replace_str,
            "with": with_str
        }
        log_chart.append(log_row)
    for r in generic_replace_rules:
        replace_str = r["replace"]
        with_str = r["with"]
        previous_step_str = next_step_str
        method = "generic_replace"
        next_step_str = previous_step_str.replace(replace_str, with_str)
        log_row = {
            "in": previous_step_str,
            "out": next_step_str,
            "method": method,
            "replace": replace_str,
            "with": with_str
        }
        log_chart.append(log_row)
    log_chart_exclusive = [i for i in log_chart if i["in"] != i["out"]]
    new_metadata = next_step_str
    final_dict = {
        "new_metadata": new_metadata,
        "changes": log_chart_exclusive
    }
    return final_dict

def less_spaces(input_string):
    try:
        input_string = str(input_string)
    except:
        print("Check type of the input!")
    output_string = " ".join(input_string.split())
    return output_string

def channel_and_generic_rules(input_string, channel_rules, generic_rules):
    input_string = less_emoji(input_string)
    input_string = less_spaces(input_string)
    if not channel_rules and not generic_rules:
        return ("No rules to apply --though it should be an impossible situation!")
    elif channel_rules and not generic_rules:
        result = channel_rules_fx(input_string, channel_rules)
    elif generic_rules and not channel_rules:
        result = generic_rules_fx(input_string, generic_rules)
    else:
        result = channel_rules_fx(input_string, channel_rules)
        input_string = result["new_metadata"]
        channel_rules_changes = result["changes"]
        result = generic_rules_fx(input_string, generic_rules)
        result["changes"] = channel_rules_changes + result["changes"]

    final_dict = {
        "new_metadata": less_spaces(result["new_metadata"]),
        "changes": result["changes"]
    }
    return final_dict


def big_replace(string, replace_chart):  # replacing one string with another using the replace chart
    mod_repl_chart = []
    for repl_pair in replace_chart:
        if len(mod_repl_chart) != 0:
            for mod_el in mod_repl_chart:
                repl_pair[0] = repl_pair[0].replace(mod_el[0], mod_el[1])
        mod_repl_chart.append(repl_pair)
        string = string.replace(repl_pair[0], repl_pair[1])
    return string

changes_template = {
    "original_metadata": "",
    "previous_iteration": "",
    "new_iteration": "",
    "rule_name": "",
    "regex": "",
    "replace": "",
    "with": ""
}


def del_emoji(input_string):  # f(x) for deleting emojis
    EMOJI_PATTERN = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "])"
    )
    output_string = re.sub(EMOJI_PATTERN, ' ', input_string)
    return output_string

def input_replace_chart():
    excel_path = '/Users/viktorkertanov/Library/Mobile Documents/com~apple~CloudDocs/Documents/repertoire/Metadator.xlsx'
    generic_replace = 'generic_replace'
    generic_replace_excel = excel_reader(excel_path, generic_replace)
    generic_rules = chart_2_list_of_dicts(generic_replace_excel, Nones_Excluded=False)
    return generic_rules

standard_replace_chart = input_replace_chart()


def generic_replace_function(metadata, replace_chart):
    for rule in replace_chart:
        if not rule['with']:
            rule['with'] = ""
    regex_rules = [i for i in replace_chart if i['regex']]
    standard_replace = [i for i in replace_chart if not i['regex'] and i['replace']]
    original_metadata = metadata
    previous_iteration_metadata = metadata
    changes_list = []
    for rule in regex_rules:
        metadata = re.sub(rule['replace'], rule['with'], metadata)
        if previous_iteration_metadata != metadata:
            changes_row = dict(changes_template)
            changes_row['original metadata'] = original_metadata
            changes_row['rule_name'] = 'generic_regex'
            changes_row['regex'] = 'yes'
            changes_row['replace'] = rule['replace']
            changes_row['with'] = rule['with']
            changes_row['previous_iteration'] = previous_iteration_metadata
            changes_row['new_iteration'] = metadata
            changes_list.append(changes_row)
            previous_iteration_metadata = metadata
    for rule in standard_replace:
        metadata = metadata.replace(rule['replace'], rule['with'])
        if previous_iteration_metadata != metadata:
            changes_row = dict(changes_template)
            changes_row['original_metadata'] = original_metadata
            changes_row['rule_name'] = 'generic_replace'
            changes_row['regex'] = 'no'
            changes_row['replace'] = rule['replace']
            changes_row['with'] = rule['with']
            changes_row['previous_iteration'] = previous_iteration_metadata
            changes_row['new_iteration'] = metadata
            changes_list.append(changes_row)
            previous_iteration_metadata = metadata
    final_dict = {"original_metadata": original_metadata, "new_metadata": metadata, "changes": changes_list}
    return final_dict


def channel_based_fx(metadata, channel_based_rules):
    """
       :param metadata: list of dicts with input metadata [{"channel_id": cnl,"original_metadata": meta}, {...}, ...]
       :param channel_based_rules: rules parsed to the function, list of dicts [{"channel_id": val, "name": val, ....},{},...]
       :return:
       """
    finalChart =[]
    channel_based_rules_ids = [i["channel_id"] for i in channel_based_rules]
    metadata_to_process = [i for i in metadata if i["channel_id"] in channel_based_rules_ids]
    for i in metadata_to_process:
        changes_list = []
        original_metadata = i["original_metadata"]
        metadata_dict = {"original_metadata":original_metadata}
        previous_iteration = original_metadata
        current_channel = i["channel_id"]
        rules_to_apply = [i for i in channel_based_rules if i["channel_id"] == current_channel]
        for rule in rules_to_apply:
            changes_row = dict(changes_template)
            if rule["separator"]:
                part = rule["part"]
                split_metadata = original_metadata.split(rule["separator"])
                if not part:
                    metadata = split_metadata[0]
                else:
                    try:
                        metadata = split_metadata[int(part)]
                    except:
                        metadata = split_metadata[0]
                if previous_iteration != metadata:
                    changes_row['original_metadata'] = original_metadata
                    changes_row['rule_name'] = 'separate'
                    changes_row['previous_iteration'] = previous_iteration
                    changes_row['new_iteration'] = metadata
                    changes_list.append(changes_row)
            if rule["replace"]:
                changes_row = dict(changes_template)
                if rule["regex"] == '1':
                    metadata = re.sub(rule['replace'], rule['with'], metadata)
                    changes_row['rule_name'] = 'channel_regex'
                    changes_row['regex'] = 'yes'
                else:
                    if rule['replace']:
                        rule['replace'] = str(rule['replace'])
                    if rule['with']:
                        rule['with'] = str(rule['with'])
                    if not rule['with']:
                        rule['with'] = ""
                    metadata = metadata.replace(rule['replace'], rule['with'])
                    changes_row['rule_name'] = 'generic_replace'
                    changes_row['regex'] = 'no'
                if previous_iteration != metadata:
                    changes_row['original_metadata'] = original_metadata
                    changes_row['replace'] = rule['replace']
                    changes_row['with'] = rule['with']
                    changes_row['previous_iteration'] = previous_iteration
                    changes_row['new_iteration'] = metadata
                    changes_list.append(changes_row)
                    previous_iteration = metadata
            metadata_dict = {"original_metadata": original_metadata, "new_metadata": metadata, "changes": changes_list}
            if rule["isolated"] != 1:
                metadata_dict_generic = generic_replace_function(metadata, standard_replace_chart)
                metadata_dict["original_metadata"] = original_metadata
                metadata_dict["new_metadata"] = metadata_dict_generic["new_metadata"]
                metadata_dict["changes"] += metadata_dict_generic["changes"]
        finalChart.append(metadata_dict)
    return finalChart

def skobki(input_string):
    skobki_pattern = re.compile("\(([^\)]+)\)")
    skobki_list = skobki_pattern.findall(input_string)
    skobki_list = [proper_case(less_spaces(i)) for i in skobki_list]
    return skobki_list


def fats_splitter(input):
    if type(input) == dict:
        try:
            input_string = input["new_metadata"]
            reverse = input["reverse"]
        except:
            return "Seems like the incorrect input"
    elif type(input) == str:
        input_string = input
        reverse = "no"

    original_metadata = input_string
    feat_str = "Feat."
    separator_str = " - "
    feat, artist, track, subtitle = [], [], [], []
    subtitle_list = skobki(input_string)

    for i in subtitle_list:
        if feat_str in i:
            feat.append(i.replace(feat_str, ""))
        else:
            subtitle.append(i)
        skobki_pattern = re.compile("\(([^\)]+)\)")
        skobki_list = skobki_pattern.findall(input_string)
        for i in skobki_list:
            input_string = less_spaces(input_string.replace(f"({i})",""))

    if separator_str in input_string:
        input_string = input_string.split(separator_str)
        if reverse == "yes":
            artist.append(", ".join(input_string[1:]))
            track.append(input_string[0])
        else:
            artist.append(input_string[0])
            track.append(", ".join(input_string[1:]))

    for i, v in enumerate(artist):
        if feat_str in v:
            aux_split = v.split(feat_str)
            artist[i] = aux_split[0]
            feat.append(aux_split[1])

    for i, v in enumerate(track):
        if feat_str in v:
            aux_split = v.split(feat_str)
            track[i] = aux_split[0]
            feat.append(", ".join(aux_split[1:]))

    final_dict = {
        "original metadata": original_metadata,
        "input_artist":input["artist"],
        "artist": artist,
        "track": track,
        "feat": feat,
        "input_subtitle": input["subtitle"],
        "subtitle": subtitle,
    }

    for k in final_dict:
        if type(final_dict[k]) == list:
            final_dict[k] = ", ".join(final_dict[k])

    if final_dict["feat"]:
        polished_feat = f" Feat. {final_dict['feat']}"
    else:
        polished_feat = ""

    if not artist and not track:
        final_dict["polished_metadata"] = original_metadata
        final_dict["search_tool"] = f"{original_metadata}|{original_metadata}"
    else:
        if final_dict['subtitle']:
            subtitle_formatted = f" ({final_dict['subtitle']})"
        else:
            subtitle_formatted = ""
        final_dict["polished_metadata"] = f"{final_dict['artist']} {polished_feat} - {final_dict['track']}{subtitle_formatted}"
        final_dict["search_tool"] = f"{final_dict['track']}{subtitle_formatted}|{final_dict['artist']} {polished_feat}"
    for k in final_dict:
        final_dict[k] = proper_case(less_spaces(final_dict[k]))
    return final_dict


def feat_extractor(in_string):
    finalDict = {}
    feat = " Feat. "
    try:
        finalDict["track"] = white_title(in_string.split(' - ')[1])
        finalDict["artist"] = in_string.split(' - ')[0]
        track = finalDict["track"]
        if feat in track:
            feat_meta = f" Feat. {track.split(feat)[1]}"
            finalDict["artist"] += feat_meta
            track = track.replace(feat_meta,'')
            track = white_title(track)
            finalDict["track"] = track.title()
        finalDict["overall"] = f"{finalDict['artist']} - {track}".title()

    except:
        finalDict["artist"] = in_string
        finalDict["track"] = in_string
        finalDict["overall"] = in_string.title()
    return finalDict


def replace_chart_reader(file_name, sheet_name):
    mainInputChart = excel_reader(file_name, sheet_name)
    split_chart, regex_chart, replace_chart = [], [], []
    for el in mainInputChart:  # changing one column cells from None to '' in order to create the proper replace
        if el[2] == None:
            el[2] = ''
    for el in mainInputChart:  # breakdown of Excel input replace chart into 3) main parts: split by YT channel rules; regex replace; standard replace
        if el[4] == "CHANNEL":
            split_row = [el[0], el[1], el[3]]
            split_chart.append(split_row)  # creating the chart for the big_split f(x)
        elif el[4] == "REGEX":
            regex_row = [el[1], el[2]]
            regex_chart.append(regex_row)  # creating the chart for the regex_repl f(x)
        else:
            replace_row = [el[1], el[2]]
            replace_chart.append(replace_row)  # creating the chart for the big_replace f(x)
    finalDict = {
        "Split chart": split_chart,
        "Regex chart": regex_chart,
        "Standard replace chart": replace_chart
    }
    return finalDict

replaceChart = replace_chart_reader(mainFolder, "Replace List")

def global_replace(input_string, channel=None):  # using the sequence of all the replace functions that we have
    finalDict = {}
    tmp_string = del_emoji(input_string)  # 1) deleting all the un-neccessary emojis from the string
    if channel != None:
        tmp_string = big_split(tmp_string, channel, replaceChart["Split chart"])
    tmp_string = regex_repl(tmp_string, replaceChart["Regex chart"])
    tmp_string = big_replace(tmp_string, replaceChart["Standard replace chart"])
    tmp_string = white_title(tmp_string)
    finalDict = feat_extractor(tmp_string)
    return finalDict


def totally_new_global_metadator():
    excel_path = '/helpers/Metadator.xlsx'
    channel_based_rules_sheet = 'channel_based_rules'
    generic_replace_sheet = 'generic_replace'
    metadata_input_sheet = 'metadata'
    channel_based_rules_excel = excel_reader(excel_path, channel_based_rules_sheet)
    generic_replace_excel = excel_reader(excel_path, generic_replace_sheet)
    metadata_excel = excel_reader(excel_path, metadata_input_sheet)
