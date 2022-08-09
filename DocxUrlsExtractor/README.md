# Azure Cognitive Search - Docx Parser
---
Description:
- Azure Cognitive Search skill to extract URLs from Microsoft Word documents

Languages:
- ![python](https://img.shields.io/badge/language-python-orange)

Products:
- Azure Cognitive Search
- Azure Functions
---

# Steps    

1. Create a Python Function in Azure, here is a good [starting point](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-python)
2. Clone this repository
3. Open the folder in VS Code and deploy the function, find here a [tutorial](https://docs.microsoft.com/azure/search/cognitive-search-custom-skill-python)
4. Add a field in your index where you will dump the enriched classes, more info [here](#sample-index-field-definition)
5. Add the skill to your skillset as [described below](#sample-skillset-integration)
6. Add the field mappings and the output field mapping in your indexer as [seen in the sample](#sample-indexer-output-field-mapping)
7. Run the indexer 

## Sample Input:

```json
{
    "values" : [{
        "recordId" : "e1",
        "data":{
            "metadata_storage_path": "https://...",
            "metadata_storage_sas_token": "?sp=r...",
            "metadata_storage_file_extension": ".docx"
        }
    },
    {
        "recordId" : "e2",
        "data":{
            "metadata_storage_path": "https://...",
            "metadata_storage_sas_token": "?sp=r...",
            "metadata_storage_file_extension": ".docx"
        }
    }]
}
```

## Sample Output:

```json
{
    "values": [
        {
            "recordId": "e1",
            "data": {
                "metadata_storage_file_extension": ".docx",
                "urls": [
                    {
                        "text": "Microsoft",
                        "url": "https://www.microsoft.com/"
                    },
                    {
                        "text": "Bing",
                        "url": "https://www.bing.com/"
                    },
                    {
                        "text": "Portal Azure",
                        "url": "https://portal.azure.com/"
                    },
                    {
                        "text": "https://www.linkedin.com",
                        "url": "https://www.linkedin.com"
                    }
                ]
            }
        },
        {
            "recordId": "e2",
            "data": {
                "metadata_storage_file_extension": ".docx",
                "urls": [
                    {
                        "text": "Azure",
                        "url": "https://portal.azure.com/"
                    },
                    {
                        "text": "LinkedIn",
                        "url": "https://www.linkedin.com"
                    }
                ]
            }
        }
    ]
}
```

## Sample Skillset Integration

In order to use this skill in a cognitive search pipeline, you'll need to add a skill definition to your skillset.
Here's a sample skill definition for this example (inputs and outputs should be updated to reflect your particular scenario and skillset environment):

```json
{
    "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
    "name": "DOCx URLs",
    "description": "",
    "context": "/document",
    "uri": "YOUR_AZURE_FUNCTION_URL",
    "httpMethod": "POST",
    "timeout": "PT30S",
    "batchSize": 1,
    "degreeOfParallelism": 1,
    "inputs": [
      {
        "name": "metadata_storage_sas_token",
        "source": "/document/metadata_storage_sas_token"
      },
      {
        "name": "metadata_storage_path",
        "source": "/document/metadata_storage_path_decoded"
      },
      {
        "name": "metadata_storage_file_extension",
        "source": "/document/metadata_storage_file_extension"
      }
    ],
    "outputs": [
      {
        "name": "urls",
        "targetName": "urls"
      }
    ],
    "httpHeaders": {}
  }
```

## Sample Index Field Definition

The skill emits different headers text you can map in the index

```json
{
    "name": "urls",
    "type": "Collection(Edm.ComplexType)",
    "analyzer": null,
    "synonymMaps": [],
    "fields": [
      {
        "name": "text",
        "type": "Edm.String",
        "facetable": true,
        "filterable": true,
        "key": false,
        "retrievable": true,
        "searchable": false,
        "sortable": false,
        "analyzer": null,
        "indexAnalyzer": null,
        "searchAnalyzer": null,
        "synonymMaps": [],
        "fields": []
      },
      {
        "name": "url",
        "type": "Edm.String",
        "facetable": true,
        "filterable": true,
        "key": false,
        "retrievable": true,
        "searchable": false,
        "sortable": false,
        "analyzer": null,
        "indexAnalyzer": null,
        "searchAnalyzer": null,
        "synonymMaps": [],
        "fields": []
      }
    ]
  },
  {
    "name": "metadata_storage_path_decoded",
    "type": "Edm.String",
    "facetable": false,
    "filterable": true,
    "key": false,
    "retrievable": true,
    "searchable": false,
    "sortable": false,
    "analyzer": null,
    "indexAnalyzer": null,
    "searchAnalyzer": null,
    "synonymMaps": [],
    "fields": []
  }
```
## Sample Indexer 


```
    "fieldMappings": [
        {
            "sourceFieldName": "metadata_storage_path",
            "targetFieldName": "metadata_storage_path_decoded"
        }
    ]

  "outputFieldMappings": [
      ...
    {
        "sourceFieldName": "/document/urls",
        "targetFieldName": "urls"
    }
```
    