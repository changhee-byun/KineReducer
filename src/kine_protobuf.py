from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from kine_logger import KineLogger
from km_protobuf import kinemaster_project_wire_pb2 as KineWire
import json

def kmprojectToString(project_binary):
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

def kmprojectToJson(project_binary):
    project_header, project = kmprojectToString(project_binary)
    return MessageToJson(project_header), MessageToJson(project)

def kmprojectToDict(project_binary):
    project_header, project = kmprojectToString(project_binary)
    return MessageToDict(project_header), MessageToDict(project)

def storeKmprojectToJsonFile(project_binary, path, filename, print_doc):
    project_header, project = kmprojectToJson(project_binary)

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

def storeKmprojectToPDSInfoFile(project_binary, path, filename, print_doc):
    project_header, project = kmprojectToDict(project_binary)

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

    specificClipTypes = [
        ('visualClip', ['titleEffectId', 'mediaPath']), 
        ('transition', ['transitionEffectId']), 
        ('audioClip', ['mediaPath']), 
        ('videoLayer', ['videoPath']), 
        ('assetLayer', ['assetItemId']), 
        ('textLayer', ['fontId'])]


    assets = json.loads(result)
    assets['Items'] = []
    assetsSummary = dict()

    def get_item(asset_item):
        item = dict(clipType=asset_item['clipType'])
        for specificType in specificClipTypes:
            if specificType[0] in asset_item:
                for clipId in specificType[1]:
                    if clipId in asset_item[specificType[0]]:
                        item[clipId] = asset_item[specificType[0]][clipId]
                        pos = item[clipId].find('serveridx=', 0, len(item[clipId]))
                        if pos != -1:
                            print(item[clipId][pos+len("serveridx="):])
        return item

    for primary_item in project['primaryItems']:
        item = get_item(primary_item)
        assets['Items'].append(item)
    
    for secondary_item in project['secondaryItems']:
        item = get_item(secondary_item)
        assets['Items'].append(item)

    formatted_info['usedAssets'] = assets

    prettyJson = json.dumps(formatted_info, indent=4, sort_keys=True)
    fullpath = "{}/{}.json".format(path, filename)

    storedJsonFile = open(fullpath, 'w')
    storedJsonFile.write(prettyJson)
    storedJsonFile.close()

    KineLogger.info("PDS info document file is created. (json/{}.json)".format(filename))

def kmProtobufToJson(file_path, dest_path, json_file_name, print_doc):
    if file_path:
        KineLogger.info("Generate Json Document for {}".format(file_path))

        file = open(file_path, 'rb')
        try:
            body = file.read()
            # header, project = kmprojectToDict(body)
            storeKmprojectToJsonFile(body, dest_path, json_file_name, print_doc)
        except Exception as e:
            KineLogger.error("Failed to generate Json document.")
            KineLogger.error(e)

        file.close()
    else:
        KineLogger.error("Failed to generate Json document.")

def kmProtobufToPDSInfo(file_path, dest_path, json_file_name, print_doc):
    if file_path:
        KineLogger.info("Generate Json Document for {}".format(file_path))

        file = open(file_path, 'rb')
        try:
            body = file.read()
            # header, project = kmprojectToDict(body)
            storeKmprojectToPDSInfoFile(body, dest_path, json_file_name, print_doc)
        except Exception as e:
            KineLogger.error("Failed to generate Json document.")
            KineLogger.error(e)

        file.close()
    else:
        KineLogger.error("Failed to generate Json document.")

# kmProtobufToJson("./km_protobuf/Retro intro.kmproject")
kmProtobufToJson("./samples/AssetTestMine/AssetTestMine.kmproject", "./reducer_output/test", "proto-info", False)
kmProtobufToPDSInfo("./samples/AssetTestMine/AssetTestMine.kmproject", "./reducer_output/test", "pds-info", False)