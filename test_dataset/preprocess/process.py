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

