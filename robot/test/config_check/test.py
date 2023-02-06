import yatest.common

from robot.jupiter.protos.upload_rules_pb2 import TUploadRuleConfigList
from robot.mercury.cmpy.common.sample import create_sample_config
from robot.mercury.protos.mercury_config_pb2 import TMercuryConfig
from robot.mercury.protos.recuperator_pb2 import TRecuperatorConfig
from robot.library.oxygen.base.protos.tier_scheme_pb2 import TTierScheme
from robot.library.yuppie.modules.environment import Environment

import google.protobuf.text_format as pbtext
import google.protobuf.json_format as pbjson

from os.path import join as pj
import logging
import os
import re


CONFIGS_DIR = "robot/mercury/packages/worker_configs/config"
ALL_CONFIGS_DIRS = (
    CONFIGS_DIR,
    "robot/mercury/packages/configs",
)

TEMPLATE_CONFIG_PROCESSORS = {
    "mercury_config_override_sample.pb.txt": lambda text: create_sample_config(text, "", "", "", 0, 0),
}


def _read_proto_config(path, TMessage):
    with open(path) as inputfile:
        proto_text = inputfile.read()
    message = TMessage()
    pbtext.Parse(proto_text, message)
    return message


def _read_tier_scheme(tier_filename):
    path = yatest.common.build_path(pj(CONFIGS_DIR, tier_filename))
    config = _read_proto_config(path, TTierScheme)
    rule_quotas = {}
    tier_configs = {}
    for quota_config in config.RuleQuotaConfig:
        rule_quotas[quota_config.Name] = quota_config

    for tier_config in config.TierConfig:
        tier_configs[tier_config.TierName] = (tier_config, rule_quotas.get(tier_config.RuleQuotaName))
        tier_config.RuleQuotaName = ""
    return tier_configs


def _read_upload_rules(rules_filename):
    path = yatest.common.build_path(pj(CONFIGS_DIR, rules_filename))
    config = _read_proto_config(path, TUploadRuleConfigList)
    result = {}
    for rule in config.UploadRules:
        result[rule.Name] = rule

    return result


def _test_config(prefix, filename, TMessage, json=False):
    logging.info("Checking %s", filename)
    path = os.path.join(prefix, filename)
    with open(path) as inputfile:
        proto_text = inputfile.read()

    result = re.search(r"{{\w+}}", proto_text)
    if result:
        logging.info("Trying to process template config %s", filename)
        template_processor = TEMPLATE_CONFIG_PROCESSORS.get(filename)
        assert template_processor, "Can't find template processor for template config " + filename
        proto_text = template_processor(proto_text)

    message = TMessage()
    if json:
        pbjson.Parse(proto_text, message)
    else:
        pbtext.Parse(proto_text, message)


def test_callisto_tier():
    mercury_tier_configs = _read_tier_scheme("TierScheme.pb.txt")
    callisto_tier_configs = _read_tier_scheme("TierSchemeCallisto.pb.txt")
    _read_tier_scheme("TierSchemeJupiter.pb.txt")

    mercury_upload_rules = _read_upload_rules("UploadRules.pb.txt")
    callisto_upload_rules = _read_upload_rules("UploadRulesCallisto.pb.txt")
    jupiter_upload_rules = _read_upload_rules("UploadRulesJupiter.pb.txt")

    assert mercury_tier_configs["WebFreshTier"][0] == callisto_tier_configs["WebFreshTier"][0], "There is a diff between Callisto and Mercury WebFreshTier config parameters"

    assert mercury_tier_configs["MercuryTier"][1] == mercury_tier_configs["WebFreshTier"][1], "Mercury MercuryTier's RuleQuotaConfig must be equal to Mercury WebFreshTier's one"

    for pos in xrange(len(mercury_tier_configs["WebFreshTier"][1].RuleQuota)):
        m_quota = mercury_tier_configs["WebFreshTier"][1].RuleQuota[pos]
        assert pos < len(callisto_tier_configs["WebFreshTier"][1].RuleQuota), "Too small Callisto WebFreshTier RuleQuotaConfig"
        c_quota = callisto_tier_configs["WebFreshTier"][1].RuleQuota[pos]
        assert m_quota == c_quota, "Callisto WebFreshTier RuleQuotaConfig must contain all Mercury MercuryTier RuleQuotaConfig rules in the same order (from the begining)"
        assert mercury_upload_rules.get(m_quota.RuleName) == callisto_upload_rules.get(c_quota.RuleName), "Callisto and Mercury WebFreshTier rules '" + m_quota.RuleName + "' are different"
    jupiter_callisto_rule_keys = set(callisto_upload_rules.keys()) & set(jupiter_upload_rules.keys())
    for key in jupiter_callisto_rule_keys:
        assert callisto_upload_rules.get(key) == jupiter_upload_rules.get(key), "Callisto and Jupiter rules '" + key + "' are different"

    for name, rule in mercury_upload_rules.items():
        if name in callisto_upload_rules:
            assert rule == callisto_upload_rules.get(name), "Callisto and Mercury rule '" + name + "' are different"


def test_mercury_configs():
    Environment.setup_logging()
    config_paths = [yatest.common.build_path(path) for path in ALL_CONFIGS_DIRS]

    for config_path in config_paths:
        def get_config_files(prefix):
            return [config for config in os.listdir(config_path) if config.startswith(prefix)]

        for config_file in get_config_files("mercury_config"):
            _test_config(config_path, config_file, TMercuryConfig)

        for config_file in get_config_files("recuperator_config"):
            _test_config(config_path, config_file, TRecuperatorConfig, json=True)
