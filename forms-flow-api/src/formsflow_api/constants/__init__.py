"""App Constants.

Constants file needed for the static values.
"""

from enum import Enum
from http import HTTPStatus

from formsflow_api_utils.exceptions import ErrorCodeMixin

# Static task filter variables.
# These variables are used in the migration & tenant based task filter configuration.

STATIC_TASK_FILTER_VARIABLES = [
    {
        "key": "applicationId",
        "label": "Submission Id",
        "type": "number",
        "name": "applicationId",
        "isChecked": True,
        "sortOrder": 1,
        "isFormVariable": False,
    },
    {
        "key": "submitterName",
        "label": "Submitter Name",
        "type": "textfield",
        "name": "submitterName",
        "isChecked": True,
        "sortOrder": 2,
        "isFormVariable": False,
    },
    {
        "key": "assignee",
        "label": "Assignee",
        "type": "textfield",
        "name": "assignee",
        "isChecked": True,
        "sortOrder": 3,
        "isFormVariable": False,
    },
    {
        "key": "roles",
        "label": "Roles",
        "type": "textfield",
        "name": "roles",
        "isChecked": True,
        "sortOrder": 4,
        "isFormVariable": False,
    },
    {
        "key": "name",
        "label": "Task",
        "type": "textfield",
        "name": "name",
        "isChecked": True,
        "sortOrder": 5,
        "isFormVariable": False,
    },
    {
        "key": "created",
        "label": "Created Date",
        "type": "datetime",
        "name": "created",
        "isChecked": True,
        "sortOrder": 6,
        "isFormVariable": False,
    },
    {
        "key": "formName",
        "label": "Form Name",
        "type": "textfield",
        "name": "formName",
        "isChecked": True,
        "sortOrder": 7,
        "isFormVariable": False,
    },
]


class BusinessErrorCode(ErrorCodeMixin, Enum):
    """Business error codes."""

    FORM_ID_NOT_FOUND = "The specified form ID does not exist", HTTPStatus.BAD_REQUEST
    INVALID_FORM_ID = "Invalid Form ID", HTTPStatus.BAD_REQUEST
    PERMISSION_DENIED = "Insufficient permission", HTTPStatus.FORBIDDEN
    APPLICATION_ID_NOT_FOUND = (
        "The specified application ID does not exist",
        HTTPStatus.BAD_REQUEST,
    )
    PROCESS_DEF_NOT_FOUND = "Process definition does not exist", HTTPStatus.BAD_REQUEST
    PROCESS_NOT_LATEST_VERSION = (
        "Passed process id is not latest version",
        HTTPStatus.BAD_REQUEST,
    )
    MAPPER_NOT_LATEST_VERSION = (
        "The provided mapper ID is not the latest version.",
        HTTPStatus.BAD_REQUEST,
    )
    DECISION_DEF_NOT_FOUND = (
        "Decision definition does not exist",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_AUTH_RESOURCE_ID = (
        "Invalid authorization resource ID",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_FORM_PROCESS_MAPPER_ID = (
        "Invalid form process mapper ID",
        HTTPStatus.BAD_REQUEST,
    )
    NO_DASHBOARD_AUTHORIZED = (
        "No Dashboard authorized Group found",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_INSIGHTS_RESPONSE = (
        "Invalid response received from insights",
        HTTPStatus.BAD_REQUEST,
    )
    INSIGHTS_NOTFOUND = (
        "Analytics is not enabled for this tenant",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_BPM_RESPONSE = "Invalid response received from bpm", HTTPStatus.BAD_REQUEST
    BPM_BASE_URL_NOT_SET = "BPM_API_URL not set environment", HTTPStatus.BAD_REQUEST
    MISSING_PAGINATION_PARAMETERS = (
        "Missing pagination parameters",
        HTTPStatus.BAD_REQUEST,
    )
    DUPLICATE_ROLE = "Duplicate role", HTTPStatus.BAD_REQUEST
    APPLICATION_CREATE_ERROR = "Cannot create application", HTTPStatus.BAD_REQUEST
    DRAFT_APPLICATION_NOT_FOUND = (
        "The specified draft application does not exist",
        HTTPStatus.BAD_REQUEST,
    )
    FILTER_NOT_FOUND = "The specified filter does not exist", HTTPStatus.BAD_REQUEST
    PROCESS_START_ERROR = "Cannot start process instance", HTTPStatus.BAD_REQUEST
    USER_NOT_FOUND = "User not found", HTTPStatus.BAD_REQUEST
    INVALID_PROCESS_DATA = (
        "Invalid process data passed; both data and process type are required",
        HTTPStatus.BAD_REQUEST,
    )
    PROCESS_ID_NOT_FOUND = (
        "The specified process ID does not exist",
        HTTPStatus.BAD_REQUEST,
    )
    THEME_NOT_FOUND = "The specified theme not exist", HTTPStatus.BAD_REQUEST
    THEME_EXIST = "The specified theme already exist", HTTPStatus.BAD_REQUEST
    ROLE_MAPPING_FAILED = "Role mapping failed", HTTPStatus.BAD_REQUEST
    INVALID_FILE_TYPE = "File format not supported", HTTPStatus.BAD_REQUEST
    FILE_NOT_FOUND = "The file not found", HTTPStatus.BAD_REQUEST
    FORM_EXISTS = (
        "Form validation failed: The Name or Path already exists. They must be unique.",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_INPUT = "Invalid input parameter", HTTPStatus.BAD_REQUEST
    INVALID_FORM_VALIDATION_INPUT = (
        "At least one query parameter (title, name, path) must be provided.",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_FORM_TITLE_LENGTH = (
        "The form title should not exceed 200 characters.",
        HTTPStatus.BAD_REQUEST,
    )
    KEYCLOAK_REQUEST_FAIL = (
        "Request to Keycloak Admin APIs failed.",
        HTTPStatus.BAD_REQUEST,
    )
    PROCESS_EXISTS = (
        "The Process name or ID already exists. It must be unique.",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_PROCESS_VALIDATION_INPUT = (
        "At least one query parameter (name, key) must be provided.",
        HTTPStatus.BAD_REQUEST,
    )
    PROCESS_INVALID_OPERATION = (
        "Cannot update a published process",
        HTTPStatus.BAD_REQUEST,
    )
    FORM_INVALID_OPERATION = (
        "Cannot update a published form",
        HTTPStatus.BAD_REQUEST,
    )
    FORM_VALIDATION_FAILED = "FORM_VALIDATION_FAILED.", HTTPStatus.BAD_REQUEST
    INVALID_PROCESS = "Invalid process.", HTTPStatus.BAD_REQUEST
    RESTRICT_FORM_DELETE = (
        "Can't delete the form that has submissions associated with it.",
        HTTPStatus.BAD_REQUEST,
    )
    ADMIN_SERVICE_UNAVAILABLE = (
        "Admin service is not available",
        HTTPStatus.SERVICE_UNAVAILABLE,
    )
    INVALID_ADMIN_RESPONSE = (
        "Invalid response received from admin service",
        HTTPStatus.BAD_REQUEST,
    )
    INVALID_PATH = (
        "The path must not contain: exists, export, role, current, logout, import, form, access, token, recaptcha or end with submission/action.",  # pylint: disable=line-too-long
        HTTPStatus.BAD_REQUEST,
    )
    FORM_NOT_FOUND = "Form not found", HTTPStatus.BAD_REQUEST
    FORM_NOT_PUBLISHED = "Form not published", HTTPStatus.BAD_REQUEST
    FILTER_PREFERENCE_BAD_REQUEST = ("Invalid payload data", HTTPStatus.BAD_REQUEST)
    FILTER_PREFERENCE_DB_ERROR = (
        "Database error while updating filter preferences",
        HTTPStatus.BAD_REQUEST,
    )
    TASK_OUTCOME_NOT_FOUND = (
        "Task outcome configuration not found for the given task Id",
        HTTPStatus.BAD_REQUEST,
    )

    def __new__(cls, message, status_code):
        """Constructor."""
        obj = object.__new__(cls)
        obj._value = status_code
        obj._message = message
        return obj

    @property
    def message(self):
        """Return message."""
        return self._message

    @property
    def status_code(self):
        """Return status code."""
        return self._value


def default_flow_xml_data(name="Defaultflow"):
    """Xml data for default flow."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <bpmn:definitions
        xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
        xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
        xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
        xmlns:camunda="http://camunda.org/schema/1.0/bpmn"
        xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
        xmlns:modeler="http://camunda.org/schema/modeler/1.0"
        id="Definitions_1gblxi8" targetNamespace="http://bpmn.io/schema/bpmn"
        exporter="Camunda Modeler" exporterVersion="4.12.0"
        modeler:executionPlatform="Camunda Platform"
        modeler:executionPlatformVersion="7.15.0">
        <bpmn:process id="{name}" name="{name}" isExecutable="true">
            <bpmn:startEvent id="StartEvent_1" name="Default Flow Started" camunda:asyncAfter="true">
                <bpmn:outgoing>Flow_09rbji4</bpmn:outgoing>
            </bpmn:startEvent>
            <bpmn:task id="Audit_Task_Executed" name="Execute Audit Task">
                <bpmn:extensionElements>
                    <camunda:executionListener event="start">
                        <camunda:script scriptFormat="javascript">execution.setVariable('applicationStatus', 'Completed');</camunda:script>
                    </camunda:executionListener>
                    <camunda:executionListener class="org.camunda.bpm.extension.hooks.listeners.BPMFormDataPipelineListener" event="start">
                        <camunda:field name="fields">
                            <camunda:expression>["applicationId","applicationStatus"]</camunda:expression>
                        </camunda:field>
                    </camunda:executionListener>
                    <camunda:executionListener class="org.camunda.bpm.extension.hooks.listeners.ApplicationStateListener" event="end" />
                </bpmn:extensionElements>
                <bpmn:incoming>Flow_09rbji4</bpmn:incoming>
                <bpmn:outgoing>Flow_0klorcg</bpmn:outgoing>
            </bpmn:task>
            <bpmn:sequenceFlow id="Flow_09rbji4" sourceRef="StartEvent_1" targetRef="Audit_Task_Executed">
                <bpmn:extensionElements>
                    <camunda:executionListener event="take">
                        <camunda:script scriptFormat="javascript">execution.setVariable('applicationStatus', 'New');</camunda:script>
                    </camunda:executionListener>
                    <camunda:executionListener class="org.camunda.bpm.extension.hooks.listeners.ApplicationStateListener" event="take" />
                </bpmn:extensionElements>
            </bpmn:sequenceFlow>
            <bpmn:endEvent id="Event_1ws2h5w" name="Default Flow Ended">
                <bpmn:incoming>Flow_0klorcg</bpmn:incoming>
            </bpmn:endEvent>
            <bpmn:sequenceFlow id="Flow_0klorcg" sourceRef="Audit_Task_Executed" targetRef="Event_1ws2h5w" />
        </bpmn:process>
        <bpmndi:BPMNDiagram id="BPMNDiagram_1">
            <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Defaultflow">
                <bpmndi:BPMNEdge id="Flow_0klorcg_di" bpmnElement="Flow_0klorcg">
                    <di:waypoint x="370" y="117" />
                    <di:waypoint x="432" y="117" />
                </bpmndi:BPMNEdge>
                <bpmndi:BPMNEdge id="Flow_09rbji4_di" bpmnElement="Flow_09rbji4">
                    <di:waypoint x="215" y="117" />
                    <di:waypoint x="270" y="117" />
                </bpmndi:BPMNEdge>
                <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
                    <dc:Bounds x="179" y="99" width="36" height="36" />
                    <bpmndi:BPMNLabel>
                        <dc:Bounds x="166" y="142" width="62" height="27" />
                    </bpmndi:BPMNLabel>
                </bpmndi:BPMNShape>
                <bpmndi:BPMNShape id="Activity_1qmqqen_di" bpmnElement="Audit_Task_Executed">
                    <dc:Bounds x="270" y="77" width="100" height="80" />
                </bpmndi:BPMNShape>
                <bpmndi:BPMNShape id="Event_1ws2h5w_di" bpmnElement="Event_1ws2h5w">
                    <dc:Bounds x="432" y="99" width="36" height="36" />
                    <bpmndi:BPMNLabel>
                        <dc:Bounds x="419" y="142" width="62" height="27" />
                    </bpmndi:BPMNLabel>
                </bpmndi:BPMNShape>
            </bpmndi:BPMNPlane>
        </bpmndi:BPMNDiagram>
    </bpmn:definitions>"""


default_task_variables = [
    {"key": "applicationId", "label": "Submission Id", "type": "hidden"},
    {"key": "applicationStatus", "label": "Submission Status", "type": "hidden"},
    {"key": "submitterLastName", "label": "Submitter Last Name", "type": "hidden"},
    {"key": "submitterFirstName", "label": "Submitter First Name", "type": "hidden"},
    {"key": "submitterEmail", "label": "Submitter Email", "type": "hidden"},
    {"key": "currentUser", "label": "Current User", "type": "hidden"},
    {"key": "currentUserRoles", "label": "Current User Roles", "type": "hidden"},
]
