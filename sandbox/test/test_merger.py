import merger


def make_test(id, status="OK", error_type=None, links={}, metrics={}, type="test"):
    return locals()


def test_merge_metrics():
    merged = merger.merge({
        "link1": [
            make_test(1, metrics={"metric1": 1, "metric2?aggr=median": 1}),
        ],
        "link2": [
            make_test(1, metrics={"metric1": 2, "metric2?aggr=median": 3}),
        ],
    })[0]
    assert merged["id"] == 1
    assert merged["metrics"]["metric1"] == 1.5
    assert merged["metrics"]["metric2"] == 2.0


def test_test_status():
    merged = merger.merge({
        "link1": [make_test(1, "OK")],
        "link2": [make_test(1, "OK")],
    })[0]

    assert merged["status"] == "OK"
    assert merged["error_type"] is None

    merged = merger.merge({
        "link1": [make_test(1, "OK")],
        "link2": [make_test(1, "FAILED")],
    })[0]

    assert merged["status"] == "FAILED"
    assert merged["error_type"] == "REGULAR"

    merged = merger.merge({
        "link1": [make_test(1, "SKIPPED")],
        "link2": [make_test(1, "SKIPPED")],
    })[0]

    assert merged["status"] == "SKIPPED"
    assert merged["error_type"] is None

    merged = merger.merge({
        "link1": [make_test(1, "FAILED", "FLAKY")],
        "link2": [make_test(1, "FAILED", "FLAKY")],
    })[0]

    assert merged["status"] == "FAILED"
    assert merged["error_type"] == "FLAKY"

    merged = merger.merge({
        "link1": [make_test(1, "FAILED", "FLAKY")],
        "link2": [make_test(1, "FAILED", "REGULAR")],
    })[0]

    assert merged["status"] == "FAILED"
    assert merged["error_type"] == "REGULAR"

    merged = merger.merge({
        "link1": [make_test(1), make_test(2)],
        "link2": [make_test(2)],
    })

    assert merged[0]["id"] == 1
    assert merged[0]["status"] == "FAILED"
    assert merged[0]["error_type"] == "REGULAR"

    assert merged[1]["id"] == 2
    assert merged[1]["status"] == "OK"
    assert merged[1]["error_type"] is None

    merged = merger.merge({
        "link1": [make_test(2, "FAILED")],
        "link2": [make_test(2, "FAILED")],
    })

    assert merged[0]["rich-snippet"] == "[[bad]]FAILED[[rst]]: task ([[path]]link2[[rst]])\n[[bad]]FAILED[[rst]]: task ([[path]]link1[[rst]])"

    merged = merger.merge({
        "link1": [make_test(2, "OK")],
        "link2": [make_test(2, "OK")],
        "link3": [make_test(2, "FAILED")],
    })
    assert merged[0]["status"] == "FAILED"

    merged = merger.merge({
        "link1": [make_test(2, "OK")],
        "link2": [make_test(2, "OK")],
        "link3": [make_test(2, "FAILED")],
    }, quorum_count=1)
    assert merged[0]["status"] == "OK"


def test_snippet():
    merged = merger.merge({
        "link1": [
            make_test(1, links={"link1": ["path1"], "link2": ["path2"]}),
            make_test(2, "FAILED", "REGULAR", links={"link3": ["path3"], "link4": ["path4"]}),
            make_test(3, "SKIPPED", links={"link5": ["path5"], "link6": ["path6"]}),
        ],
        "link2": [
            make_test(2, "FAILED", "REGULAR", links={"link7": ["path7"]}),
            make_test(3, "SKIPPED", links={"link8": ["path8"], "link9": ["path9"]}),
        ],
    })

    assert merged[0]["id"] == 1
    assert merged[0]["status"] == "FAILED"
    assert merged[0]["error_type"] == "REGULAR"
    assert merged[0]["rich-snippet"] == "[[bad]]NO_DATA[[rst]]: [[path]]link2[[rst]]\n[[good]]OK[[rst]]: link1 ([[path]]path1[[rst]]), link2 ([[path]]path2[[rst]])"

    assert merged[1]["id"] == 2
    assert merged[1]["status"] == "FAILED"
    assert merged[1]["error_type"] == "REGULAR"
    assert merged[1]["rich-snippet"] == "[[bad]]FAILED[[rst]]: link7 ([[path]]path7[[rst]])\n[[bad]]FAILED[[rst]]: link4 ([[path]]path4[[rst]]), link3 ([[path]]path3[[rst]])"

    assert merged[2]["id"] == 3
    assert merged[2]["status"] == "SKIPPED"
    assert merged[2]["error_type"] is None
    assert merged[2]["rich-snippet"] == "[[alt]]SKIPPED[[rst]]: link5 ([[path]]path5[[rst]]), link6 ([[path]]path6[[rst]])\n[[alt]]SKIPPED[[rst]]: link9 ([[path]]path9[[rst]]), link8 ([[path]]path8[[rst]])"


def test_links():
    merged = merger.merge({
        "link1": [
            make_test(1, links={"link1": ["path1"], "link2": ["path2"]}),
        ],
        "link2": [
            make_test(1, links={"link1": ["path3"], "link2": ["path4"]}),
        ],
    })[0]

    assert merged["links"] == {
        "link1_1": ["path1"], "link2_1": ["path2"],
        "link1_2": ["path3"], "link2_2": ["path4"],
    }


def test_with_quorum_count_no_data():
    merged = merger.merge({
        "link1": [
            make_test(1, links={"link1": ["path1"], "link2": ["path2"]}),
            make_test(2, "FAILED", "REGULAR", links={"link3": ["path3"], "link4": ["path4"]}),
            make_test(3, "SKIPPED", links={"link5": ["path5"], "link6": ["path6"]}),
        ],
        "link2": [
            make_test(1, links={"link1": ["path1"], "link2": ["path2"]}),
            make_test(2, "FAILED", "REGULAR", links={"link3": ["path3"], "link4": ["path4"]}),
            make_test(3, "SKIPPED", links={"link5": ["path5"], "link6": ["path6"]}),
        ],
        "link3": [
            make_test(2, "FAILED", "REGULAR", links={"link7": ["path7"]}),
            make_test(3, "SKIPPED", links={"link8": ["path8"], "link9": ["path9"]}),
        ],
    }, quorum_count=2)

    assert merged[0]["id"] == 1
    assert merged[0]["status"] == "OK"
    assert merged[0]["rich-snippet"] == "[[bad]]NO_DATA[[rst]]: [[path]]link3[[rst]]\n[[good]]OK[[rst]]: link1 ([[path]]path1[[rst]]), link2 ([[path]]path2[[rst]])\n[[good]]OK[[rst]]: link1 ([[path]]path1[[rst]]), link2 ([[path]]path2[[rst]])"


def test_with_quorum_count_failed():
    merged = merger.merge({
        "link1": [
            make_test(1, "FAILED", "REGULAR", links={"link1": ["path1"], "link2": ["path2"]}),
        ],
        "link2": [
            make_test(1, links={"link1": ["path1"], "link2": ["path2"]}),
        ],
        "link3": [
            make_test(1, links={"link1": ["path1"], "link2": ["path2"]}),
        ],
    }, quorum_count=2)

    assert merged[0]["id"] == 1
    assert merged[0]["status"] == "OK"


def test_with_skilled():
    merged = merger.merge({
        "link1": [
            make_test(1, "SKIPPED"),
        ],
        "link2": [
            make_test(1, "SKIPPED"),
        ],
        "link3": [
            make_test(1, "SKIPPED"),
        ],
    }, quorum_count=2)

    assert merged[0]["id"] == 1
    assert merged[0]["status"] == "SKIPPED"
