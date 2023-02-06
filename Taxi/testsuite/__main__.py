import vh3
import sys
from time import sleep
from uuid import uuid4

from taxi.ml.nirvana.common import TaxiMlContext

from .helper import test_operations


def run_tests():
    """
    This is a single test, because we got a time limit
    and we need it all to run asap,
    so we have to make it a single graph
    """

    with vh3.Profile.from_file(
        context_class=TaxiMlContext,
        quota="taximl",
        yt_cluster="hahn",
        dev_mode=True,
        workflow=vh3.Workflow(name="8b093cc6-7aec-421a-86cd-9e84eb5c0927"),
        data_ttl_days=1,
    ).build(vh3.WorkflowInstance) as wi:
        test_operations()
    wi.run()
    print(wi.url, file=sys.stderr)
    sleep(120)
    assert wi.get_result() == vh3.graph.state.Result.success


if __name__ == "__main__":
    run_tests()
