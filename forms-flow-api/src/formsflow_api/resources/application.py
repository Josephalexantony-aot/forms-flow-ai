"""API endpoints for managing application resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields
from formsflow_api_utils.utils import (
    ANALYZE_SUBMISSIONS_VIEW,
    CREATE_DESIGNS,
    CREATE_SUBMISSIONS,
    MANAGE_TASKS,
    NEW_APPLICATION_STATUS,
    VIEW_SUBMISSIONS,
    VIEW_TASKS,
    auth,
    cors_preflight,
    get_form_and_submission_id_from_form_url,
    profiletime,
    submission_response,
)

from formsflow_api.schemas import (
    ApplicationListReqSchema,
    ApplicationListRequestSchema,
    ApplicationSchema,
    ApplicationSubmissionSchema,
    ApplicationUpdateSchema,
)
from formsflow_api.services import ApplicationService, DraftService

API = Namespace(
    "Application",
    description="Manages form submissions, creating, retrieving, updating, managing submission data,\
                    and tracking submission history.",
)

application_create_model = API.model(
    "ApplicationCreate",
    {
        "data": fields.Raw(),
        "formId": fields.String(),
        "submissionId": fields.String(),
        "formUrl": fields.String(),
        "webFormUrl": fields.String(),
    },
)

application_create_response_model = API.model(
    "ApplicationCreationResponse", submission_response
)

application_model = API.inherit(
    "Application",
    application_create_response_model,
    {
        "applicationName": fields.String(),
        "processKey": fields.String(),
        "processName": fields.String(),
        "processTenant": fields.String(),
    },
)

application_list_model = API.model(
    "ApplicationList",
    {
        "applications": fields.List(
            fields.Nested(application_model, description="List of Applications.")
        ),
        "totalCount": fields.Integer(),
        "limit": fields.Integer(),
        "pageNo": fields.Integer(),
    },
)

application_update_model = API.model(
    "ApplicationUpdate",
    {
        "applicationStatus": fields.String(),
        "formUrl": fields.String(),
        "data": fields.Raw(),
    },
)

application_status_list_model = API.model(
    "StatusList", {"applicationStatus": fields.List(fields.String())}
)

application_resubmit_model = API.model(
    "ApplicationResubmitModel",
    {
        "processInstanceId": fields.String(),
        "messageName": fields.String(),
        "data": fields.Raw(),
    },
)

message = API.model("Message", {"message": fields.String()})

application_count_model = API.inherit(
    "ApplicationCountModel",
    message,
    {
        "value": fields.Integer(),
    },
)


@cors_preflight("GET,POST,OPTIONS")
@API.route("", methods=["GET", "OPTIONS"])
class ApplicationsResource(Resource):
    """Resource for managing applications."""

    @staticmethod
    @auth.has_one_of_roles([VIEW_SUBMISSIONS, VIEW_TASKS, MANAGE_TASKS])
    @profiletime
    @API.doc(
        params={
            "pageNo": {
                "in": "query",
                "description": "Page number for paginated results",
                "default": "1",
            },
            "limit": {
                "in": "query",
                "description": "Limit for paginated results",
                "default": "5",
            },
            "sortBy": {
                "in": "query",
                "description": "Specify field for sorting the results.",
                "default": "id",
            },
            "sortOrder": {
                "in": "query",
                "description": "Specify sorting  order.",
                "default": "desc",
            },
            "applicationName": {
                "in": "query",
                "description": "Filter resources by application name.",
                "type": "string",
            },
            "Id": {
                "in": "query",
                "description": "Filter resources by id.",
                "type": "integer",
            },
            "modifiedFrom": {
                "in": "query",
                "description": "Filter resources by modified from.",
                "type": "string",
            },
            "modifiedTo": {
                "in": "query",
                "description": "Filter resources by modified to.",
                "type": "string",
            },
            "createdBy": {
                "in": "query",
                "description": "Filter resources by created by.",
                "type": "string",
            },
            "createdFrom": {
                "in": "query",
                "description": "Filter resources by created from.",
                "type": "string",
            },
            "createdTo": {
                "in": "query",
                "description": "Filter resources by created to.",
                "type": "string",
            },
            "applicationStatus": {
                "in": "query",
                "description": "Filter resources by application status.",
                "type": "string",
            },
            "parentFormId": {
                "in": "query",
                "description": "Filter resources by parent form id.",
                "type": "string",
            },
            "createdUserSubmissions": {
                "in": "query",
                "description": "Return user created submissions.",
                "type": "boolean",
            },
            "includeDrafts": {
                "in": "query",
                "description": "Return submissions and drafts/Specific to client permission.",
                "type": "boolean",
            },
            "onlyDrafts": {
                "in": "query",
                "description": "Return only drafts/Specific to client permission.",
                "type": "boolean",
            },
        }
    )
    @API.response(200, "OK:- Successful request.", model=application_list_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def get():  # pylint:disable=too-many-locals
        """Get applications."""
        dict_data = ApplicationListRequestSchema().load(request.args) or {}
        # Common parameters
        common_filters = {
            "page_no": dict_data.get("page_no"),
            "limit": dict_data.get("limit"),
            "order_by": dict_data.get("order_by", "id"),
            "application_id": dict_data.get("application_id"),
            "application_name": dict_data.get("application_name"),
            "application_status": dict_data.get("application_status"),
            "created_by": dict_data.get("created_by"),
            "created_from": dict_data.get("created_from_date"),
            "created_to": dict_data.get("created_to_date"),
            "modified_from": dict_data.get("modified_from_date"),
            "modified_to": dict_data.get("modified_to_date"),
            "sort_order": dict_data.get("sort_order", "desc"),
            "parent_form_id": dict_data.get("parent_form_id"),
        }

        # Flags
        include_drafts = dict_data.get("include_drafts", False)
        only_drafts = dict_data.get("only_drafts", False)
        created_user_submissions = dict_data.get("created_user_submissions", False)
        form_name, form_id = (
            ApplicationService.fetch_latest_form_name_formid_by_parent_form_id(
                common_filters["parent_form_id"]
            )
        )
        # Check if the application_id is not a valid integer, return an empty response
        application_id = dict_data.get("application_id")
        if application_id and not application_id.isdigit():
            application_schema_dump, application_count = [], 0
        elif auth.has_role([VIEW_TASKS, MANAGE_TASKS]) and not created_user_submissions:
            (
                application_schema_dump,
                application_count,
            ) = ApplicationService.get_auth_applications_and_count(
                filters=common_filters
            )
        else:
            (
                application_schema_dump,
                application_count,
            ) = ApplicationService.get_all_applications_by_user(
                filters=common_filters,
                include_drafts=include_drafts,
                only_drafts=only_drafts,
            )
        return (
            (
                {
                    "applications": application_schema_dump,
                    "totalCount": application_count,
                    "limit": common_filters["limit"],
                    "pageNo": common_filters["page_no"],
                    "formName": form_name,
                    "formId": form_id,
                    "parentFormId": common_filters["parent_form_id"],
                }
            ),
            HTTPStatus.OK,
        )


@cors_preflight("GET,PUT,DELETE,OPTIONS")
@API.route("/<int:application_id>", methods=["GET", "PUT", "DELETE", "OPTIONS"])
class ApplicationResourceById(Resource):
    """Resource for getting application by id."""

    @staticmethod
    @auth.has_one_of_roles(
        [
            CREATE_SUBMISSIONS,
            VIEW_SUBMISSIONS,
            VIEW_TASKS,
            MANAGE_TASKS,
            ANALYZE_SUBMISSIONS_VIEW,
        ]
    )
    @profiletime
    @API.response(200, "OK:- Successful request.", model=application_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def get(application_id: int):
        """Get application by id."""
        if auth.has_one_of_roles([VIEW_TASKS, MANAGE_TASKS, ANALYZE_SUBMISSIONS_VIEW]):
            (
                application_schema_dump,
                status,
            ) = ApplicationService.get_auth_by_application_id(
                application_id=application_id,
            )
            return (
                application_schema_dump,
                status,
            )
        application, status = ApplicationService.get_application_by_user(
            application_id=application_id
        )
        return application, status

    @staticmethod
    @auth.require
    @profiletime
    @API.doc(
        body=application_update_model,
        description="Provide `applicationStatus` and `formUrl` for an application update, or\
                    `data` for a draft update.",
    )
    @API.response(200, "OK:- Successful request.")
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def put(application_id: int):
        """Update either an application or a draft."""
        application_json = request.get_json()
        application_schema = ApplicationUpdateSchema()
        dict_data = application_schema.load(application_json)
        form_url = dict_data.get("form_url", None)
        if form_url:
            (
                latest_form_id,
                submission_id,
            ) = get_form_and_submission_id_from_form_url(form_url)
            dict_data["latest_form_id"] = latest_form_id
            dict_data["submission_id"] = submission_id
        response = ApplicationService.update_application(
            application_id=application_id, data=dict_data
        )
        return response, HTTPStatus.OK

    @staticmethod
    @auth.has_one_of_roles([CREATE_SUBMISSIONS])
    @profiletime
    @API.response(200, "OK:- Successful request.", model=message)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    def delete(application_id: int):
        """Delete draft application."""
        ApplicationService.delete_draft_application(application_id)
        return {"message": "Draft deleted successfully"}, HTTPStatus.OK


@cors_preflight("GET,OPTIONS")
@API.route("/formid/<string:form_id>", methods=["GET", "OPTIONS"])
class ApplicationResourceByFormId(Resource):
    """Resource for getting applications based on formid."""

    @staticmethod
    @auth.require
    @profiletime
    @API.doc(
        params={
            "pageNo": {
                "in": "query",
                "description": "Page number for paginated results",
                "default": "1",
            },
            "limit": {
                "in": "query",
                "description": "Limit for paginated results",
                "default": "5",
            },
        }
    )
    @API.response(200, "OK:- Successful request.", model=application_list_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def get(form_id: str):
        """Get applications by formId."""
        if request.args:
            dict_data = ApplicationListReqSchema().load(request.args)
            page_no = dict_data["page_no"]
            limit = dict_data["limit"]
        else:
            page_no = 0
            limit = 0

        if auth.has_role([VIEW_TASKS]):
            application_schema = ApplicationService.get_all_applications_form_id(
                form_id=form_id, page_no=page_no, limit=limit
            )
            application_count = ApplicationService.get_all_applications_form_id_count(
                form_id=form_id
            )
        else:
            application_schema = ApplicationService.get_all_applications_form_id_user(
                form_id=form_id,
                page_no=page_no,
                limit=limit,
            )
            application_count = (
                ApplicationService.get_all_applications_form_id_user_count(
                    form_id=form_id
                )
            )

        if page_no == 0:
            return (
                (
                    {
                        "applications": application_schema,
                        "totalCount": application_count,
                    }
                ),
                HTTPStatus.OK,
            )
        return (
            (
                {
                    "applications": application_schema,
                    "totalCount": application_count,
                    "limit": limit,
                    "pageNo": page_no,
                }
            ),
            HTTPStatus.OK,
        )


@cors_preflight("GET,OPTIONS")
@API.route("/formid/<string:form_id>/count", methods=["GET", "OPTIONS"])
class ApplicationResourceCountByFormId(Resource):
    """Resource for getting applications count on formid."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.doc(
        responses={
            200: "OK:- Successful request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
        },
        model=application_count_model,
    )
    def get(form_id: str):
        """Get application count by formId."""
        application_count = ApplicationService.get_all_applications_form_id_count(
            form_id=form_id
        )
        return (
            (
                {
                    "message": f"Total Applications found are: {application_count}",
                    "value": application_count,
                }
            ),
            HTTPStatus.OK,
        )


@cors_preflight("POST,OPTIONS")
@API.route("/create", methods=["POST", "OPTIONS"])
class ApplicationResourcesByIds(Resource):
    """Resource for application creation."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_SUBMISSIONS])
    @profiletime
    @API.doc(body=application_create_model)
    @API.response(
        201, "CREATED:- Successful request.", model=application_create_response_model
    )
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def post():
        """Post a new application using the request body.

        e.g,
        ```
        {
           "formId":"632208d9fbcab29c2ab1a097",
           "submissionId":"63407583fbcab29c2ab1bed4",
           "formUrl":"https://formsflow-forms/form/632208d9fbcab29c2ab1a097/submission/63407583fbcab29c2ab1bed4",
           "webFormUrl":"https://formsflow-web/form/632208d9fbcab29c2ab1a097/submission/63407583fbcab29c2ab1bed4"
        }
        ```
        """
        application_json = request.get_json()

        application_schema = ApplicationSchema()
        dict_data = application_schema.load(application_json)
        application, status = ApplicationService.create_application(
            data=dict_data, token=request.headers["Authorization"]
        )
        response = application_schema.dump(application)
        return response, status


@cors_preflight("GET,OPTIONS")
@API.route("/status/list", methods=["GET", "OPTIONS"])
class ApplicationResourceByApplicationStatus(Resource):
    """Get application status list."""

    @staticmethod
    @auth.has_one_of_roles([VIEW_SUBMISSIONS])
    @profiletime
    @API.response(200, "OK:- Successful request.", model=application_status_list_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def get():
        """Retrieve the list of application statuses."""
        return (
            ApplicationService.get_all_application_status(),
            HTTPStatus.OK,
        )


@cors_preflight("POST,OPTIONS")
@API.route("/<int:application_id>/resubmit", methods=["POST", "OPTIONS"])
class ApplicationResubmitById(Resource):
    """Resource for resubmit application."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_SUBMISSIONS])
    @profiletime
    @API.doc(body=application_resubmit_model)
    @API.response(200, "OK:- Successful request.")
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(403, "FORBIDDEN:- Permission denied")
    def post(application_id: int):
        """Resubmit application."""
        resubmit_json = request.get_json()
        ApplicationService.resubmit_application(
            application_id, resubmit_json, token=request.headers["Authorization"]
        )
        return "Message event updated successfully.", HTTPStatus.OK


@cors_preflight("PUT, OPTIONS")
@API.route("/<int:application_id>/submit", methods=["PUT", "OPTIONS"])
class DraftSubmissionResource(Resource):
    """Converts the given draft entry to actual submission."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_SUBMISSIONS])
    @profiletime
    @API.doc(body=application_create_model)
    @API.response(
        200, "OK:- Successful request.", model=application_create_response_model
    )
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def put(application_id: str):
        """Updates the draft to actual submission."""
        payload = request.get_json()
        token = request.headers["Authorization"]
        application_schema = ApplicationSubmissionSchema()
        dict_data = application_schema.load(payload)
        dict_data["application_status"] = NEW_APPLICATION_STATUS
        response = DraftService.make_submission_from_draft(
            dict_data, application_id, token
        )
        res = ApplicationSchema().dump(response)
        return res, HTTPStatus.OK
