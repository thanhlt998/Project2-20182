import re


def parse_attribute(d):
    attr = []
    for k, v in d.items():
        if type(v) is not dict:
            attr.append(k)
        else:
            attr += [f'{k}_{at}' for at in parse_attribute(v)]
    return attr


def flatten_dict(d):
    result = {}
    for k, v in d.items():
        if k.startswith('@'):
            continue
        if type(v) is not dict:
            result[k] = v
        else:
            result = {**result, **{f'{k}_{k_}': v_ for k_, v_ in flatten_dict(v).items()}}
    return result


def format(json_object, dictionary):
    result = {}
    for k, v in json_object.items():
        if k == '@id' or k == '@type':
            continue
        key = k.split("/")[-1]

        # iter over all values in v
        value = []
        for vi in v:
            tmp = None
            if type(vi) is dict:
                if vi.get('@id') is not None:
                    if dictionary.get(vi['@id']) is not None:
                        tmp = format(dictionary[vi['@id']], dictionary)
                else:
                    tmp = re.sub("\\n\\s+", "\n ", vi['@value'].strip())
            else:
                tmp = re.sub("\\n\\s+", "\n ", vi.strip())

            if tmp not in value and tmp is not None:
                value.append(tmp)

        if len(value) == 0:
            continue
        elif len(value) == 1:
            if value[0] == '':
                continue
            result[key] = value[0]
        else:
            is_all_string = True
            for vi in value:
                if type(vi) is dict:
                    result[key] = vi
                    is_all_string = False
                    break
            if is_all_string:
                result[key] = value

    return result


def parse_json(json_list):
    dictionary = {o['@id']: o for o in json_list}

    # Find json object with JobPostingSchema
    jobs = [o for o in json_list if "http://schema.org/JobPosting" in o.get("@type")]

    return [format(job, dictionary) for job in jobs]
