from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from kine_logger import KineLogger
from km_protobuf import kinemaster_project_wire_pb2 as KineWire
import json
# from enum import Enum

def kmproject_to_string(project_binary):
    if project_binary.index(b'\xf3\x4b\x4d\xea') == -1:
        KineLogger.error('Invaild kmproj file.')		
        raise Exception('Invaild kmproj file.')
    
    ftrx = project_binary.index(b'FTRX')
    tiln = project_binary.index(b'TLIN')
    khdr = project_binary.index(b'KHDR')


    khdrData = project_binary[(khdr+8):(tiln)]
    headerLen = project_binary[(khdr+4):(khdr+8)]
    tlinData = project_binary[(tiln+8):(ftrx)]

    project_header = KineWire.KMProto.KMProjectHeader()
    project_header.ParseFromString(khdrData)

    project = KineWire.KMProto.KMProject()
    project.ParseFromString(tlinData)

    return project_header, project

def kmproject_to_json(project_binary):
    project_header, project = kmproject_to_string(project_binary)
    return MessageToJson(project_header), MessageToJson(project)

def kmproject_to_dict(project_binary):
    project_header, project = kmproject_to_string(project_binary)
    return MessageToDict(project_header), MessageToDict(project)

def store_kmproject_to_json_file(project_binary, path, filename, print_doc):
    project_header, project = kmproject_to_json(project_binary)

    result = "{"
    result += "\"project\" : "
    result += project
    result += ",\n"
    result += "\"project header\" : "
    result += project_header
    result += "}"

    parsed = json.loads(result)
    prettyJson = json.dumps(parsed, indent=4, sort_keys=True)
    if print_doc:
        print(prettyJson)

    fullpath = "{}/{}.json".format(path, filename)

    storedJsonFile = open(fullpath, 'w')
    storedJsonFile.write(prettyJson)
    storedJsonFile.close()

    KineLogger.info("Json document file is created. (json/{}.json)".format(filename))

def store_kmproject_to_PDS_info_file(project_binary, path, filename, print_doc):
    project_header, project = kmproject_to_dict(project_binary)

    result = "{"
    result += "}"

    formatted_info = json.loads(result)
    formatted_info['projectName'] = filename
    formatted_info['aspectRatio'] = '{}:{}'.format(project_header['projectAspectWidth'], project_header['projectAspectHeight'])
    formatted_info['duration'] = float(project_header['totalPlayTime']) / 1000.0
    formatted_info['savedOnPlatform'] = project_header['savedOnPlatform']
    formatted_info['savedWithKmVerName'] = project_header['savedWithKmVerName']

    # 원하는 포맷.
    # Effects, Transitions, Stickers, Music, Sound Effects, Clip Graphics, Videos, Images, Fonts
    #   에셋의 이름, 인덱스 아이디, 종류
    #   Neonlight [2967] (Transition)

    # Clip types.. more types may exsist.
    # visualClip - titleEffectId, mediaPath
    # transition, - transitionEffectId
    # audioClip, - mediaPath
    # videoLayer, - videoPath
    # assetLayer, - assetItemId
    # textLayer - fontId

    # From KineMaster project proto spec.
    # // Only one of the following is used depending on clip_type
    # optional VisualClip visual_clip = 4;				// A visual clip (video, image, etc.) on the primary timeline
    # optional Transition transition = 5;					// A transition on the primary timeline
    # optional AudioClip audio_clip = 6;					// An audio clip on the secondary timeline
    # optional TextLayer text_layer = 7;					// A text layer on the secondary timeline

    # // Deprecated  ------------------------------------------------------
    # optional StickerLayer sticker_layer = 8;			// A sticker layer on the secondary timeline

    # optional ImageLayer image_layer = 9;				// An image layer on the secondary timeline
    # optional HandwritingLayer handwriting_layer = 10;	// A handwriting layer on the secondary timeline
    # optional VideoLayer video_layer = 11;				// A video layer on the secondary timeline

    # // Deprecated  ------------------------------------------------------
    # optional EffectLayer effect_layer = 12;				// DO NOT USE!! This was used during dev version and show demo for effect layers; now effects are handled by AssetLayer

    # optional AssetLayer asset_layer = 13;				// An asset layer on the secondary timeline
    # optional GroupLayer group_layer = 15;				// An asset layer on the secondary timeline

    # class ClipKinds(str, Enum):
    #     visualClip = 'visualClip'
    #     transition = 'transition'
    #     audioClip = 'audioClip'
    #     videoLayer = 'videoLayer'
    #     assetLayer = 'assetLayer'
    #     textLayer = 'textLayer'

    specific_clip_types = [
        ('visualClip', ['titleEffectId', 'mediaPath']), 
        ('transition', ['transitionEffectId']), 
        ('audioClip', ['mediaPath']), 
        ('videoLayer', ['videoPath']), 
        ('assetLayer', ['assetItemId']), 
        ('textLayer', ['fontId'])]

    SERVER_INDEX_KEYWORD = '?serveridx='
    ASSET_ID_PREFIX = 'kmm://assetitemid/'

    assets = json.loads(result)
    assets['Items'] = []
    asset_summary = dict()

    # def get_readable_kinds(name, kinds):
    #     pos = name.find(SERVER_INDEX_KEYWORD, 0, len(asset_clip_id))
    #     if pos != -1:
    #         server_index = asset_clip_id[pos+len(SERVER_INDEX_KEYWORD):]
    #         asset_name = asset_clip_id[len(ASSET_ID_PREFIX):pos]


    def make_summary(summary, asset_clip_id, kinds):
        pos = asset_clip_id.find(SERVER_INDEX_KEYWORD, 0, len(asset_clip_id))
        if pos != -1:
            server_index = asset_clip_id[pos+len(SERVER_INDEX_KEYWORD):]
            asset_name = asset_clip_id[len(ASSET_ID_PREFIX):pos]
            if not server_index in summary:
                summary[server_index] = []
            summary_item = dict(assetIndex = server_index)
            summary_item['assetName'] = asset_name
            summary_item['kinds'] = kinds
            summary[server_index].append(summary_item)
            # else:
                

    def get_item(asset_item):
        item = dict(clipType=asset_item['clipType'])
        for specific_clip_type in specific_clip_types:
            if specific_clip_type[0] in asset_item:
                for clip_id in specific_clip_type[1]:
                    if clip_id in asset_item[specific_clip_type[0]]:
                        item[clip_id] = asset_item[specific_clip_type[0]][clip_id]
                        make_summary(asset_summary, item[clip_id], specific_clip_type[0])
        return item

    for primary_item in project['primaryItems']:
        item = get_item(primary_item)
        assets['Items'].append(item)
    
    if 'secondaryItems' in project:
        for secondary_item in project['secondaryItems']:
            item = get_item(secondary_item)
            assets['Items'].append(item)

    formatted_info['z_assetSummary'] = asset_summary
    formatted_info['z_extraInfosUsedAssets'] = assets
    

    prettyJson = json.dumps(formatted_info, indent=4, sort_keys=True)
    fullpath = "{}/{}.json".format(path, filename)

    storedJsonFile = open(fullpath, 'w')
    storedJsonFile.write(prettyJson)
    storedJsonFile.close()

    KineLogger.info("PDS info document file is created. (json/{}.json)".format(filename))

def km_protobuf_to_json(file_path, dest_path, json_file_name, print_doc):
    if file_path:
        KineLogger.info("Generate Json Document for {}".format(file_path))

        file = open(file_path, 'rb')
        try:
            body = file.read()
            # header, project = kmproject_to_dict(body)
            store_kmproject_to_json_file(body, dest_path, json_file_name, print_doc)
        except Exception as e:
            KineLogger.error("Failed to generate Json document.")
            KineLogger.error(e)

        file.close()
    else:
        KineLogger.error("Failed to generate Json document.")

def km_protobuf_to_PDS_info(file_path, dest_path, json_file_name, print_doc):
    if file_path:
        KineLogger.info("Generate Json Document for {}".format(file_path))

        file = open(file_path, 'rb')
        try:
            body = file.read()
            # header, project = kmproject_to_dict(body)
            store_kmproject_to_PDS_info_file(body, dest_path, json_file_name, print_doc)
        except Exception as e:
            KineLogger.error("Failed to generate Json document.")
            KineLogger.error(e)

        file.close()
    else:
        KineLogger.error("Failed to generate Json document.")

# km_protobuf_to_json("./km_protobuf/Retro intro.kmproject")
km_protobuf_to_json("./samples/AssetTestMine/AssetTestMine.kmproject", "./reducer_output/test", "proto-info", False)
km_protobuf_to_PDS_info("./samples/AssetTestMine/AssetTestMine.kmproject", "./reducer_output/test", "pds-info", False)