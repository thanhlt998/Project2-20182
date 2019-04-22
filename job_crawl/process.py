import json
import re

standard_job = {
    "title": "",
    "description": "",
    "jobBenefits": "",
    "experienceRequirements": "",
    "datePosted": "",
    "validThrough": "",
    "employmentType": "",
    "hiringOrganization": {
        "name": ""
    },
    "jobLocation": {
        "address": {
            "addressRegion": "",
            "addressCountry": "",
            "addressLocality": ""
        }
    },
    "baseSalary": {
        "currency": "",
        "minValue": 0,
        "maxValue": 0,
        "unitText": "",
        "value": ""
    },
    "occupationalCategory": [

    ]
}


def normalize_job(job):
    norm_job = standard_job.copy()
    norm_job['title'] = job['title']
    des = re.split(r"<h2>[^<>]*</h2>", job['description'])
    norm_job['description'] = re.sub(r'<[^<]*>', '', des[1]).strip()
    norm_job['experienceRequirements'] = re.sub(r'<[^<]*>', '', des[2]).strip()
    norm_job['jobBenefits'] = re.sub(r'<[^<]*>', '', des[3]).strip()
    norm_job['datePosted'] = job['datePosted']
    norm_job['validThrough'] = job['validThrough']
    norm_job['employmentType'] = job['employmentType']
    norm_job['hiringOrganization']['name'] = job['hiringOrganization']['name']
    norm_job['jobLocation']['address']['addressRegion'] = job['jobLocation'][0]['address']['addressRegion']
    norm_job['jobLocation']['address']['addressCountry'] = job['jobLocation'][0]['address']['addressRegion']
    norm_job['jobLocation']['address']['addressLocality'] = job['jobLocation'][0]['address']['addressLocality']
    norm_job['baseSalary']['currency'] = job['baseSalary']['currency']
    norm_job['baseSalary']['minValue'] = job['baseSalary']['value'].setdefault('minValue', '')
    norm_job['baseSalary']['maxValue'] = job['baseSalary']['value'].setdefault('maxValue', '')
    norm_job['baseSalary']['value'] = job['baseSalary']['value'].setdefault('value', '')
    norm_job['baseSalary']['unitText'] = job['baseSalary']['value'].setdefault('unitText', '')
    norm_job['occupationalCategory'] = [occupation.strip() for occupation in job['skills'].split(',')]
    return norm_job


with open('topcv1.json', mode='r', encoding='utf8') as f:
    jobs = json.load(f)
    f.close()

normalized_jobs = [normalize_job(job) for job in jobs]

with open('topcv_norm.json', mode='w', encoding='utf8') as f:
    json.dump(normalized_jobs, f, ensure_ascii=False)
    f.close()
