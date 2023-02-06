from nose.tools import assert_equal, assert_raises

import taxi.tools.dorblu.dorblu_uploader.validation as validation


def test_parse_monitoring_feature():
    print "parse_monitoring_feature without MatchRule:",
    inputData = {'Limits': {'Crit': 0.5, 'Warn': 0}}
    assert_raises(Exception, validation.parse_monitoring_feature, inputData)

    print "parse_monitoring_feature with full valid data:",
    inputData = {
        'Limits': {'Crit': 0.5, 'Warn': 0, 'NonAlerting': 5},
        'MatchRule': {'Equals': {'http_host': 'blah.example.com'}}
    }
    expectedResult = {
        'Limits': {'Crit': 0.5, 'Warn': 0, 'NonAlerting': 5},
        'MatchRule': {'operand': 'blah.example.com', 'field': 'http_host', 'type': 'Equals'}
    }
    res = validation.parse_monitoring_feature(inputData)
    assert_equal(expectedResult, res)

    print "parse_monitoring_feature with bad Limits:",
    inputData = {'Limits': {'Critt': 0.5, 'Warn': 0}}
    assert_raises(Exception, validation.parse_monitoring_feature, inputData)

    print "parse_monitoring_feature with not arithmetic Limits:",
    inputData = {'Limits': {'Critt': 0.5, 'Warn': "abc"}}
    assert_raises(Exception, validation.parse_monitoring_feature, inputData)

    print "parse_monitoring_feature with missing Limits:",
    inputData = {'MatchRule': {'Equals': {'http_host': 'blah.example.com'}}}
    assert_raises(Exception, validation.parse_monitoring_feature, inputData)

    print "parse_monitoring_feature with not a dict:",
    inputData = [1, 2, 3]
    assert_raises(Exception, validation.parse_monitoring_feature, inputData)


def test_parse_vhostXXX():
    print "parse_vhostXXX with not a dict:",
    inputData = [1, 2, 3]
    assert_raises(Exception, validation.parse_vhostXXX, inputData, [])

    print "parse_vhostXXX without features:",
    inputData = {'some': 'stuff'}
    validation.parse_vhostXXX(inputData, [])

    print "parse_vhostXXX with non-list features:",
    inputData = {'Features': {'Limits': {'Crit': 0.5, 'Warn': 0}}}
    assert_raises(Exception, validation.parse_vhostXXX, inputData, [])

    print "parse_vhostXXX with minimal valid data:",
    inputData = {
        'Features': [{
            'Limits': {'Crit': 0.5, 'Warn': 0.0},
            'MatchRule': {'Equals': {'http_host': 'blah.example.com'}}
        }],
    }
    expectedResult = {
        'blacklist': [],
        'features': [{
            'Limits': {'Crit': 0.5, 'Warn': 0.0},
            'MatchRule': {'operand': 'blah.example.com', 'field': 'http_host', 'type': 'Equals'}
        }]
    }

    res = validation.parse_vhostXXX(inputData, [])
    assert_equal(res, expectedResult)


def test_parse_monitoring():
    print "parse_monitoring with non dict:",
    inputData = []
    assert_raises(Exception, validation.parse_monitoring, inputData, {})

    print "parse_monitoring with minimal valid data:",
    inputData = {'vhost500': {
        'Features': [{
            'Limits': {'Crit': 0.5, 'Warn': 0},
            'MatchRule': {'Equals': {'http_host': 'blah.example.com'}}
        }],
        'MatchRule': {'Equals': {'http_host': 'blah.example.com'}}
    }}
    validation.parse_monitoring(inputData, {})
