from sandbox.projects.websearch.begemot.common import BegemotService, BegemotResources


def test_SNAKE_CASE():
    assert BegemotService._upper_snake_case('') == ""
    assert BegemotService._upper_snake_case('Bravo') == "BRAVO"
    assert BegemotService._upper_snake_case('ServiceWizard') == "SERVICE_WIZARD"
    assert BegemotService._upper_snake_case('MisspellFeatures2') == "MISSPELL_FEATURES_2"
    assert BegemotService._upper_snake_case('WorkerABCdA') == "WORKER_ABCD_A"
    assert BegemotService._upper_snake_case('ImagesCV') == "IMAGES_CV"
    assert BegemotService._upper_snake_case('Worker23') == "WORKER_23"


def test_assumptions():
    # These assumptions are used in sandbox/projects/release_machine/components/configs/begemot.py :
    assert BegemotResources.Binaries[0] == BegemotResources.MainBinary
    assert BegemotResources.Common[0] == BegemotResources.MainBinary
