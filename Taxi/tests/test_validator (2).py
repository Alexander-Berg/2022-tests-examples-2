import os
import yaml

aggregation_ops = ['And', 'Or', 'Not']
comparison_ops = ['Equals', 'StartsWith', 'EndsWith', 'Contains', 'Regex', 'LessThan', 'GreaterThan']
defaultMonitorings = ['vhost-500', 'vhost-499', 'vhost-4xx', 'vhost-429', 'vhost-404']


def group_name_by_file_name(filename):
    return os.path.basename(filename).rsplit('.yaml', 1)[0]

def get_line(obj):
    if hasattr(obj, 'line'):
        return obj.line
    else:
        return None

def is_list_or_int(data):
    if isinstance(data, list) and len(data) == 2:
        if is_int(data[0]) and is_int(data[1]):
            return True
    elif is_int(data):
        return True

    return False

def is_int(data):
    try:
        int(data)
    except:
        return False
    return True

def is_float(data):
    try:
        float(data)
    except:
        return False
    return True

def parse_monitoring(data, defaultBlacklists):
    if not isinstance(data, dict):
        raise TypeError("Monitoring should be a dict: <%s>" % (data))

    monitoring = {}

    for part in data:
        if part not in defaultMonitorings:
            monitoring[part] = parse_custom_monitoring(data[part], [])
        else:
            monitoring[part] = parse_vhostXXX(data[part], [])

    return monitoring

def parse_comparison_op(name, data):
    if not isinstance(data, dict):
        raise TypeError("Comparison operand's nested should be a dict")
    if len(data) != 1:
        raise TypeError("Comparison operand's nested dict should have precisely one parameter")

    k = list(data.keys())[0]
    if data[k] is None:
        raise TypeError("Comparison operand's nested dict should not contain <None> values")
    op = {
        'type': name,
        'field': k,
        'operand': data[k],
    }

    return op

def parse_options(data):
    if 'Options' not in data:
        return None

    options = data['Options']
    for k in options:
        if k == 'Apdex':
            validate_apdex(options['Apdex'])
        elif k == 'Timings':
            validate_timings(options['Timings'])
        elif k == 'CustomHttp':
            validate_custom_http(options['CustomHttp'])
        elif k == 'AdditionalTimingCodes':
            validate_additional_timing_codes(options['AdditionalTimingCodes'])
        elif k == 'Vhost500':
            validate_vhost500(options['Vhost500'])
        else:
            raise TypeError("Bad option: %s" % (k))
    return options

def parse_aggregation_op(name, data):
    if not isinstance(data, list):
        raise TypeError("Aggregation operand's nested should be a list")

    op = {
        'type': name,
        'children': [],
    }
    for f in data:
        op['children'].append(parse_filter(f))

    return op

def parse_blacklist(data, line):
    print(type(data))
    print(data)
    if not isinstance(data, list):
        raise TypeError("Blacklist should be a list")
    return [parse_filter(element, get_line(data)) for element in data]

def parse_custom_monitoring(data, defaultBlacklist):
    output = parse_vhostXXX(data, defaultBlacklist)

    if 'MatchRule' not in data:
        raise ValueError("Custom monitoring should contain <MatchRule> field: <%s>" % (data))

    output['MatchRule'] = parse_filter(data['MatchRule'])

    if 'Base' in data:
        base_check = data['Base']
        if not isinstance(base_check, str):
            raise TypeError('Bad base check name: %s' % base_check)
        if base_check not in defaultMonitorings:
            raise ValueError("base check name should be one of default checks: %s" % defaultMonitorings)
        output['Base'] = base_check

    return output

def parse_vhostXXX(data, defaultBlacklist):
    print('parse_vhostXXX function')
    print(data)
    if not isinstance(data, dict):
        raise TypeError("VhostXXX should be a dict: <%s>" % (data))

    output = {
        'features': [],
    }

    if 'Features' in data:
        if not isinstance(data['Features'], list):
            raise TypeError("vhostXXX configuration's <Features> parameter should be a list: <%s>" % (data))

        for feat in data['Features']:
            output['features'].append(parse_monitoring_feature(feat))

    if 'DefaultLimits' in data:
        output['defaultFeature'] = {'Limits': parse_limits(data['DefaultLimits'])}

    if 'Blacklist' in data:
        output['blacklist'] = parse_blacklist(data['Blacklist'], get_line(data))
    else:
        output['blacklist'] = parse_blacklist(defaultBlacklist, None)

    return output

def parse_monitoring_feature(data):
    if not isinstance(data, dict):
        raise TypeError("Monitoring feature should be a dict: <%s>" % (data))
    feature = {}
    if 'MatchRule' not in data:
        raise ValueError("Filters at monitoring should contain <MatchRule> field: <%s>" % (data))

    if 'Limits' not in data:
        raise ValueError("Filters at monitoring should contain <Limits> field: <%s>" % (data))

    feature['MatchRule'] = parse_filter(data['MatchRule'], get_line(data))
    feature['Limits'] = parse_limits(data['Limits'], get_line(data))
    return feature

def parse_limits(data, line=None):
    limits = {}
    limits_cfg = data
    if not isinstance(limits_cfg, dict):
        raise TypeError("Limit should be a dict: <%s>" % (data))
    for param in limits_cfg:
        if param in ['Warn', 'Crit', 'NonAlerting']:
            try:
                limits[param] = float(limits_cfg[param])
            except:
                raise LineTypeError(line, "Parameter <%s> of Limits should be int or double: <%s>" % (param, limits_cfg))
        else:
            raise LineTypeError(line, "Unknown Limits parameter <%s>: <%s>" % (param, limits_cfg))

    return limits

def parse_filter(data, line=None):
    if not isinstance(data, dict):
        raise TypeError("Filters should be a dict: <%s>" % (data))

    fltr = None
    for k in data:
        if k in aggregation_ops:
            if fltr:
                raise ValueError("There can't be two root-level operations at one graph")
            fltr = parse_aggregation_op(k, data[k])
        elif k in comparison_ops:
            if fltr:
                raise ValueError("There can't be two root-level operations at one graph")
            fltr = parse_comparison_op(k, data[k])
        elif k == "Options":
            continue
        else:
            raise TypeError("Bad parameter: %s" % (k))
    return fltr

def validate_apdex(data):
    for aspect in data:
        if aspect not in ['Ups', 'Req', 'Ssl'] or not is_list_or_int(data[aspect]):
            raise ValueError("Bad apdex: %s" % (aspect))

def validate_timings(data):
    if not isinstance(data, list):
        raise ValueError("Timings should be an instance of list")

    valid_timings = ['Ups', 'Req', 'Ssl']
    valid_keys = ['Type', 'Percentile', 'Warn', 'Crit']
    for i in range(len(data)):
        entry = data[i]
        if not isinstance(entry, dict):
            raise ValueError("Timings[{}] should be an instance of dict".format(i))
        if len(valid_keys) != len(entry):
            raise ValueError("Timings[{}] has wrong number of arguments {} while {} were expected".format(i, len(valid_keys), len(entry)))
        for key in valid_keys:
            if key not in entry:
                raise ValueError("Timings[{}] should have argument {}".format(i, key))
            if key == 'Type' and entry[key] not in valid_timings:
                raise ValueError("Timings[{}] has unknown type {} while one of {} was expected".format(i, entry[key], valid_keys))
            elif key != 'Type' and not is_float(entry[key]):
                raise ValueError("Timings[{}][{}] should be float (actual value: {})".format(i, key, entry[key]))

def validate_custom_http(data):
    for http in data:
        if not is_list_or_int(http):
            raise TypeError("Bad custom http: %s" % (http))

def validate_additional_timing_codes(data):
    for code in data:
        if not is_int(code):
            raise TypeError("Bad additional timing codes: %s" % (code))

def test_dorblu_config(config_file_path):
    with open(config_file_path, 'r') as f:
        raw_data = yaml.load(f, Loader=getattr(yaml, 'CLoader', yaml.Loader))
    f_name = group_name_by_file_name(config_file_path)

    if 'graphs' in raw_data and 'group' in raw_data:
        data = raw_data['graphs']
        group = raw_data['group']
        group.setdefault('name', f_name)
    elif 'graphs' in raw_data or 'group' in raw_data:
        raise KeyError('Bad conf file syntax in %s' % f_name)
    else:
        data = raw_data
        group = {}
        group['type'] = 'conductor'
        group['name'] = f_name

    for graph_name in data:
        if graph_name == "Monitoring":
            parse_monitoring(data[graph_name], [])
        else:
            try:
                parse_filter(data[graph_name])
                parse_options(data[graph_name])
            except Exception as e:
                raise e
