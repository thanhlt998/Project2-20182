import json
import io

with open('job_topdev.json', mode='r', encoding='utf8') as f:
    objects = json.load(f)
    f.close()

jobs = [o for o in objects if "http://schema.org/JobPosting" in o.get("@type")]

# build a dict with the key is id
d = {}
for o in objects:
    d[o['@id']] = o


# format function
def format(json_object, dictionary):
    result = {}
    for k, v in json_object.items():
        if k == '@id' or k == '@type':
            continue
        key = k.split("/")[-1]

        # iter over all values in v
        value = []
        for vi in v:
            if type(vi) is dict:
                if vi.get('@id') is not None:
                    if dictionary.get(vi['@id']) is not None:
                        value.append(format(dictionary[vi['@id']], dictionary))
                else:
                    value.append(vi['@value'].strip())
            else:
                value.append(vi.strip())

        if len(value) == 0:
            continue
        elif len(value) == 1:
            if value[0] == '':
                continue
            result[key] = value[0]
        else:
            if type(value[-1]) is dict:
                value = value[-1]
            result[key] = value

    return result


# re-format the job
new_jobs = []
for job in jobs:
    new_jobs.append(format(job, dictionary=d))

# Save formated job
with io.open('new_topdev.json', mode='w', encoding='utf8') as f:
    json.dump(new_jobs, f, ensure_ascii=False)
