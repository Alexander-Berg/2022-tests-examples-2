import logging

from sandbox.projects.tv.target_check.common.utils import generate_head_for_html_report


def print_test_pass(key, expected):
    return "<p><font color = #00b300>pass</font> - " + key + ": " + str(expected) + "</p>"


def print_test_fail(key, expected, actual):
    return "<p><font color = #ff0000>fail</font> - " + key + ": " \
           + str(expected) + "(from json config) != " + str(actual) + "(from build rom props)</p>"


def assert_property(expected, actual, key):
    logging.info("assert_property: {} <> {}".format(expected, actual[key]))
    if str(expected) == str(actual[key]):
        logging.info("assert_property: pass")
        return print_test_pass(key, expected)
    else:
        logging.info("assert_property: fail")
        return print_test_fail(key, expected, actual[key])


def assert_fingerprint(json_fingerprint, actual):
    expected = json_fingerprint["props"]["brand"] + "/"
    expected += json_fingerprint["props"]["name"] + "/"
    expected += json_fingerprint["props"]["device"]
    logging.info("assert_fingerprint: \n{}\n<>\n{}".format(expected, actual))
    if str(expected) in str(actual):
        logging.info("assert_fingerprint: pass")
        return print_test_pass("fingerprint", expected)
    else:
        logging.info("assert_fingerprint: fail")
        return print_test_fail("fingerprint", expected, actual)


def compare_props(json_config, build_props, report_path, platform, target):
    json_config = json_config.to_json()
    report = generate_head_for_html_report(platform, target, "Test Report For Target")
    report += "<h2>Properties tests:</h2>"
    if json_config.get("clids") is not None:
        for i in build_props["clids"].keys():
            key = i.split(".")[-1]
            report += assert_property(json_config["clids"][key], build_props["clids"], "yndx.config.{}".format(key))
    else:
        logging.info("Skip test because clids not found in json config")

    report += "<h2>Build props tests:</h2>"
    for i in build_props["product_props"].keys():
        if "fingerprint" in i:
            report += assert_fingerprint(json_config, build_props["product_props"][i])
        else:
            key = i.split(".")[-1]
            report += assert_property(json_config["props"][key], build_props["product_props"],
                                      "ro.product.{}".format(key))

    if build_props.get("uniota_props_keys") is not None:
        report += "<h2>Uniota props tests:</h2>"
        for i in build_props["uniota_props_keys"]:
            report += assert_property(json_config["uniota_props"][i], build_props["uniota_props"],
                                      "ro.yndx.dim.{}".format(i))
    report += "</body></html>"

    html_file = open("{}/test_results.html".format(report_path), "w")
    html_file.write(report)
    html_file.close()
