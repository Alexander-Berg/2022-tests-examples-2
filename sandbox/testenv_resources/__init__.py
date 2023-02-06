# -*- coding: utf-8 -*-


class Resource(object):
    DbName = 'voicetech-trunk'  # use for build autoupdate attr name

    def __init__(
        self, name, sandboxName=None, nameBuilderTest=None,
        autoUpdate=False, releaseArch=None, forceUpdate=None,
        db=None, attrNameMixin='',
    ):
        self.Name = name
        self.SandboxName = sandboxName if sandboxName else name
        self.NameBuilderTest = nameBuilderTest
        self.AttrName = None
        self.DbName = ''
        if autoUpdate:
            self.attrName = 'autoupdate_resources_{}{}_task_id'.format(
                attrNameMixin, self.DbName.replace('-', '_'))
        if db:
            self.DbName = db
        self.AutoUpdate = autoUpdate
        self.ReleaseArch = releaseArch
        self.ForceUpdate = forceUpdate

    def CreateSimilar(self, test_type, db=None):
        params = {
            'autoUpdate': self.AutoUpdate,
            'releaseArch': self.ReleaseArch,
            'forceUpdate': self.ForceUpdate,
            'db': db,
            'attrNameMixin': test_type.lower().replace('-', '_'),
        }

        nameBuilderTest = (test_type.upper() + '_' + self.NameBuilderTest) if self.NameBuilderTest else None
        params['nameBuilderTest'] = nameBuilderTest
        return Resource(
            test_type.upper() + '_' + self.Name,
            self.SandboxName,
            **params
        )


class AsrServerResource(Resource):
    db = 'voicetech-asr-server-trunk'


VOICETECH_ASR_SERVER = AsrServerResource(
    'VOICETECH_ASR_SERVER',
    nameBuilderTest='BUILD_ASR_SERVER',
)

VOICETECH_ASR_SERVER_GPU = AsrServerResource(
    'VOICETECH_ASR_SERVER_GPU',
    nameBuilderTest='BUILD_ASR_SERVER_GPU',
)

VOICETECH_ASR_SERVER_RUNNER = AsrServerResource(
    'VOICETECH_ASR_SERVER_RUNNER',
    nameBuilderTest='BUILD_ASR_SERVER_GPU',
)

VOICETECH_ASR_SERVER_EVLOGDUMP = AsrServerResource(
    'VOICETECH_EVLOGDUMP',
    nameBuilderTest='BUILD_ASR_SERVER_GPU',
)

VOICETECH_SERVER_CONFIG = AsrServerResource(
    'VOICETECH_SERVER_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_CONFIG = AsrServerResource(
    'VOICETECH_ASR_SERVER_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_RU_RU_DIALOGENERALGPU_CONFIG = AsrServerResource(
    'VOICETECH_ASR_SERVER_RU_RU_DIALOGENERALGPU_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_CONFIG = AsrServerResource(
    'VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_RU_RU_TVGENERALGPU_CONFIG = AsrServerResource(
    'VOICETECH_ASR_SERVER_RU_RU_TVGENERALGPU_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU_CONFIG = AsrServerResource(
    'VOICETECH_ASR_SERVER_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_MULTITOPIC_RU_TR_DIALOGMAPSGPU_CONFIG = AsrServerResource(
    'VOICETECH_ASR_SERVER_MULTITOPIC_RU_TR_DIALOGMAPSGPU_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_MRGC = AsrServerResource(
    'VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_MRGC',
    autoUpdate=True,
)

VOICETECH_ASR_NN_SERVER_RU_RU_QUASARGENERALGPU_CONFIG = AsrServerResource(
    'VOICETECH_ASR_NN_SERVER_RU_RU_QUASARGENERALGPU_CONFIG',
    autoUpdate=True,
)

VOICETECH_ASR_RU_RU_DIALOGENERALGPU = AsrServerResource(
    'VOICETECH_ASR_RU_RU_DIALOGENERALGPU',
    nameBuilderTest='BUILD_ASR_LINGWARE_RU_DIALOG_GENERAL_E2E',
)


VOICETECH_ASR_RU_RU_QUASARGENERALGPU = AsrServerResource(
    'VOICETECH_ASR_RU_RU_QUASARGENERALGPU',
    nameBuilderTest='BUILD_ASR_LINGWARE_RU_QUASAR_GENERAL_E2E',
)

VOICETECH_ASR_RU_RU_TVGENERALGPU = AsrServerResource(
    'VOICETECH_ASR_RU_RU_TVGENERALGPU',
    nameBuilderTest='BUILD_ASR_LINGWARE_RU_TV_GENERAL_E2E',
)

VOICETECH_ASR_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU = AsrServerResource(
    'VOICETECH_ASR_MULTITOPIC_RU_RU_QUASARGENERALGPU_RU_RU_TVGENERALGPU',
    nameBuilderTest='BUILD_ASR_LINGWARE_MULTITOPIC_RU_QUASAR_TV_E2E',
)

VOICETECH_ASR_MULTITOPIC_RU_RU_DIALOGMAPSGPU_TR_TR_DIALOGMAPSGPU = AsrServerResource(
    'VOICETECH_ASR_MULTITOPIC_RU_RU_DIALOGMAPSGPU_TR_TR_DIALOGMAPSGPU',
    nameBuilderTest='BUILD_ASR_LINGWARE_MULTITOPIC_RU_TR_DIALOG_MAPS_E2E',
)

# deprecate:
VOICETECH_YALDI_RU_RU_DIALOGENERALGPU = AsrServerResource(
    'VOICETECH_YALDI_RU_RU_DIALOGENERALGPU',
    autoUpdate=True,
)

VOICETECH_SERVER_REVERSE_NORMALIZER_DATA = AsrServerResource(
    'VOICETECH_SERVER_REVERSE_NORMALIZER_DATA',
    nameBuilderTest='BUILD_ASR_NORMALIZER_DATA',
)

VOICETECH_SERVER_PUNCTUATION_DATA = AsrServerResource(
    'VOICETECH_SERVER_PUNCTUATION_DATA',
    nameBuilderTest='BUILD_ASR_PUNCTUATION_DATA',
)

VOICETECH_SERVER_BIOMETRY_DATA = AsrServerResource(
    'VOICETECH_SERVER_BIOMETRY_DATA',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_SANITY_JOBS = AsrServerResource(
    'VOICETECH_ASR_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_SANITY_JOBS_RU_DIALOG_GENERAL_E2E = AsrServerResource(
    'VOICETECH_ASR_SERVER_SANITY_JOBS_RU_DIALOG_GENERAL_E2E',
    sandboxName='VOICETECH_ASR_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_SANITY_JOBS_RU_QUASAR_GENERAL_E2E = AsrServerResource(
    'VOICETECH_ASR_SERVER_SANITY_JOBS_RU_QUASAR_GENERAL_E2E',
    sandboxName='VOICETECH_ASR_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_QUASAR_TV_E2E = AsrServerResource(
    'VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_QUASAR_TV_E2E',
    sandboxName='VOICETECH_ASR_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_TR_DIALOG_MAPS_E2E = AsrServerResource(
    'VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_TR_DIALOG_MAPS_E2E',
    sandboxName='VOICETECH_ASR_SERVER_SANITY_JOBS',
    autoUpdate=True,
)


class AsrLingwareType(object):
    def __init__(self, config_resource, lingware_resource, sanity_jobs_resource, mrgc_resource, nn_config_resouce):
        self.config_resource = config_resource
        self.lingware_resource = lingware_resource
        self.sanity_jobs_resource = sanity_jobs_resource
        self.mrgc_resource = mrgc_resource
        self.nn_config_resouce = nn_config_resouce


# linware_type after lowercasing MUST be equal one of folder arcadia voicetech/asr/lingware/*
ASR_LINGWARE_TYPES = {
    'RU_DIALOG_GENERAL_E2E': AsrLingwareType(
        VOICETECH_ASR_SERVER_RU_RU_DIALOGENERALGPU_CONFIG,
        VOICETECH_ASR_RU_RU_DIALOGENERALGPU,
        VOICETECH_ASR_SERVER_SANITY_JOBS_RU_DIALOG_GENERAL_E2E,
        mrgc_resource=None,
        nn_config_resouce=None,
    ),
    'RU_QUASAR_GENERAL_E2E': AsrLingwareType(
        VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_CONFIG,
        VOICETECH_ASR_RU_RU_QUASARGENERALGPU,
        VOICETECH_ASR_SERVER_SANITY_JOBS_RU_QUASAR_GENERAL_E2E,
        mrgc_resource=VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_MRGC,
        nn_config_resouce=VOICETECH_ASR_NN_SERVER_RU_RU_QUASARGENERALGPU_CONFIG,
    ),
    'RU_TV_GENERAL_E2E': AsrLingwareType(
        VOICETECH_ASR_SERVER_RU_RU_TVGENERALGPU_CONFIG,
        VOICETECH_ASR_RU_RU_TVGENERALGPU,
        sanity_jobs_resource=None,
        mrgc_resource=None,
        nn_config_resouce=None
    ),
    'MULTITOPIC_RU_QUASAR_TV_E2E': AsrLingwareType(
        VOICETECH_ASR_SERVER_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU_CONFIG,
        VOICETECH_ASR_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU,
        VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_QUASAR_TV_E2E,
        mrgc_resource=None,
        nn_config_resouce=None,
    ),
    'MULTITOPIC_RU_TR_DIALOG_MAPS_E2E': AsrLingwareType(
        VOICETECH_ASR_SERVER_MULTITOPIC_RU_TR_DIALOGMAPSGPU_CONFIG,
        VOICETECH_ASR_MULTITOPIC_RU_RU_DIALOGMAPSGPU_TR_TR_DIALOGMAPSGPU,
        VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_TR_DIALOG_MAPS_E2E,
        mrgc_resource=None,
        nn_config_resouce=None,
    ),
}


class TtsServerResource(Resource):
    db = 'voicetech-tts-server-trunk'


VOICETECH_TTS_SERVER = TtsServerResource(
    'VOICETECH_TTS_SERVER',
    nameBuilderTest='BUILD_TTS_SERVER',
)

VOICETECH_TTS_SERVER_GPU = TtsServerResource(
    'VOICETECH_TTS_SERVER_GPU',
    nameBuilderTest='BUILD_TTS_SERVER_GPU',
)

VOICETECH_TTS_SERVER_EVLOGDUMP = TtsServerResource(
    'VOICETECH_EVLOGDUMP',
    nameBuilderTest='BUILD_TTS_SERVER_GPU',
)

VOICETECH_TTS_SERVER_RUNNER = TtsServerResource(
    'VOICETECH_TTS_SERVER_RUNNER',
    nameBuilderTest='BUILD_TTS_SERVER_GPU',
)

VOICETECH_TTS_RU_GPU = TtsServerResource(
    'VOICETECH_TTS_RU_GPU',
    nameBuilderTest='BUILD_TTS_LINGWARE_RU_E2E',
)

VOICETECH_TTS_RU_MULTISPEAKER_GPU = TtsServerResource(
    'VOICETECH_TTS_RU_MULTISPEAKER_GPU',
    nameBuilderTest='BUILD_TTS_LINGWARE_RU_MULTISPEAKER_E2E',
)

VOICETECH_TTS_RU_VALTZ_GPU = TtsServerResource(
    'VOICETECH_TTS_RU_VALTZ_GPU',
    nameBuilderTest='BUILD_TTS_LINGWARE_RU_VALTZ_E2E',
)

VOICETECH_TTS_TR_GPU = TtsServerResource(
    'VOICETECH_TTS_TR_GPU',
    nameBuilderTest='BUILD_TTS_LINGWARE_TR_E2E',
)

VOICETECH_TTS_SERVER_SANITY_JOBS_RU_E2E = AsrServerResource(
    'VOICETECH_TTS_SERVER_SANITY_JOBS_RU_E2E',
    sandboxName='VOICETECH_TTS_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_TTS_SERVER_SANITY_JOBS_RU_OKSANA_E2E = AsrServerResource(
    'VOICETECH_TTS_SERVER_SANITY_JOBS_RU_OKSANA_E2E',
    sandboxName='VOICETECH_TTS_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_TTS_SERVER_SANITY_JOBS_RU_VALTZ_E2E = AsrServerResource(
    'VOICETECH_TTS_SERVER_SANITY_JOBS_RU_VALTZ_E2E',
    sandboxName='VOICETECH_TTS_SERVER_SANITY_JOBS',
    autoUpdate=True,
)

VOICETECH_TTS_SERVER_SANITY_JOBS_TR_E2E = AsrServerResource(
    'VOICETECH_TTS_SERVER_SANITY_JOBS_TR_E2E',
    sandboxName='VOICETECH_TTS_SERVER_SANITY_JOBS',
    autoUpdate=True,
)


class TtsLingwareType(object):
    def __init__(self, lingware_resource, sanity_jobs_resource):
        self.lingware_resource = lingware_resource
        self.sanity_jobs_resource = sanity_jobs_resource


# linware_type after lowercasing MUST be equal one of folder arcadia voicetech/tts/lingware/*
TTS_LINGWARE_TYPES = {
    'RU_E2E': TtsLingwareType(
        VOICETECH_TTS_RU_GPU,
        VOICETECH_TTS_SERVER_SANITY_JOBS_RU_E2E,
    ),
    'RU_VALTZ_E2E': TtsLingwareType(
        VOICETECH_TTS_RU_VALTZ_GPU,
        VOICETECH_TTS_SERVER_SANITY_JOBS_RU_VALTZ_E2E,
    ),
    'RU_MULTISPEAKER_E2E': TtsLingwareType(
        VOICETECH_TTS_RU_MULTISPEAKER_GPU,
        VOICETECH_TTS_SERVER_SANITY_JOBS_RU_OKSANA_E2E,
    ),
    'TR_E2E': TtsLingwareType(
        VOICETECH_TTS_TR_GPU,
        VOICETECH_TTS_SERVER_SANITY_JOBS_TR_E2E,
    ),
}


class UniproxyResource(Resource):
    db = 'alice-uniproxy-trunk'


VOICETECH_UNIPROXY_EXPERIMENTS = UniproxyResource(
    'VOICETECH_UNIPROXY_EXPERIMENTS',
    nameBuilderTest='BUILD_UNIPROXY_EXPERIMENTS',
)

VOICETECH_UNIPROXY_PACKAGE = UniproxyResource(
    'VOICETECH_UNIPROXY_PACKAGE',
    nameBuilderTest='BUILD_UNIPROXY_PACKAGE',
)

VOICETECH_CUTTLEFISH_PACKAGE = UniproxyResource(
    'VOICETECH_CUTTLEFISH_PACKAGE',
    nameBuilderTest='BUILD_CUTTLEFISH_PACKAGE',
)


class BioServerResource(Resource):
    db = 'voicetech-bio-server-trunk'


VOICETECH_BIO_SERVER = BioServerResource(
    'VOICETECH_BIO_SERVER',
    nameBuilderTest='BUILD_BIO_SERVER',
)


VOICETECH_BIO_SERVER_RUNNER = BioServerResource(
    'VOICETECH_BIO_SERVER_RUNNER',
    nameBuilderTest='BUILD_BIO_SERVER',
)


VOICETECH_BIO_SERVER_EVLOGDUMP = BioServerResource(
    'VOICETECH_EVLOGDUMP',
    nameBuilderTest='BUILD_BIO_SERVER',
)


VOICETECH_ASR_SERVER_BIO_QUASAR_CONFIG = BioServerResource(
    'VOICETECH_ASR_SERVER_BIO_QUASAR_CONFIG',
    autoUpdate=True
)


VOICETECH_ASR_SERVER_SANITY_JOBS_BIO_QUASAR = BioServerResource(
    'VOICETECH_ASR_SERVER_SANITY_JOBS_BIO_QUASAR',
    sandboxName='VOICETECH_ASR_SERVER_SANITY_JOBS',
    autoUpdate=True,
)


VOICETECH_BIO_QUASAR = BioServerResource(
    'VOICETECH_BIO_QUASAR',
    nameBuilderTest='BUILD_ASR_LINGWARE_BIO_QUASAR',
)


ALL_TESTENV_RESOURCES = [
    VOICETECH_ASR_SERVER,
    VOICETECH_ASR_SERVER_GPU,
    VOICETECH_ASR_SERVER_RUNNER,
    VOICETECH_ASR_SERVER_EVLOGDUMP,
    VOICETECH_SERVER_CONFIG,
    VOICETECH_ASR_SERVER_CONFIG,
    VOICETECH_ASR_SERVER_RU_RU_DIALOGENERALGPU_CONFIG,
    VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_CONFIG,
    VOICETECH_ASR_SERVER_RU_RU_TVGENERALGPU_CONFIG,
    VOICETECH_ASR_SERVER_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU_CONFIG,
    VOICETECH_ASR_SERVER_MULTITOPIC_RU_TR_DIALOGMAPSGPU_CONFIG,
    VOICETECH_ASR_SERVER_RU_RU_QUASARGENERALGPU_MRGC,
    VOICETECH_ASR_NN_SERVER_RU_RU_QUASARGENERALGPU_CONFIG,
    VOICETECH_ASR_RU_RU_DIALOGENERALGPU,
    VOICETECH_ASR_RU_RU_QUASARGENERALGPU,
    VOICETECH_ASR_RU_RU_TVGENERALGPU,
    VOICETECH_ASR_MULTITOPIC_RU_RU_QUASARGENERALGPU_TVGENERALGPU,
    VOICETECH_ASR_MULTITOPIC_RU_RU_DIALOGMAPSGPU_TR_TR_DIALOGMAPSGPU,
    VOICETECH_YALDI_RU_RU_DIALOGENERALGPU,
    VOICETECH_SERVER_REVERSE_NORMALIZER_DATA,
    VOICETECH_SERVER_PUNCTUATION_DATA,
    VOICETECH_SERVER_BIOMETRY_DATA,
    VOICETECH_ASR_SERVER_SANITY_JOBS,
    VOICETECH_ASR_SERVER_SANITY_JOBS_RU_DIALOG_GENERAL_E2E,
    VOICETECH_ASR_SERVER_SANITY_JOBS_RU_QUASAR_GENERAL_E2E,
    VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_QUASAR_TV_E2E,
    VOICETECH_ASR_SERVER_SANITY_JOBS_MULTITOPIC_RU_TR_DIALOG_MAPS_E2E,
    VOICETECH_TTS_SERVER,
    VOICETECH_TTS_SERVER_GPU,
    VOICETECH_TTS_SERVER_EVLOGDUMP,
    VOICETECH_TTS_SERVER_RUNNER,
    VOICETECH_TTS_RU_GPU,
    VOICETECH_TTS_RU_MULTISPEAKER_GPU,
    VOICETECH_TTS_RU_VALTZ_GPU,
    VOICETECH_TTS_TR_GPU,
    VOICETECH_TTS_SERVER_SANITY_JOBS_RU_E2E,
    VOICETECH_TTS_SERVER_SANITY_JOBS_RU_OKSANA_E2E,
    VOICETECH_TTS_SERVER_SANITY_JOBS_RU_VALTZ_E2E,
    VOICETECH_TTS_SERVER_SANITY_JOBS_TR_E2E,
    VOICETECH_UNIPROXY_EXPERIMENTS,
    VOICETECH_UNIPROXY_PACKAGE,
    VOICETECH_CUTTLEFISH_PACKAGE,
    VOICETECH_BIO_SERVER,
    VOICETECH_BIO_SERVER_RUNNER,
    VOICETECH_BIO_SERVER_EVLOGDUMP,
    VOICETECH_ASR_SERVER_BIO_QUASAR_CONFIG,
    VOICETECH_ASR_SERVER_SANITY_JOBS_BIO_QUASAR,
    VOICETECH_BIO_QUASAR,
]
