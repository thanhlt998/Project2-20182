import re
import json


def load_dict(dict_file_name):
    if dict_file_name is not None:
        with open(dict_file_name, encoding='utf-8-sig', mode='r') as f:
            d = json.load(f)
            f.close()
        return d
    return None


CAREER_DICT = load_dict('job_crawl/dict/career.json')
ADDRESS_DICT = load_dict('job_crawl/dict/address.json')


def normalize_job(job):
    job['occupationalCategory'] = normalize_occupational_category(job['occupationalCategory'])
    job['title'] = normalize_title(job['title'])
    job['jobLocation']['address']['addressRegion'] = normalize_address_region(
        job['jobLocation']['address']['addressRegion'])
    job['baseSalary']['minValue'] = normalize_salary(job['baseSalary']['minValue'])
    job['baseSalary']['maxValue'] = normalize_salary(job['baseSalary']['maxValue'])
    return job


def normalize_occupational_category(occupational_category):
    normalized_occupational_category = []
    if type(occupational_category) is list:
        for careers in occupational_category:
            for career in careers.split(','):
                career_tmp = re.sub("\\s*[-\\/]\\s*", " - ", career.strip())
                normalized_occupational_category.append(CAREER_DICT.get(career_tmp, "Khác"))
    else:
        for career in occupational_category.split(','):
            career_tmp = re.sub("\\s*[-\\/]\\s*", " - ", career.strip())
            normalized_occupational_category.append(CAREER_DICT.get(career_tmp, "Khác"))
    return list(set(normalized_occupational_category))


def normalize_address_region(address_region):
    return ADDRESS_DICT.get(address_region.strip(), address_region)


def normalize_title(title):
    return re.sub(
        r"(\\(.+\\)|\\[.+\\]|{.+}|–.+|-.*|,.*|Thu Nhập.*|Khu Vực.*|Làm Việc Tại.*|Lương.*|\d{1,2}[ ]{0,1}-[ ]{0,1}\d{1,2}.*)",
        '', title).strip()


def normalize_salary(salary_value):
    res = salary_value
    if re.match(r"^(((\d{1,3}([\.,]\d{3})*)|(\d+))|(\w*\d+))$", str(salary_value)) is not None:
        res = int(re.sub(r'.,', '', str(salary_value)))
    else:
        value_list = re.findall(r'\d+', salary_value)
        if len(value_list) > 0:
            res = int(value_list[-1]) * 1000000
    return res
