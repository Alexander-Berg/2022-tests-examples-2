from . import db_helpers


def check_failed_response(response, req, check_message=True):
    assert response.status_code == req.status_code
    resp_json = response.json()
    assert len(resp_json) == 2
    assert resp_json['code'] == req.code
    if check_message:
        assert resp_json['message'] == req.message
    else:
        assert len(resp_json['message']) > 1


def check_db_response_and_req(db_response, req):
    assert db_response == [req]
    result_req = db_response[0]
    assert len(result_req.req_id) > 1
    return result_req


def select_and_check_req_in_db(pgsql, req):
    db_response = db_helpers.select_mark_events_requests(pgsql)
    return check_db_response_and_req(db_response, req)


def insert_and_check_req_in_db(pgsql, req):
    db_response = db_helpers.insert_mark_events_requests(pgsql, req)
    return check_db_response_and_req(db_response, req)
