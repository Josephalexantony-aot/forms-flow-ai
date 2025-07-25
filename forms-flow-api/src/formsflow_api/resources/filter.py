"""API endpoints for filter resource."""

from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, fields
from formsflow_api_utils.utils import (
    CREATE_FILTERS,
    MANAGE_ALL_FILTERS,
    VIEW_FILTERS,
    auth,
    cors_preflight,
    profiletime,
)

from formsflow_api.schemas import FilterSchema
from formsflow_api.services import FilterPreferenceService, FilterService

filter_schema = FilterSchema()

API = Namespace(
    "Filter",
    description="Manages filters for review tasks, including creation, retrieval, updating, and deletion.",
)

criteria = API.model(
    "Criteria",
    {
        "candidateGroupsExpression": fields.String(
            description="Filter task specific to group"
        ),
        "includeAssignedTasks": fields.Boolean(description="Include assigned task"),
    },
)

variable = API.model(
    "Variables",
    {
        "name": fields.String(description="Variable name"),
        "label": fields.String(description="Display name"),
        "key": fields.String(description="Variable key"),
        "type": fields.String(description="Variable type"),
        "isChecked": fields.Boolean(description="Is variable checked"),
        "sortOrder": fields.Integer(description="Sort order of the variable"),
        "isFormVariable": fields.Boolean(description="Is this a form variable"),
    },
)
properties = API.model(
    "Properties",
    {"showUndefinedVariable": fields.Boolean(description="Show undefined variables")},
)

filter_base_model = API.model(
    "FilterBaseModel",
    {
        "name": fields.String(description="Name of the filter"),
        "criteria": fields.Nested(criteria, description="Filter criteria"),
        "variables": fields.List(
            fields.Nested(variable, description=" Variables shown in the tasks list"),
        ),
        "properties": fields.Nested(properties, description="Properties of filter"),
        "roles": fields.List(
            fields.String(), description="Authorized Roles to the filter"
        ),
        "users": fields.List(
            fields.String(), description="Authorized Users to the filter"
        ),
        "parentFilterId": fields.Integer(description="Parent filter id"),
        "filterType": fields.String(description="Filter type"),
    },
)
filter_request = API.inherit(
    "FilterRequest",
    filter_base_model,
    {
        "isMyTasksEnabled": fields.Boolean(),
        "isTasksForCurrentUserGroupsEnabled": fields.Boolean(),
    },
)
filter_response = API.inherit(
    "FilterResponse",
    filter_base_model,
    {
        "status": fields.String(description="Status of the filter"),
        "tenant": fields.String(description="Authorized Tenant to the filter"),
        "id": fields.Integer(description="Unique id of the filter"),
        "created": fields.DateTime(description="Created time"),
        "modified": fields.DateTime(description="Modified time"),
        "createdBy": fields.String(),
        "modifiedBy": fields.String(),
        "hide": fields.Boolean(
            description="Status of this filter from filter preference data"
        ),
        "sortOrder": fields.Integer(
            description="Sort order of the filter from filter preference data"
        ),
    },
)

filter_response_with_attribute_filters = API.inherit(
    "FilterResponseWithAttributeFilter",
    filter_response,
    {
        "attributeFilters": fields.List(fields.Nested(filter_response)),
    },
)

filter_response_with_default_filter = API.model(
    "FilterResponseWithDefaultFilter",
    {
        "filters": fields.List(fields.Nested(filter_response)),
        "defaultFilter": fields.String(description="Default filter"),
    },
)

filter_preference_model = API.model(
    "FilterPreferenceItem",
    {
        "filterId": fields.Integer(description="ID of the filter"),
        "sortOrder": fields.Integer(description="Sort order for the filter"),
        "hide": fields.Boolean(description="Whether the filter is hidden"),
    },
)


filter_preference_response_model = API.inherit(
    "BaseFilterPreferenceResponseModel",
    filter_preference_model,
    {
        "id": fields.Integer(description="Unique identifier for the preference"),
        "tenant": fields.String(description="Tenant identifier"),
        "userId": fields.String(description="User identifier"),
    },
)


@cors_preflight("GET, POST, OPTIONS")
@API.route("", methods=["GET", "POST", "OPTIONS"])
class FilterResource(Resource):
    """Resource to create and list filter."""

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, VIEW_FILTERS])
    @profiletime
    @API.doc(
        responses={
            200: "OK:- Successful request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
            403: "FORBIDDEN:- Permission denied",
        },
        model=[filter_response],
    )
    def get():
        """
        Get all filters.

        List all active filters for requests with ```view filter permission```.
        """
        response, status = FilterService.get_all_filters(), HTTPStatus.OK
        return response, status

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, CREATE_FILTERS])
    @profiletime
    @API.doc(
        responses={
            201: ("CREATED:- Successful request.", filter_response),
            400: "BAD_REQUEST:- Invalid request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
            403: "FORBIDDEN:- Permission denied",
        }
    )
    @API.expect(filter_request)
    def post():
        """
        Create filter.

        Post a new filter using request body for requests with ```create filter permission```.
        e.g payload,
        ```
        {
            "name": "Test Task",
            "variables":[
                    {
                    "name": "name",
                    "label": "userName"
                    }
                ],
            "criteria": {
                "candidateGroup":"/formsflow/formsflow-reviewer",
                "includeAssignedTasks":true
            },
            "properties": {
                "showUndefinedVariable":false
            },
            "users": [],
            "roles": ["/formsflow/formsflow-reviewer"],
            "isTasksForCurrentUserGroupsEnabled":true,
            "isMyTasksEnabled":true,
            "parentFilterId": null,
            "filterType": "TASK"
        }
        ```
        """
        filter_data = filter_schema.load(request.get_json())
        response, status = (
            FilterService.create_filter(filter_data),
            HTTPStatus.CREATED,
        )
        return response, status


@cors_preflight("GET, OPTIONS")
@API.route("/user", methods=["GET", "OPTIONS"])
class UsersFilterList(Resource):
    """Resource to list filters specific to current user."""

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, VIEW_FILTERS])
    @profiletime
    @API.doc(
        responses={
            200: "OK:- Successful request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
            403: "FORBIDDEN:- Permission denied",
        },
        model=filter_response_with_default_filter,
    )
    def get():
        """
        List filters of current user.

        Get all active filters of current reviewer user for requests with ```view filter permission```.
        """
        response, status = FilterService.get_user_filters(), HTTPStatus.OK
        return response, status


@cors_preflight("PUT, OPTIONS,DELETE,GET")
@API.route("/<int:filter_id>", methods=["GET", "PUT", "DELETE", "OPTIONS"])
@API.doc(params={"filter_id": "Filter details corresponding to filter_id"})
class FilterResourceById(Resource):
    """Resource for managing filter by id."""

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, VIEW_FILTERS])
    @profiletime
    @API.doc(
        responses={
            200: "OK:- Successful request.",
            400: "BAD_REQUEST:- Invalid request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
            403: "FORBIDDEN:- Permission denied",
        },
        model=filter_response_with_attribute_filters,
    )
    def get(filter_id: int):
        """
        Get filter by id.

        Get filter details corresponding to a filter id for requests with ```manage all filters``` permission.
        """
        filter_result = FilterService.get_filter_by_id(filter_id)
        response, status = filter_result, HTTPStatus.OK

        return response, status

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, CREATE_FILTERS])
    @profiletime
    @API.doc(
        responses={
            200: "OK:- Successful request.",
            400: "BAD_REQUEST:- Invalid request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
            403: "FORBIDDEN:- Permission denied",
        },
        model=filter_response,
    )
    @API.expect(filter_request)
    def put(filter_id: int):
        """
        Update filter by id.

        Update filter details corresponding to a filter id for requests with ```create filter``` permission.
        """
        filter_data = filter_schema.load(request.get_json())
        filter_result = FilterService.update_filter(filter_id, filter_data)
        response, status = (
            filter_schema.dump(filter_result),
            HTTPStatus.OK,
        )
        return response, status

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, CREATE_FILTERS])
    @profiletime
    @API.doc(
        responses={
            200: "OK:- Successful request.",
            400: "BAD_REQUEST:- Invalid request.",
            401: "UNAUTHORIZED:- Authorization header not provided or an invalid token passed.",
            403: "FORBIDDEN:- Permission denied",
        }
    )
    def delete(filter_id: int):
        """
        Delete filter by id.

        Delete filter corresponding to a filter id for requests with ```create filter``` permission.
        """
        FilterService.mark_inactive(filter_id=filter_id)
        response, status = "Deleted", HTTPStatus.OK

        return response, status


@cors_preflight("POST,OPTIONS")
@API.route("/filter-preference", methods=["POST", "OPTIONS"])
class FilterPreferenceResource(Resource):
    """Resource for managing filter preferences."""

    @staticmethod
    @auth.has_one_of_roles([MANAGE_ALL_FILTERS, VIEW_FILTERS])
    @profiletime
    @API.doc(
        params={
            "filterType": "Filter type to set preferences for",
            "parentFilterId": "Parent filter ID of the attribute filter",
        },
        body=[filter_preference_model],
    )
    @API.response(
        201, "CREATED:- Successful request.", model=[filter_preference_response_model]
    )
    @API.response(400, "BAD_REQUEST:- Invalid request.")
    @API.response(
        401, "UNAUTHORIZED:- Authorization header not provided or invalid token."
    )
    def post():
        """Create a new filter preference.

        Creates a new user preference for filter ordering and visibility.

        Request Body:
            filterId (str): The ID of the filter to set preferences for
            sortOrder (int): The order in which the filter should appear (1 being first)
            hide (bool): Whether to hide the filter from view

        Query Parameters:
            filterType (str): The type of filter for which preferences are being set
            parentFilterId (int): The ID of the parent filter for attribute filters

        Returns:
            List: [dict] containing:
                - Filter preference data including id, tenant and userId
                - HTTP 201 status code

        Raises:
            400: If request body is invalid
            401: If user is not authenticated
        """
        data = request.get_json()
        filter_type = request.args.get("filterType", None)
        parent_filter_id = request.args.get("parentFilterId", None)
        return (
            FilterPreferenceService.create_or_update_filter_preference(
                data, filter_type, parent_filter_id
            ),
            HTTPStatus.CREATED,
        )
