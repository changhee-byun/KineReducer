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

# kmProtobufToJson("./km_protobuf/Retro intro.kmproject")