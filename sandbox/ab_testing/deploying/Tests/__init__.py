from .TestWeb4ExperimentsReleaseDevDevRunner import AbDeployingTestWeb4ExperimentsReleaseDevDevRunner
from .TestWeb4ExperimentsReleaseProdProdRunner import AbDeployingTestWeb4ExperimentsReleaseProdProdRunner
from .TestFijiExperimentsReleaseImagesRunner import AbDeployingTestFijiExperimentsReleaseImagesRunner
from .TestFijiExperimentsReleaseVideoRunner import AbDeployingTestFijiExperimentsReleaseVideoRunner

# (service, test) see https://st.yandex-team.ru/USEREXP-6913, https://st.yandex-team.ru/USEREXP-6267

WEB_DEV_DEV_RUNNER = ('web', AbDeployingTestWeb4ExperimentsReleaseDevDevRunner, )
WEB_PROD_PROD_RUNNER = ('web', AbDeployingTestWeb4ExperimentsReleaseProdProdRunner, )
VIDEO_PROD_PROD_RUNNER = ('video', AbDeployingTestFijiExperimentsReleaseVideoRunner, )
IMAGES_PROD_PROD_RUNNER = ('images', AbDeployingTestFijiExperimentsReleaseImagesRunner, )

TEST_LIST = [
    WEB_DEV_DEV_RUNNER,
    WEB_PROD_PROD_RUNNER,
    VIDEO_PROD_PROD_RUNNER,
    IMAGES_PROD_PROD_RUNNER,
]

TESTID_TEST_LIST = [
    WEB_PROD_PROD_RUNNER,
    VIDEO_PROD_PROD_RUNNER,
    IMAGES_PROD_PROD_RUNNER,
]

SEARCH_INTERFACES_RELEASE_TEST_LIST = [
    WEB_DEV_DEV_RUNNER,
    WEB_PROD_PROD_RUNNER,
    VIDEO_PROD_PROD_RUNNER,
    IMAGES_PROD_PROD_RUNNER,
]
