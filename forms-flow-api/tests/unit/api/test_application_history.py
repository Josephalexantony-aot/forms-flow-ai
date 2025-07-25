"""Test suite for application History API endpoint."""

from typing import Dict, List

from formsflow_api_utils.utils import SUBMISSION_VIEW_HISTORY, get_token

from formsflow_api.models import Application


def get_history_create_payload():
    """Returns the payload for creating application history entry."""
    return {
        "applicationId": 1,
        "applicationStatus": "New",
        "formUrl": "http://testsample.com/form/23/submission/3423",
        "submittedBy": "client",
    }


def test_get_application_history_unauthorized(app, client, session):
    """Testing the response of unauthorized application /application/{application_id}/history."""
    rv = client.get("/application/1/history")
    assert rv.status_code == 401


def test_post_application_history_create_method(app, client, session, jwt):
    """Tests the application history create method."""
    token = get_token(jwt)
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    new_application = client.post(
        "/application/1/history",
        headers=headers,
        json=get_history_create_payload(),
    )
    assert new_application.status_code == 201
    assert new_application.json["formId"] == "23"
    assert new_application.json["submissionId"] == "3423"
    assert new_application.json["applicationStatus"] == "New"
    assert new_application.json["submittedBy"] == "client"


def test_get_application_history(app, client, session, jwt):
    """Get the json request for application /application/{application_id}/history."""
    token = get_token(jwt, role=SUBMISSION_VIEW_HISTORY)
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    new_entry = client.post(
        "/application/1/history",
        headers=headers,
        json=get_history_create_payload(),
    )
    assert new_entry.status_code == 201
    rv = client.get("/application/1/history", headers=headers)
    assert rv.status_code == 200
    assert isinstance(rv.json, Dict)
    assert isinstance(rv.json["applications"], List)
    assert len(rv.json["applications"]) == 1
    assert rv.json["applications"][0]["formId"] == "23"
    assert rv.json["applications"][0]["submissionId"] == "3423"
    assert rv.json["applications"][0]["submittedBy"] == "client"
    assert rv.json["applications"][0]["applicationStatus"] == "New"


def test_application_history_get_un_authorized(app, client, session, jwt):
    """Tests if the get endpoint is accessible without authentication."""
    token = get_token(jwt)
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    new_entry = client.post(
        "/application/1/history", headers=headers, json=get_history_create_payload()
    )
    assert new_entry.status_code == 201
    # sending get request withouttoken
    rv = client.get("/application/1/history")
    assert rv.status_code == 401


def create_application_history_service_account(app, client, session, jwt):
    """Tests if the initial application history created with a service account replaced by application creator."""
    application = Application()
    application.created_by = "client"
    application.application_status = "New"
    application.form_process_mapper_id = 1
    application.submission_id = "2345"
    application.latest_form_id = "1234"
    application.save()

    payload = {
        "applicationId": 1,
        "applicationStatus": "New",
        "formUrl": "http://testsample.com/form/23/submission/3423",
        "submittedBy": "service-account-bpmn",
    }
    token = get_token(jwt)
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    new_entry = client.post("/application/1/history", headers=headers, json=payload)
    assert new_entry.status_code == 201
    assert new_entry.submitted_by == "client"
