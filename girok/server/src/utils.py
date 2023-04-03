import datetime
from collections import Counter
from typing import List


def get_current_year():
    now = datetime.datetime.now()
    return now.year


def extract_sub_dict(dct: dict, included_keys: List[str]):
    return {k: v for k, v in dct.items() if k in included_keys}


def capitalize_variable(var_name: str):
    """
    capitalizing a variable

    e.g. a_bcD -> ABcD

    :param var_name: name of variable in string
    :return: capitalized name
    """

    return ''.join([str(_).capitalize() for _ in var_name.split('_')])


def count_enum(values, enumTy, asec=False):
    """
    Count enum in list
    :param values: list of enum value
    :param enumTy: enum type
    :return: { enum key: count }
    """
        
    return {k.value: 0 for k in enumTy} | Counter(values)


def dict_as_list(dct: dict, asc=False):
    keys = list(dct.keys())
    values = list(dct.values())
    if not asc:
        keys = keys[::-1]
        values = values[::-1]
    return {"keys": keys, "values": values}


def sql_obj_list_to_dict_list(sql_obj_list):
    return [sql_obj_to_dict(sql_obj) for sql_obj in sql_obj_list]


def sql_obj_to_dict(sql_obj):
    return {col.name: getattr(sql_obj, col.name) for col in sql_obj.__table__.columns}



        
    
        