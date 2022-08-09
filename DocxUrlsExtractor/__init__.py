import logging
import azure.functions as func
import json
import docxpy
import requests
import os
from uuid import uuid4

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

        filename = str(uuid4())
        with open(f'{filename}.docx', 'wb') as f:
            f.write(content)
        
        doc = docxpy.DOCReader(f"{filename}.docx")
        doc.process()

        data['urls'] = list(map(lambda x: {"text" : x[0].decode("utf-8") , "url": x[1]}, doc.data['links']))

        os.remove(f"{filename}.docx")

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
