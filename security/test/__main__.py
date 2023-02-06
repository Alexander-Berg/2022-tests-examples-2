import os
import json
import uuid
import decimal
import datetime

from dateutil import parser
from yql.api.v1.client import YqlClient
from security.yql_conversion import main
from yql.client.parameter_value_builder import \
    YqlParameterValueBuilder as ValueBuilder


query_for_json =  """
    DECLARE $x1 AS Int8;
    DECLARE $x2 AS Int16;
    DECLARE $x3 AS Int32;
    DECLARE $x4 AS Int64;
    DECLARE $x5 AS Uint8;
    DECLARE $x6 AS Uint16;
    DECLARE $x7 AS Uint32;
    DECLARE $x8 AS Uint64;
    DECLARE $x9 AS Bool;
    DECLARE $x10 AS Float;
    DECLARE $x11 AS Double;
    DECLARE $x12 AS Decimal(33,2);
    -- DECLARE $x121 AS Decimal(33,2); "inf"
    -- DECLARE $x122 AS Decimal(33,2); "nan"
    -- DECLARE $x123 AS Decimal(33,2); "-inf"
    DECLARE $x13 AS String;
    DECLARE $x131 AS String; --binary
    DECLARE $x14 AS Utf8;
    DECLARE $x15 AS Uuid;
    DECLARE $x16 AS Yson;
    DECLARE $x17 AS Json;
    DECLARE $x18 AS Date;
    DECLARE $x19 AS Datetime;
    DECLARE $x20 AS Timestamp;
    DECLARE $x21 AS Interval;
    DECLARE $x22 AS TzDate;
    DECLARE $x23 AS TzDatetime;
    DECLARE $x24 AS TzTimestamp;
    DECLARE $x25 AS Void;
    DECLARE $x251 AS Void;

    -- Optional
    DECLARE $x26 AS Int8?;
    DECLARE $x27 AS Int16?;
    DECLARE $x28 AS Int32?;
    DECLARE $x29 AS Int64?;
    DECLARE $x30 AS Uint8?;
    DECLARE $x31 AS Uint16?;
    DECLARE $x32 AS Uint32?;
    DECLARE $x33 AS Uint64?;
    DECLARE $x34 AS Bool?;
    DECLARE $x35 AS Float?;
    DECLARE $x36 AS Double?;
    DECLARE $x37 AS Decimal(33,2)?;
    -- DECLARE $x371 AS Decimal(33,2)?;  "inf"
    -- DECLARE $x372 AS Decimal(33,2)?;  "nan"
    -- DECLARE $x373 AS Decimal(33,2)?;  "-inf"
    DECLARE $x38 AS String?;
    DECLARE $x381 AS String?; --binary
    DECLARE $x382 AS String?; --empty
    DECLARE $x383 AS String?; --null
    DECLARE $x39 AS Utf8?;
    DECLARE $x40 AS Uuid?; -- don't work with ["GLwSGDhY3kyYqihzAml7kA=="] format
    DECLARE $x41 AS Yson?;
    DECLARE $x42 AS Json?;
    DECLARE $x43 AS Date?;
    DECLARE $x44 AS Datetime?;
    DECLARE $x45 AS Timestamp?;
    DECLARE $x46 AS Interval?;
    DECLARE $x47 AS TzDate?;
    DECLARE $x48 AS TzDatetime?;
    DECLARE $x49 AS TzTimestamp?;
    DECLARE $x50 AS Void?;
    DECLARE $x501 AS Void?;

    DECLARE $x60 AS Struct<Id:Int64, Name:String>;
    DECLARE $x601 AS Struct<Id:Int64, Name:String>?;

    DECLARE $x61 AS List<String>;
    DECLARE $x611 AS List<String>?;

    DECLARE $x62 AS Dict<Int64, String>;
    DECLARE $x621 AS Dict<Int64,String>?;

    -- DECLARE $x63 AS Variant<Int64, String>;
    -- DECLARE $x64 AS Variant<a:Int64, b:String>;

    DECLARE $x65 AS Tuple<String, Int64?>;
    DECLARE $x651 AS Tuple<String, Int64>?;

    DECLARE $x66 AS EmptyList;
    DECLARE $x661 AS EmptyList?;

    DECLARE $x67 AS EmptyDict;
    DECLARE $x671 AS EmptyDict?;

    SELECT $x1 as x1, $x2 as x2, $x3 as x3, $x4 as x4, $x5 as x5, $x6 as x6, 
    $x7 as x7, $x8 as x8, $x9 as x9, $x10 as x10, $x11 as x11, $x12 as x12, $x13 as x13, 
    $x131 as x131, $x14 as x14, $x15 as x15, $x16 as x16, $x17 as x17, $x18 as x18, 
    $x19 as x19,  $x20 as x20, $x21 as x21, $x22 as x22, $x23 as x23, $x24 as x24,  
    $x25 as x25, $x251 as x251, $x26 as x26, $x27 as x27, $x28 as x28, $x29 as x29, 
    $x30 as x30,  $x31 as x31, $x32 as x32, $x33 as x33, $x34 as x34, $x35 as x35, 
    $x36 as x36, $x37 as x37, $x38 as x38, $x381 as x381, $x382 as x382, $x383 as x383, 
    $x39 as x39, $x40 as x40, $x41 as x41, $x42 as x42, $x43 as x43, $x44 as x44, 
    $x45 as x45,  $x46 as x46, $x47 as x47, $x48 as x48, $x49 as x49, $x50 as x50, 
    $x501 as x501,  $x60 as x60, $x601 as x601, $x61 as x61, $x611 as x611, $x62 as x62,
    $x621 as x621, $x65 as x65, $x651 as x651, $x66 as x66, $x661 as x661, $x67 as x67, 
    $x671 as x671
    """ 

parameters_yql_converted = {'$x21': '{"Data": "-2509261088556"}', '$x8': '{"Data": "8"}', 
    '$x501': '{"Data": null}', '$x34': '{"Data": [false]}', '$x18': '{"Data": "17563"}', 
    '$x12': '{"Data": "-123456789.8765432"}', '$x36': '{"Data": ["-89.760000000000005"]}', 
    '$x17': '{"Data": "{\\"b\\": 321}"}', '$x382': '{"Data": null}', 
    '$x24': '{"Data": "2018-02-01T15:16:17.034567,GMT"}', '$x3': '{"Data": "3"}', 
    '$x11': '{"Data": "-89.760000000000005"}',
    '$x19': '{"Data": "1517498177"}', '$x14': '{"Data": "bbbb"}', '$x6': '{"Data": "6"}', 
    '$x46': '{"Data": ["-2509261088556"]}', '$x20': '{"Data": "1517498177034567"}', 
    '$x38': '{"Data": ["aaaa"]}', '$x45': '{"Data": ["1517498177034567"]}', 
    '$x15': '{"Data": ["AIQOVZvi1EGnFkRmVUQAAA=="]}', '$x9': '{"Data": false}', 
    '$x60': '{"Data": {"Id": "1", "Name": "Anna"}}', 
    '$x32': '{"Data": ["7"]}', '$x23': '{"Data": "2018-02-01T15:16:17,Europe/Moscow"}', 
    '$x601': '{"Data": [{"Id": "1", "Name": "Anna"}]}', '$x4': '{"Data": "4"}', 
    '$x25': '{"Data": null}', '$x28': '{"Data": ["3"]}', '$x33': '{"Data": ["8"]}', 
    '$x621': '{"Data": [[["1", "Value"], ["2", "Value"]]]}', '$x29': '{"Data": ["4"]}', 
    '$x1': '{"Data": "1"}', '$x251': '{"Data": null}', '$x39': '{"Data": ["bbbb"]}', 
    '$x671': '{"Data": null}', '$x27': '{"Data": ["2"]}', '$x66': '{"Data": []}', 
    '$x37': '{"Data": ["-123456789.8765432"]}', '$x48': '{"Data": ["2018-02-01T15:16:17,Europe/Moscow"]}',
    '$x26': '{"Data": ["1"]}', '$x13': '{"Data": "aaaa"}', 
    '$x47': '{"Data": ["2018-02-01,America/Los_Angeles"]}',  '$x40': '{"Data": [["AIQOVZvi1EGnFkRmVUQAAA=="]]}', 
    '$x43': '{"Data": ["17563"]}', '$x35': '{"Data": ["-1.25"]}', '$x31': '{"Data": ["6"]}', 
    '$x42': '{"Data": ["{\\"b\\": 321}"]}', '$x67': '{"Data": {}}', 
    '$x30': '{"Data": ["5"]}', '$x131': '{"Data": "\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\b"}', 
    '$x49': '{"Data": ["2018-02-01T15:16:17.034567,GMT"]}', 
    '$x10': '{"Data": "-1.25"}', '$x22': '{"Data": "2018-02-01,America/Los_Angeles"}', 
    '$x611': '{"Data": [["a", "b"]]}', '$x5': '{"Data": "5"}', '$x661': '{"Data": null}', 
    '$x44': '{"Data": ["1517498177"]}', '$x50': '{"Data": null}', 
    '$x381': '{"Data": ["\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\b"]}', 
    '$x62': '{"Data": [["1", "Value"], ["2", "Value"]]}', '$x383': '{"Data": null}', 
    '$x16': '{"Data": {"a": {"$type": "int64", "$value": "123"}, "b": {"$type": "string", "$value": "aaa"}}}', '$x2': '{"Data": "2"}', 
    '$x41': '{"Data": [{"a": {"$type": "int64", "$value": "123"}, "b": {"$type": "string", "$value": "aaa"}}]}', 
    '$x61': '{"Data": ["a", "b"]}', '$x7': '{"Data": "7"}'}

parameters_outside_json = '{"$x1": 1, "$x2": 2, "$x3": 3, "$x4": 4, "$x5": 5, "$x6": 6, "$x7": 7, "$x8": 8, "$x9": false, "$x10": -1.25, "$x11": -89.76, "$x12": "-123456789.8765432", "$x121": "Infinity", "$x122": "NaN", "$x123": "-Infinity", "$x13": "aaaa", "$x131": "\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\u0008", "$x14": "bbbb", "$x15": "550e8400-e29b-41d4-a716-446655440000", "$x16": "{a=123; b=aaa}", "$x17": {"b": 321}, "$x18": "2018-02-01", "$x19": "2018-02-01T15:16:17", "$x20": "2018-02-01T15:16:17.034567", "$x21": ["2018-02-01T15:16:17.034567","2018-03-02T16:17:18.123123"], "$x22": "2018-02-01,America/Los_Angeles", "$x23": "2018-02-01T15:16:17,Europe/Moscow", "$x24": "2018-02-01T15:16:17.034567,GMT", "$x25": "Void", "$x251": null, "$x26": 1, "$x27": 2, "$x28": 3, "$x29": 4, "$x30": 5, "$x31": 6, "$x32": 7, "$x33": 8, "$x34": false, "$x35": -1.25, "$x36": -89.76, "$x37": "-123456789.8765432", "$x38": "aaaa", "$x381":"\\u0000\\u0001\\u0002\\u0003\\u0004\\u0005\\u0006\\u0007\\u0008",  "$x382": "",  "$x383": null,  "$x39": "bbbb", "$x40": "550e8400-e29b-41d4-a716-446655440000", "$x41": "{a=123; b=aaa}", "$x42": {"b": 321}, "$x43": "2018-02-01", "$x44": "2018-02-01T15:16:17", "$x45": "2018-02-01T15:16:17.034567", "$x46": ["2018-02-01T15:16:17.034567","2018-03-02T16:17:18.123123"], "$x47": "2018-02-01,America/Los_Angeles", "$x48": "2018-02-01T15:16:17,Europe/Moscow", "$x49": "2018-02-01T15:16:17.034567,GMT", "$x50": "Void", "$x501": null, "$x60": {"Id": "1", "Name": "Anna"}, "$x601": {"Id": "1", "Name": "Anna"}, "$x61": ["a", "b"], "$x611": ["a", "b"], "$x62": [["1","Value"],["2","Value"]], "$x621": [["1","Value"],["2","Value"]], "$x63": [["1","Value"],["2","Value"]], "$x64": ["1", "value1"], "$x65": ["Some string", "64"], "$x651": ["Some string", "64"], "$x66": [], "$x661": [], "$x67": {}, "$x671": {}}'

if __name__ == '__main__':
    
    parameters_into_python = json.loads(parameters_outside_json) 
    query = query_for_json

    parameters = main(query ,parameters_into_python)

    for key, value in parameters_yql_converted.items():
        print("Test Start")
        print("Key: {}".format(key))
        print("Value: {}".format(value))
        print("Converted value: {}".format(parameters.get(key)))
        assert parameters.get(key) == value, "Incorrect convert"

        print("-----------------------------")
