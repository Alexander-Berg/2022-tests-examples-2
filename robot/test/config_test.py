from json import dumps
import os

from robot.cmpy.library.config import (
    CmpyConfigException,
    Config,
    NonOverridableConfig,
    OverridableConfig,
    ensure_config_correctness)


def create_correct_config(config_type=NonOverridableConfig):
    cfg = config_type()

    cfg.BoolVar = True
    cfg.Cleanup.SpreadSampleStates = 4
    cfg.DeployDelay.ForProduction = 1000
    cfg.Flag = False
    cfg.Indie.TameImpala = "pop"
    cfg.Indie.The.Killers = "rock"
    cfg.Metallica = "en"
    cfg.RammStein = "ger"
    cfg.RobotTierRatio = 0.5

    cfg.freeze()
    return cfg


def create_incorrect_config(config_type=NonOverridableConfig):
    cfg = config_type()

    cfg.Bool.Var = True
    cfg.BoolVar = True
    cfg.Indie.TameImpala = "pop1"
    cfg.Indie.Tame.Impala = "pop2"

    cfg.freeze()
    return cfg


def compare_configs(pure, modified):
    assert type(pure) == type(modified)
    if isinstance(pure, Config):
        for key in (key for key in pure.keys() if not key.startswith('__')):
            assert key in modified
            compare_configs(pure[key], modified[key])
    elif isinstance(pure, str):
        assert modified == "_" + pure
    elif isinstance(pure, bool):
        assert modified != pure
    elif isinstance(pure, int):
        assert modified == pure * 7
    elif isinstance(pure, float):
        assert modified == pure * 0.3


def try_modify_freezed(cfg):
    try:
        cfg.Some.Random.Name = "value"
        assert False, "Freezed config successfully modified!"
    except CmpyConfigException:
        pass  # Ok, unable to modify freezed config.


def try_set_second_time(cfg):
    is_overridable = isinstance(cfg, OverridableConfig)
    msg = "The variable was{} overwritten!".format(" not" if is_overridable else "")

    original_value = cfg.Metallica
    cfg.Metallica = "ger"
    assert is_overridable ^ (original_value == cfg.Metallica), msg

    original_value = cfg.Indie.TameImpala
    cfg.Indie.TameImpala = "dance"
    assert is_overridable ^ (original_value == cfg.Indie.TameImpala), msg


def try_get_from_env(value):
    os.environ["Env.Var"] = str(value) if type(value) != bool else str(value).lower()
    os.environ["New.Var"] = dumps(value) if type(value) != str else value
    cfg = NonOverridableConfig()
    cfg.Env.Var = None
    cfg.New.Var = None
    cfg.freeze()

    if not isinstance(value, bool):
        assert cfg.Env.Var == value
    assert cfg.New.Var == value


def do_test_constraints(config_type):
    cfg = create_correct_config(config_type)
    try_modify_freezed(cfg)
    try_set_second_time(cfg)


def test_non_overridable_constraints():
    do_test_constraints(NonOverridableConfig)


def test_overridable_constraints():
    do_test_constraints(OverridableConfig)


def test_getenv():
    pure_cfg = create_correct_config()

    os.environ["BoolVar"] = "false"
    os.environ["Cleanup.SpreadSampleStates"] = str(7 * 4)  # Should be used as config variable value
    os.environ["CLEANUP_SPREAD_SAMPLE_STATES"] = str(123)  # Should NOT be used as config variable value
    os.environ["DEPLOY_DELAY_FOR_PRODUCTION"] = str(7 * 1000)
    os.environ["FLAG"] = "true"
    os.environ["INDIE_TAME_IMPALA"] = "_pop"
    os.environ["INDIE_THE_KILLERS"] = "_rock"
    os.environ["METALLICA"] = "_en"
    os.environ["RAMM_STEIN"] = "_ger"
    os.environ["ROBOT_TIER_RATIO"] = str(0.5 * 0.3)

    modified_cfg = create_correct_config()
    compare_configs(pure_cfg, modified_cfg)


def test_cast():
    for x in (100500, -12.3, "a/B/a", True, False):
        try_get_from_env(x)


def test_ensure_config_correctness_success():
    config = create_correct_config()
    ensure_config_correctness(config)


def test_ensure_config_correctness_failure():
    config = create_incorrect_config()
    try:
        ensure_config_correctness(config)
        assert False, "Incorrect config must trigger CmpyConfigException."
    except CmpyConfigException:
        pass  # Ok.
