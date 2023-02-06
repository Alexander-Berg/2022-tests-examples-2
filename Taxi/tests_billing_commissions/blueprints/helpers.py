import copy


def clean_mongo_data_before_compare(records):
    def remove_uncomparable(val):
        val = copy.deepcopy(val)
        if 'updated' in val:
            del val['updated']
        if '_id' in val:
            del val['_id']
        return val

    return list(map(remove_uncomparable, records))
