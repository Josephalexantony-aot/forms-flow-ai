"""Common utils.

CORS pre-flight decorator. A simple decorator to add the options
method to a Request Class.
camel_to_snake - Converts camel case to snake case.
validate_sort_order_and_order_by - Utility function to validate
if sort order and sort order by is correct.
translate - Translate the response to provided language
"""
import re
from typing import Tuple

from .constants import (
    ALLOW_ALL_ORIGINS,
)
from .enums import (
    ApplicationSortingParameters,
    DraftSortingParameters,
    FormioRoles,
    ProcessSortingParameters,
)
from .translations.translations import translations
from .permisions import (
    CREATE_DESIGNS,
VIEW_DESIGNS,
MANAGE_TASKS,
VIEW_TASKS,
CREATE_SUBMISSIONS,
VIEW_SUBMISSIONS,
ANALYZE_SUBMISSIONS_VIEW,
)
from sqlalchemy.sql.expression import text

def cors_preflight(methods: str = "GET"):
    """Render an option method on the class."""

    def wrapper(f):  # pylint: disable=invalid-name
        def options(self, *args, **kwargs):  # pylint: disable=unused-argument
            return (
                {"Allow": "GET"},
                200,
                {
                    "Access-Control-Allow-Origin": ALLOW_ALL_ORIGINS,
                    "Access-Control-Allow-Methods": methods,
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                },
            )

        setattr(f, "options", options)
        return f

    return wrapper


def camel_to_snake(name: str) -> str:
    """Convert camel case to snake case."""
    s_1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s_1).lower()


def validate_sort_order_and_order_by(order_by: str, sort_order: str) -> bool:
    """Validate sort order and order by."""
    if order_by not in [
        ApplicationSortingParameters.Id,
        ApplicationSortingParameters.Name,
        ApplicationSortingParameters.Status,
        ApplicationSortingParameters.Modified,
        ApplicationSortingParameters.FormStatus,
        ApplicationSortingParameters.FormName,
        ApplicationSortingParameters.visibility,
        ApplicationSortingParameters.type,
        DraftSortingParameters.Name,
        ProcessSortingParameters.Name,
        ProcessSortingParameters.Created,
        ProcessSortingParameters.Modified,
        ProcessSortingParameters.ProcessKey,
    ]:
        order_by = None
    else:
        if order_by in [ApplicationSortingParameters.Name, DraftSortingParameters.Name]:
            order_by = ApplicationSortingParameters.FormName
        if order_by == ApplicationSortingParameters.visibility:
            order_by = ApplicationSortingParameters.is_anonymous
        if order_by == ApplicationSortingParameters.type:
            # If the sort type is 'type', sort by the 'is_draft' column
            order_by = ApplicationSortingParameters.is_draft
            # - By default, sorting boolean values in ascending order places `False` (submissions) first.
            # - To ensure drafts (True) come first in ascending order, we invert the sort order.
            sort_order = "asc" if sort_order == "desc" else "desc"
        order_by = camel_to_snake(order_by)
    if sort_order not in ["asc", "desc"]:
        sort_order = None
    return order_by, sort_order


def translate(to_lang: str, data: dict) -> dict:
    """Translate the response to provided language.

    will return the translated object if there is match
    else return the original object
    """
    try:
        translated_data = {}
        if to_lang not in translations:
            raise KeyError
        for key, value in data.items():
            # if matching translation is present for either key / value,
            # then translated string is used
            # original string otherwise
            translated_data[
                translations[to_lang][key] if key in translations[to_lang] else key
            ] = (
                translations[to_lang][value]
                if value in translations[to_lang]
                else value
            )
        return translated_data
    except KeyError as err:
        raise err
    except Exception as err:
        raise err


def get_role_ids_from_user_groups(role_ids, user_role):
    """Filters out formio role ids specific to user groups."""
    if role_ids is None or user_role is None:
        return None

    if any(permission in user_role for permission in [ CREATE_DESIGNS, VIEW_DESIGNS]):
        return role_ids
    if any(permission in user_role for permission in [ MANAGE_TASKS, VIEW_TASKS, ANALYZE_SUBMISSIONS_VIEW]):
        return filter_list_by_user_role(FormioRoles.REVIEWER.name, role_ids)
    if any(permission in user_role for permission in [ CREATE_SUBMISSIONS, VIEW_SUBMISSIONS]):
        return filter_list_by_user_role(FormioRoles.CLIENT.name, role_ids)
    return None


def filter_list_by_user_role(formio_role, role_ids):
    """Iterate over role_ids and return entries with matching formio role."""
    return list(filter(lambda item: item["type"] == formio_role, role_ids))


def get_form_and_submission_id_from_form_url(form_url: str) -> Tuple:
    """Retrieves the formid and submission id from the url parameters."""
    form_id = form_url[form_url.find("/form/") + 6 : form_url.find("/submission/")]
    submission_id = form_url[form_url.find("/submission/") + 12 : len(form_url)]
    return (form_id, submission_id)


def add_sort_filter(query, sort_by, sort_order, model_name):
    """Adding sortBy and sortOrder."""
    order = []
    if sort_by and sort_order:
        for sort_by_att, sort_order_attr in zip(sort_by, sort_order):
            name, value = validate_sort_order_and_order_by(
                sort_order=sort_order_attr, order_by=sort_by_att
            )
            if name and value:
                # Handle null values in is_anonymous to false
                if name == "is_anonymous":
                     order.append(text(f"COALESCE({model_name}.{name}, false) {value}"))
                else:
                    order.append(text(f"{model_name}.{name} {value}"))

        query = query.order_by(*order)
    return query
