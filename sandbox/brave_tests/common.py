from enum import Enum


class TestType(Enum):
    FT = 'ft'
    FT_SAAS = 'ft_saas'
    PERFORMANCE = 'performance'
    PERFORMANCE_META = 'performance_meta'
    SANITIZE = 'sanitize'


TESTENV_TEST_NAMES = {
    TestType.FT.value: {
        "bs": "YABS_SERVER_40_FT_BS_SAMPLED",
        "yabs": "YABS_SERVER_40_FT_YABS_SAMPLED",
        "bsrank": "YABS_SERVER_40_FT_BSRANK_SAMPLED",
        "meta_bs": "YABS_SERVER_40_FT_META_BS_A_B_SAMPLED",
        "meta_yabs": "YABS_SERVER_40_FT_META_YABS_A_B_SAMPLED",
        "meta_bsrank": "YABS_SERVER_40_FT_META_BSRANK_A_B_SAMPLED",
    },
    TestType.PERFORMANCE.value: {
        "bs": "YABS_SERVER_40_PERFORMANCE_BEST_BS_SAMPLED",
        "yabs": "YABS_SERVER_40_PERFORMANCE_BEST_YABS_SAMPLED",
        "bsrank": "YABS_SERVER_40_PERFORMANCE_BEST_BSRANK_SAMPLED",
    },
    TestType.PERFORMANCE_META.value: {
        "bs": "YABS_SERVER_45_PERFORMANCE_META_BS_A_B_SAMPLED",
        "yabs": "YABS_SERVER_45_PERFORMANCE_META_YABS_A_B_SAMPLED",
        "bsrank": "YABS_SERVER_45_PERFORMANCE_META_BSRANK_A_B_SAMPLED",
    },
    TestType.FT_SAAS.value: {
        "bs": "YABS_SERVER_40_FT_KVRS_SAAS_BS_SAMPLED",
        "yabs": "YABS_SERVER_40_FT_KVRS_SAAS_YABS_SAMPLED",
    },
}
