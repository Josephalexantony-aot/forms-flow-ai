"""API endpoints for managing form resource."""

import json
from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields
from formsflow_api_utils.exceptions import BusinessException
from formsflow_api_utils.utils import (
    CREATE_DESIGNS,
    CREATE_FILTERS,
    CREATE_SUBMISSIONS,
    MANAGE_ALL_FILTERS,
    VIEW_DESIGNS,
    VIEW_FILTERS,
    VIEW_SUBMISSIONS,
    auth,
    authorization_list_model,
    cors_preflight,
    profiletime,
)

from formsflow_api.schemas import (
    FormProcessMapperListRequestSchema,
    FormProcessMapperSchema,
)
from formsflow_api.services import (
    ApplicationService,
    AuthorizationService,
    FilterService,
    FormHistoryService,
    FormProcessMapperService,
)

API = Namespace(
    "Form",
    description="Manages form lifecycle, including creation, update, listing, \
                deletion, retrieval, validation, publish, unpublish, and history.",
)

form_list_model = API.model(
    "FormList",
    {
        "forms": fields.List(
            fields.Nested(
                API.model(
                    "Form",
                    {
                        "formId": fields.String(),
                        "formName": fields.String(),
                        "id": fields.String(),
                        "processKey": fields.String(),
                        "formType": fields.String(),
                        "created": fields.String(),
                        "modified": fields.String(),
                        "anonymous": fields.Boolean(),
                        "status": fields.String(),
                        "description": fields.String(),
                    },
                )
            )
        ),
        "totalCount": fields.Integer(),
        "pageNo": fields.Integer(),
        "limit": fields.Integer(),
    },
)

mapper_create_model = API.model(
    "CreateMapper",
    {
        "anonymous": fields.Boolean(),
        "formId": fields.String(),
        "formName": fields.String(),
        "formRevisionNumber": fields.String(),
        "formType": fields.String(),
        "parentFormId": fields.String(),
    },
)
task_variables_model = API.model(
    "TaskVariables",
    {
        "key": fields.String(),
        "label": fields.String(),
        "type": fields.String(),
    },
)
mapper_create_response_model = API.model(
    "MapperCreateResponse",
    {
        "anonymous": fields.Boolean(),
        "comments": fields.String(),
        "created": fields.String(),
        "createdBy": fields.String(),
        "formId": fields.String(),
        "formName": fields.String(),
        "id": fields.String(),
        "modified": fields.String(),
        "modifiedBy": fields.String(),
        "processKey": fields.String(),
        "processName": fields.String(),
        "processTenant": fields.String(),
        "status": fields.String(),
        "taskVariables": fields.List(fields.Nested(task_variables_model)),
        "version": fields.String(),
        "promptNewVersion": fields.Boolean(default=False),
        "deleted": fields.Boolean(default=False),
        "description": fields.String(),
        "isMigrated": fields.Boolean(),
        "majorVersion": fields.Integer(),
        "minorVersion": fields.Integer(),
    },
)

mapper_update_model = API.model(
    "MapperUpdate",
    {
        "formId": fields.String(),
        "formName": fields.String(),
        "description": fields.String(),
        "status": fields.String(),
        "taskVariable": fields.String(),
        "anonymous": fields.Boolean(),
        "processKey": fields.String(),
        "processName": fields.String(),
        "id": fields.String(),
        "formType": fields.String(),
        "majorVersion": fields.Integer(),
        "minorVersion": fields.Integer(),
        "parentFormId": fields.String(),
        "taskVariables": fields.List(fields.Nested(task_variables_model)),
    },
)

mapper_update_request_model = API.model(
    "MapperAuthorizationUpdateModel",
    {
        "mapper": fields.Nested(mapper_update_model),
        "authorizations": fields.Nested(authorization_list_model),
    },
)
mapper_update_response_model = API.model(
    "MapperUpdateResponseModel",
    {
        "mapper": fields.Nested(mapper_create_response_model),
        "authorizations": fields.Nested(authorization_list_model),
    },
)
application_count_model = API.model(
    "ApplicationCount", {"message": fields.String(), "value": fields.Integer()}
)

task_variable_response_model = API.model(
    "TaskVariableResponse",
    {
        "id": fields.String(),
        "formType": fields.String(),
        "processName": fields.String(),
        "processKey": fields.String(),
        "processTenant": fields.String(),
        "taskVariables": fields.String(),
    },
)

access_model = API.model(
    "SubmissionAccess",
    {"type": fields.String(), "roles": fields.List(fields.String())},
)
form_create_model = API.model(
    "FormCreate",
    {
        "title": fields.String(),
        "tags": fields.List(fields.String()),
        "submissionAccess": fields.List(fields.Nested(access_model)),
        "path": fields.String(),
        "name": fields.String(),
        "display": fields.String(),
        "components": fields.List(fields.Raw()),
        "access": fields.List(fields.Nested(access_model)),
    },
)
form_create_request_model = API.inherit(
    "FormCreateRequest",
    form_create_model,
    {
        "newVersion": fields.Boolean(),
    },
)

form_create_response_model = API.inherit(
    "FormCreateResponse",
    form_create_model,
    {
        "_id": fields.String(),
        "isBundle": fields.Boolean(default=False),
        "machineName": fields.String(),
        "owner": fields.String(),
        "created": fields.String(description="Date string"),
        "modified": fields.String(description="Date string"),
    },
)
form_update_model = API.inherit(
    "FormUpdate",
    form_create_response_model,
    {
        "parentFormId": fields.String(),
    },
)

form_update_request_model = API.inherit(
    "FormUpdateRequest",
    form_update_model,
    {
        "componentChanged": fields.Boolean(),
    },
)

form_history_change_log_model = API.model(
    "formHistoryChangeLog",
    {"clone_id": fields.String(), "new_version": fields.Boolean()},
)
form_history_response_model = API.inherit(
    "FormHistoryResponse",
    {
        "formHistory": fields.List(
            fields.Nested(
                API.model(
                    "FormHistory",
                    {
                        "id": fields.String(),
                        "formId": fields.String(),
                        "createdBy": fields.String(),
                        "created": fields.String(),
                        "changeLog": fields.Nested(form_history_change_log_model),
                        "majorVersion": fields.Integer(),
                        "minorVersion": fields.Integer(),
                        "isMajor": fields.Boolean(),
                        "version": fields.String(),
                    },
                )
            )
        ),
        "totalCount": fields.Integer(),
    },
)
forms_list_model = API.model(
    "FormsListModel",
    {
        "formTitle": fields.String(),
        "formDescription": fields.String(),
        "anonymous": fields.Boolean(),
        "type": fields.String(),
        "content": fields.Raw(),
    },
)
workflows_list_model = API.model(
    "WorkflowsList",
    {
        "processKey": fields.String(),
        "processName": fields.String(),
        "processType": fields.String(),
        "type": fields.String(),
        "content": fields.String(),
    },
)
dmns_list_model = API.model(
    "DMNList",
    {"key": fields.String(), "type": fields.String(), "content": fields.String()},
)
resource_details_model = API.model("resource_details", {"name": fields.String()})

authorization_model = API.model(
    "Authorization",
    {
        "resourceId": fields.String(),
        "resourceDetails": fields.Nested(resource_details_model),
        "roles": fields.List(fields.String),
        "userName": fields.String(),
    },
)

export_response_model = API.model(
    "ExportResponse",
    {
        "forms": fields.List(fields.Nested(forms_list_model)),
        "workflows": fields.List(fields.Nested(workflows_list_model)),
        "rules": fields.List(fields.Nested(dmns_list_model)),
        "authorizations": fields.List(fields.Nested(authorization_list_model)),
    },
)


@cors_preflight("GET,OPTIONS")
@API.route("", methods=["GET", "OPTIONS"])
class FormResourceList(Resource):
    """Resource for getting forms."""

    @staticmethod
    @auth.has_one_of_roles(
        [
            CREATE_DESIGNS,
            VIEW_DESIGNS,
            CREATE_SUBMISSIONS,
            VIEW_SUBMISSIONS,
            CREATE_FILTERS,
            VIEW_FILTERS,
            MANAGE_ALL_FILTERS,
        ]
    )
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
                "description": "Name of column to sort by.",
                "default": "id",
            },
            "sortOrder": {
                "in": "query",
                "description": "Specify sorting order.",
                "default": "desc",
            },
            "search": {
                "in": "query",
                "description": "Retrieve form list based on form name or description.",
                "default": "",
            },
            "showForOnlyCreateSubmissionUsers": {
                "in": "query",
                "description": "Retrieve only active forms that the current user is authorized \
                                to create submissions when set to True",
                "default": False,
            },
            "isActive": {
                "in": "query",
                "description": "Filter authorized active/inactive forms.",
                "default": None,
            },
            "activeForms": {
                "in": "query",
                "description": "Retrieve all active forms.",
                "default": False,
            },
            "includeSubmissionsCount": {
                "in": "query",
                "description": "Retrieve the submission count for the form, \
                                applicable only to users with create submission permission.",
                "default": False,
            },
        }
    )
    @API.response(200, "OK:- Successful request.", model=form_list_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    def get():  # pylint: disable=too-many-locals
        """List forms."""
        dict_data = FormProcessMapperListRequestSchema().load(request.args) or {}
        search: str = dict_data.get("search", "")
        page_no: int = dict_data.get("page_no")
        limit: int = dict_data.get("limit")
        sort_by: str = dict_data.get("sort_by", "")
        sort_order: str = dict_data.get("sort_order", "")
        form_type: str = dict_data.get("form_type", None)
        is_active = dict_data.get("is_active", None)
        active_forms = dict_data.get("active_forms", None)
        # when ignore_designer true, exclude designer priorities like
        # listing both active and inactive forms or listing forms created by the designer.
        ignore_designer = dict_data.get("ignore_designer", False)
        is_designer = (
            auth.has_any_role([CREATE_DESIGNS, VIEW_DESIGNS]) and not ignore_designer
        )
        sort_by = sort_by.split(",")
        sort_order = sort_order.split(",")
        include_submissions_count = dict_data.get("include_submissions_count", False)
        if form_type:
            form_type = form_type.split(",")
        if search:
            search = search.replace("%", r"\%").replace("_", r"\_")
            search = [key for key in search.split(" ") if key.strip()]

        (
            form_process_mapper_schema,
            form_process_mapper_count,
        ) = FormProcessMapperService.get_all_forms(
            page_number=page_no,
            limit=limit,
            search=search if search else [],
            sort_by=sort_by,
            sort_order=sort_order,
            form_type=form_type,
            is_active=is_active,
            is_designer=is_designer,
            active_forms=active_forms,
            include_submissions_count=include_submissions_count,
        )
        return (
            (
                {
                    "forms": form_process_mapper_schema,
                    "totalCount": form_process_mapper_count,
                    "pageNo": page_no,
                    "limit": limit,
                }
            ),
            HTTPStatus.OK,
        )


@cors_preflight("GET,PUT,DELETE,OPTIONS")
@API.route("/<int:mapper_id>", methods=["GET", "PUT", "DELETE", "OPTIONS"])
class FormResourceById(Resource):
    """Resource for managing forms by mapper_id."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.response(200, "OK:- Successful request.", model=mapper_create_response_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def get(mapper_id: int):
        """Get form by mapper_id."""
        return (
            FormProcessMapperService.get_mapper(form_process_mapper_id=mapper_id),
            HTTPStatus.OK,
        )

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.response(200, "OK:- Successful request.")
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def delete(mapper_id: int):
        """Delete form by mapper_id."""
        FormProcessMapperService.mark_inactive_and_delete(
            form_process_mapper_id=mapper_id
        )
        return "Deleted", HTTPStatus.OK

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @API.doc(body=mapper_update_request_model)
    @API.response(
        200, "CREATED:- Successful request.", model=mapper_update_response_model
    )
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def put(mapper_id: int):
        """Update form details and authorization by mapper_id."""
        data = request.get_json()

        # Extract mapper and authorization data from the request
        mapper_data = data.get("mapper")
        authorization_data = data.get("authorizations")

        # Get the parentFormId as resource id from mapper data if authorization data is provided
        resource_id = mapper_data.get("parentFormId") if authorization_data else None
        task_variable = mapper_data.get("taskVariables", [])

        # If task variables are present, update filter variables and serialize them
        if "taskVariables" in mapper_data:
            FilterService.update_filter_variables(
                task_variable, mapper_data.get("formId")
            )
            mapper_data["taskVariables"] = json.dumps(task_variable)

        # Load the mapper data into the schema
        mapper_schema = FormProcessMapperSchema()
        dict_data = mapper_schema.load(mapper_data)

        # Update the mapper with the provided data
        mapper = FormProcessMapperService.update_mapper(
            form_process_mapper_id=mapper_id, data=dict_data
        )

        # If authorization data and resource ID are provided, update resource authorization
        if authorization_data and resource_id:
            AuthorizationService.create_or_update_resource_authorization(
                authorization_data, bool(auth.has_role([CREATE_DESIGNS]))
            )

        # Dump the updated mapper data into the response schema
        mapper_response = mapper_schema.dump(mapper)

        if task_variables := mapper_response.get("taskVariables"):
            mapper_response["taskVariables"] = json.loads(task_variables)

        # Create form logs without cloning
        FormHistoryService.create_form_logs_without_clone(data=mapper_data)

        # Prepare the response
        response = {}
        major_version, minor_version = FormProcessMapperService.get_form_version(mapper)
        mapper_response["majorVersion"] = major_version
        mapper_response["minorVersion"] = minor_version
        response["mapper"] = mapper_response
        if resource_id:
            response["authorizations"] = AuthorizationService().get_auth_list_by_id(
                resource_id
            )

        # Return the response with HTTP status OK
        return (
            response,
            HTTPStatus.OK,
        )


@cors_preflight("GET,OPTIONS")
@API.route("/formid/<string:form_id>", methods=["GET", "OPTIONS"])
class FormResourceByFormId(Resource):
    """Resource for managing forms by corresponding form_id."""

    @staticmethod
    @auth.has_one_of_roles(
        [
            CREATE_DESIGNS,
            VIEW_DESIGNS,
            CREATE_SUBMISSIONS,
            CREATE_FILTERS,
            VIEW_FILTERS,
            MANAGE_ALL_FILTERS,
        ]
    )
    @profiletime
    @API.response(
        200, "CREATED:- Successful request.", model=mapper_create_response_model
    )
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def get(form_id: str):
        """Retrieve form details using form_id.

        : form_id:- Get details of the form corresponding to a particular formId
        """
        response = FormProcessMapperService.get_mapper_by_formid(form_id=form_id)
        task_variable = response.get("taskVariables")
        response["taskVariables"] = json.loads(task_variable) if task_variable else None
        return (
            response,
            HTTPStatus.OK,
        )


@cors_preflight("GET,OPTIONS")
@API.route("/<int:mapper_id>/application/count", methods=["GET", "OPTIONS"])
class FormResourceApplicationCount(Resource):
    """Resource for getting applications count according to a mapper id."""

    @staticmethod
    @auth.has_one_of_roles(
        [
            CREATE_DESIGNS,
            VIEW_DESIGNS,
            CREATE_SUBMISSIONS,
        ]
    )
    @profiletime
    @API.response(200, "OK:- Successful request.", model=application_count_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def get(mapper_id: int):
        """Retrieves the total application count for the given mapper id."""
        FormProcessMapperService.check_tenant_authorization(mapper_id=mapper_id)
        (
            response,
            status,
        ) = ApplicationService.get_total_application_corresponding_to_mapper_id(
            mapper_id
        )
        return response, status


@cors_preflight("GET,OPTIONS")
@API.route("/applicationid/<int:application_id>", methods=["GET", "OPTIONS"])
class FormResourceTaskVariablesbyApplicationId(Resource):
    """Resource to get task filter variables of a form based on application id."""

    @staticmethod
    @auth.require
    @profiletime
    @API.response(200, "OK:- Successful request.", model=task_variable_response_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def get(application_id: int):
        """Retrieves task variables of a form based on application id."""
        return (
            ApplicationService.get_application_form_mapper_by_id(application_id),
            HTTPStatus.OK,
        )


@cors_preflight("POST,OPTIONS")
@API.route("/form-design", methods=["POST", "OPTIONS"])
class FormioFormResource(Resource):
    """Resource for formio form creation."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.doc(body=form_create_request_model)
    @API.response(
        201, "CREATED:- Successful request.", model=form_create_response_model
    )
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def post():
        """Create a form with an associated flow, authorization rules, and history tracking."""
        try:
            # form data
            data = request.get_json()
            response = FormProcessMapperService.create_form(
                data, bool(auth.has_role([CREATE_DESIGNS]))
            )
            return response, HTTPStatus.CREATED

        except BusinessException as err:
            message = (
                err.details[0]["message"]
                if hasattr(err, "details") and err.details
                else err.message
            )
            return message, err.status_code


@cors_preflight("PUT,OPTIONS")
@API.route("/form-design/<string:form_id>", methods=["PUT", "OPTIONS"])
class FormioFormUpdateResource(Resource):
    """Resource for formio form Update."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.doc(body=form_update_request_model)
    @API.response(200, "CREATED:- Successful request.", model=form_update_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def put(form_id: str):
        """Update form design and form history."""
        try:
            data = request.get_json()
            response = FormProcessMapperService.form_design_update(data, form_id)
            return response, HTTPStatus.OK
        except BusinessException as err:
            message = (
                err.details[0]["message"]
                if hasattr(err, "details") and err.details
                else err.message
            )
            return message, err.status_code


@cors_preflight("GET,OPTIONS")
@API.route("/form-history/<string:form_id>", methods=["GET", "OPTIONS"])
class FormHistoryResource(Resource):
    """Resource for form history."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS, VIEW_DESIGNS])
    @profiletime
    @API.response(200, "OK:- Successful request.", model=form_history_response_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def get(form_id: str):
        """Retrieve form history by form_id."""
        FormProcessMapperService.check_tenant_authorization_by_formid(form_id=form_id)
        form_history, count = FormHistoryService.get_all_history(form_id, request.args)
        return (
            (
                {
                    "formHistory": form_history,
                    "totalCount": count,
                }
            ),
            HTTPStatus.OK,
        )


@cors_preflight("GET,OPTIONS")
@API.route("/<int:mapper_id>/export", methods=["GET", "OPTIONS"])
class ExportById(Resource):
    """Resource to support export by mapper_id."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS, VIEW_DESIGNS])
    @profiletime
    @API.response(200, "OK:- Successful request.", model=export_response_model)
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def get(mapper_id: int):
        """Export form and workflow by mapper_id."""
        form_service = FormProcessMapperService()
        return (
            form_service.export(mapper_id),
            HTTPStatus.OK,
        )


@cors_preflight("GET,OPTIONS")
@API.route("/validate", methods=["GET", "OPTIONS"])
class ValidateFormName(Resource):
    """Resource for validating a form name."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.doc(
        params={
            "title": {
                "in": "query",
                "description": "Form title to be validated",
            },
            "name": {
                "in": "query",
                "description": "Form name to be validated",
            },
            "path": {
                "in": "query",
                "description": "Form path to be validated",
            },
            "parentFormId": {
                "in": "query",
                "description": "Used for validating title against an existing form",
            },
            "id": {
                "in": "query",
                "description": "Form ID: Used for validating the path or name against an existing form",
            },
        }
    )
    @API.response(200, "OK:- Successful request.")
    @API.response(400, "BAD_REQUEST:- Invalid request.")
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(403, "FORBIDDEN:- Authorization will not help.")
    def get():
        """Validates the form name, path and title.

        Retrieves query parameters, validates the form name, path, and title,
        and returns a response indicating validity..
        """
        response = FormProcessMapperService.validate_form_name_path_title(request)
        return response, HTTPStatus.OK


@cors_preflight("POST,OPTIONS")
@API.route("/<int:mapper_id>/publish", methods=["POST", "OPTIONS"])
class PublishResource(Resource):
    """Resource to support publish."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.response(200, "OK:- Successful request.")
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def post(mapper_id: int):
        """Publish form and workflow by mapper_id."""
        form_service = FormProcessMapperService()
        return (
            form_service.publish(mapper_id),
            HTTPStatus.OK,
        )


@cors_preflight("POST,OPTIONS")
@API.route("/<int:mapper_id>/unpublish", methods=["POST", "OPTIONS"])
class UnpublishResource(Resource):
    """Resource to support unpublish."""

    @staticmethod
    @auth.has_one_of_roles([CREATE_DESIGNS])
    @profiletime
    @API.response(200, "OK:- Successful request.")
    @API.response(
        400,
        "BAD_REQUEST:- Invalid request.",
    )
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(
        403,
        "FORBIDDEN:- Authorization will not help.",
    )
    def post(mapper_id: int):
        """Unpublish form and workflow by mapper_id."""
        form_service = FormProcessMapperService()
        return (
            form_service.unpublish(mapper_id),
            HTTPStatus.OK,
        )


@cors_preflight("GET,OPTIONS")
@API.route("/form-data/<string:form_id>", methods=["GET", "OPTIONS"])
@API.doc(
    params={
        "form_id": "Unique identifier of the form",
        "authType": "Authorization type (form, application, designer)",
    }
)
class FormDataResource(Resource):
    """Resource to support form data."""

    @staticmethod
    @auth.has_one_of_roles(
        [CREATE_DESIGNS, VIEW_DESIGNS, CREATE_SUBMISSIONS, VIEW_SUBMISSIONS]
    )
    @profiletime
    @API.response(200, "OK:- Successful request.")
    @API.response(400, "BAD_REQUEST:- Invalid request.")
    @API.response(
        401,
        "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
    )
    @API.response(403, "FORBIDDEN:- Authorization will not help.")
    def get(form_id: str):
        """Get form data by form_id."""
        form_service = FormProcessMapperService()
        auth_type = request.args.get("authType")
        is_designer = auth.has_role([CREATE_DESIGNS])
        return (
            form_service.get_form_data(form_id, auth_type, is_designer),
            HTTPStatus.OK,
        )
