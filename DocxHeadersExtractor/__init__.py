import logging
import azure.functions as func
import json
from docx import Document
import requests
import io

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        body = json.dumps(req.get_json())
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )


def compose_response(json_data):
    values = json.loads(json_data)['values']
    
    # Prepare the Output before the loop
    results = {}
    results["values"] = []
    
    for value in values:
        output_record = transform_value(value)
        if output_record != None:
            results["values"].append(output_record)
    return json.dumps(results, ensure_ascii=False)

## Perform an operation on a record
def transform_value(value):
    try:
        recordId = value['recordId']
    except AssertionError  as error:
        return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('metadata_storage_sas_token' in data), "'metadata_storage_sas_token' field is required in 'data' object."
        assert (data['metadata_storage_file_extension'].lower() == ".docx", "'metadata_storage_file_extension' has to be docx")
    except AssertionError  as error:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })

    try:
        metadata_storage_path = data['metadata_storage_path']
        metadata_storage_sas_token = data['metadata_storage_sas_token']
        
        url = f"{metadata_storage_path}{metadata_storage_sas_token}"

        content = requests.get(url).content

        document = Document(io.BytesIO(content))

        data['headings'] = extract_headings(document)            
       
        data['head_lv1'] = list(map(lambda x : x['text'], list(filter(lambda x: x.get('level') == 1, data['headings']))))
        data['head_lv2'] = list(map(lambda x : x['text'], list(filter(lambda x: x.get('level') == 2, data['headings']))))
        data['head_lv3'] = list(map(lambda x : x['text'], list(filter(lambda x: x.get('level') == 3, data['headings']))))
        data['head_lv4'] = list(map(lambda x : x['text'], list(filter(lambda x: x.get('level') == 4, data['headings']))))
        data['head_lv5'] = list(map(lambda x : x['text'], list(filter(lambda x: x.get('level') == 5, data['headings']))))
        data['head_lv6'] = list(map(lambda x : x['text'], list(filter(lambda x: x.get('level') == 6, data['headings']))))

        data.pop('metadata_storage_path')
        data.pop('metadata_storage_sas_token')

    except ValueError as e:
        return (
            {
            "recordId": recordId,
            "errors": [ { "message": f"Could not complete operation for record: {recordId} with error: {str(e)}" }   ]       
            })

    return ({
            "recordId": recordId,
            "data" : data
            })


def extract_headings(document):
    headings = []
    for paragraph in document.paragraphs:
        if paragraph.style.name in heading_levels.keys():
            headings.append({'text': paragraph.text.replace('\t',''), 'level' : heading_levels.get(paragraph.style.name)})
    return headings

heading_levels = {
    "Heading 1" : 1,
    "Heading 2" : 2,
    "Heading 3" : 3,
    "Heading 4" : 4,
    "Heading 5" : 5,
    "Heading 6" : 6
}
