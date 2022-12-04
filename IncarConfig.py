import json
from dataclasses import dataclass


def get_job_templates(json_file: str = "resources/jobTemplates.json") -> dict:
    '''
    Loads incar parameter dictionaries from json file
    '''
    with open(json_file, "r") as f:
        job_templates = json.load(f)

    return job_templates

def get_incar_dict(job_type: str, job_templates: dict, json_file: str = "resources/INCAR_TAGS.txt") -> dict:
    '''
    Returns incar parameter dictionary for given job type
    '''
    #check if incar tags are valid using "AutoVASP/resources/INCAR_TAGS.txt"
    incar_tags = [ line.strip() for line in open(json_file, "r") ]
    for key in job_templates[job_type]:
        if key not in incar_tags:
            raise ValueError(f"ERROR: Invalid INCAR tag: {key}")

    return job_templates[job_type]








    

