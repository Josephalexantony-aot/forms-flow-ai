"""This manages Application submission Data."""

# pylint: disable=too-many-lines

from __future__ import annotations

from flask_sqlalchemy.query import Query
from formsflow_api_utils.utils import (
    FILTER_MAPS,
    add_sort_filter,
    validate_sort_order_and_order_by,
)
from formsflow_api_utils.utils.enums import MetricsState
from formsflow_api_utils.utils.user_context import UserContext, user_context
from sqlalchemy import (
    and_,
    asc,
    case,
    desc,
    func,
    nulls_first,
    nulls_last,
    or_,
    text,
)
from sqlalchemy.orm import aliased

from .application_history import ApplicationHistory
from .audit_mixin import AuditDateTimeMixin, AuditUserMixin
from .base_model import BaseModel
from .db import db
from .draft import Draft
from .form_history_logs import FormHistory
from .form_process_mapper import FormProcessMapper


class Application(
    AuditDateTimeMixin, AuditUserMixin, BaseModel, db.Model
):  # pylint: disable=too-many-public-methods
    """This class manages application against each form."""

    id = db.Column(db.Integer, primary_key=True)
    application_status = db.Column(db.String(100), nullable=False)
    form_process_mapper_id = db.Column(
        db.Integer, db.ForeignKey("form_process_mapper.id"), nullable=False
    )
    process_instance_id = db.Column(db.String(100), nullable=True)
    # Submission id will be null for drafts
    submission_id = db.Column(db.String(100), nullable=True)
    latest_form_id = db.Column(db.String(100), nullable=False)
    is_resubmit = db.Column(db.Boolean, nullable=True, default=False)
    event_name = db.Column(db.String(100), nullable=True)
    is_draft = db.Column(db.Boolean, default=False, index=True)

    draft = db.relationship(
        "Draft", backref=db.backref("Application", cascade="save-update, merge")
    )

    @classmethod
    def create_from_dict(cls, application_info: dict) -> Application:
        """Create new application."""
        if application_info:
            application = Application()
            application.created_by = application_info["created_by"]
            application.application_status = application_info["application_status"]
            application.form_process_mapper_id = application_info[
                "form_process_mapper_id"
            ]
            application.submission_id = application_info["submission_id"]
            application.latest_form_id = application_info["form_id"]
            application.is_draft = application_info.get("is_draft", False)
            application.save_and_flush()
            return application
        return None

    def update(self, mapper_info: dict):
        """Update application."""
        self.update_from_dict(
            [
                "application_status",
                "submission_id",
                "latest_form_id",
                "form_process_mapper_id",
                "process_instance_id",
                "modified_by",
                "is_resubmit",
                "event_name",
                "is_draft",
            ],
            mapper_info,
        )
        self.save_and_flush()

    @classmethod
    def created_by_condition_query_for_draft(cls, query, username):
        """Query to filter by created by if its a draft."""
        query = query.filter(
            or_(
                cls.is_draft.is_(
                    False
                ),  # No need to filter by created_by if it's not a draft
                and_(
                    cls.is_draft.is_(True), cls.created_by == username
                ),  # Filter by created_by if it's a draft
            )
        )
        return query

    @classmethod
    def find_by_id(cls, application_id: int, user_id: str = None) -> Application:
        """Find application that matches the provided id."""
        query = cls.query.join(
            FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
        )
        query = query.filter(cls.id == application_id)
        query = cls.created_by_condition_query_for_draft(query, user_id)
        return FormProcessMapper.tenant_authorization(query=query).first()

    @classmethod
    def find_draft_application_by_user(
        cls, application_id: int, user_id: str = None
    ) -> Application:
        """Find draft application by application id created by specific user."""
        query = cls.query.join(
            FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
        ).filter(
            cls.id == application_id,
            and_(cls.is_draft.is_(True), cls.created_by == user_id),
        )
        return FormProcessMapper.tenant_authorization(query=query).first()

    @classmethod
    def find_auth_by_id(cls, application_id: int, user_id: str) -> Application:
        """Find application that matches the provided id."""
        result = (
            FormProcessMapper.query.with_entities(
                cls.id,
                cls.application_status,
                cls.submission_id,
                cls.latest_form_id,
                cls.form_process_mapper_id,
                cls.process_instance_id,
                cls.created_by,
                cls.created,
                cls.modified,
                cls.modified_by,
                cls.is_resubmit,
                cls.event_name,
                cls.is_draft,
                case(
                    (
                        and_(cls.is_draft.is_(True), cls.created_by == user_id),
                        Draft.data,
                    ),
                    else_=None,
                ).label("data"),
                FormProcessMapper.process_key,
                FormProcessMapper.process_name,
                FormProcessMapper.process_tenant,
                FormProcessMapper.form_name.label("application_name"),
            )
            .join(cls, FormProcessMapper.id == cls.form_process_mapper_id)
            .outerjoin(Draft, cls.id == Draft.application_id)
            .filter(Application.id == application_id)
            .filter(
                or_(
                    cls.is_draft.is_(
                        False
                    ),  # No need to filter by created_by if it's not a draft
                    and_(
                        cls.is_draft.is_(True), cls.created_by == user_id
                    ),  # Filter by created_by if it's a draft
                )
            )
        )
        result = FormProcessMapper.tenant_authorization(query=result)
        return result.first()

    @classmethod
    def find_all_application_status(cls):
        """Find all application status."""
        query = cls.query.join(
            FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
        ).distinct(Application.application_status)
        query = FormProcessMapper.tenant_authorization(query)
        return query

    @classmethod
    def find_by_ids(cls, application_ids) -> Application:
        """Find application that matches the provided id."""
        return cls.query.filter(cls.id.in_(application_ids)).order_by(
            Application.id.desc()
        )

    @classmethod
    def find_all(
        cls,
        page_no: int,
        limit: int,
        order_by: str,
        sort_order: str,
        **filters,
    ) -> Application:
        """Fetch all application."""
        query = cls.filter_conditions(**filters)
        query = FormProcessMapper.tenant_authorization(query=query)
        query = cls.filter_draft_applications(query=query)
        order_by, sort_order = validate_sort_order_and_order_by(order_by, sort_order)
        if order_by and sort_order:
            table_name = "application"
            if order_by == "form_name":
                table_name = "form_process_mapper"
            query = query.order_by(text(f"{table_name}.{order_by} {sort_order}"))
        total_count = query.count()
        pagination = query.paginate(page=page_no, per_page=limit, error_out=False)
        return pagination.items, total_count

    @classmethod
    def filter_conditions(cls, **filters):
        """This method creates dynamic filter conditions based on the input param."""
        filter_conditions = []
        query = cls.query.join(
            FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
        )
        for key, value in filters.items():
            if value:
                filter_map = FILTER_MAPS[key]
                model_name = (
                    Application
                    if filter_map["field"] not in ["form_name", "parent_form_id"]
                    else FormProcessMapper
                )
                condition = Application.create_filter_condition(
                    model=model_name,
                    column_name=filter_map["field"],
                    operator=filter_map["operator"],
                    value=value,
                )
                filter_conditions.append(condition)
        query = query.add_columns(
            cls.id,
            cls.application_status,
            cls.submission_id,
            cls.latest_form_id,
            cls.form_process_mapper_id,
            cls.process_instance_id,
            cls.created_by,
            cls.created,
            cls.modified,
            cls.modified_by,
            cls.is_resubmit,
            cls.event_name,
            cls.is_draft,
            FormProcessMapper.form_name.label("application_name"),
            FormProcessMapper.process_key.label("process_key"),
            FormProcessMapper.process_name.label("process_name"),
            FormProcessMapper.process_tenant.label("process_tenant"),
            FormProcessMapper.parent_form_id,
        )
        query = query.filter(*filter_conditions) if filter_conditions else query
        return query

    @classmethod
    def find_all_by_user(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        cls,
        user_id: str,
        view_only_submission: bool,
        page_no: int,
        limit: int,
        order_by: str,
        sort_order: str,
        include_drafts: str,
        only_drafts: str,
        **filters,
    ) -> Application:
        """Fetch applications list based on searching parameters for Non-reviewer."""
        query = cls.filter_conditions(**filters)
        query = FormProcessMapper.tenant_authorization(query=query)
        query = query.filter(Application.created_by == user_id)
        # if view_only_submission is True, then we need to filter out drafts and resubmissions
        if view_only_submission:
            query = query.filter(
                ~or_(
                    cls.is_draft.is_(True),  # Exclude drafts
                    cls.is_resubmit.is_(True),
                    cls.application_status.in_(
                        ["Resubmit", "Awaiting Acknowledgement"]
                    ),
                )
            )
        elif only_drafts:  # only draft applications
            query = query.filter(Application.is_draft.is_(True))
        elif not include_drafts:  # only submissions
            query = cls.filter_draft_applications(query=query)
        order_by, sort_order = validate_sort_order_and_order_by(order_by, sort_order)
        if order_by and sort_order:
            table_name = "application"
            if order_by == "form_name":
                table_name = "form_process_mapper"
            query = query.order_by(text(f"{table_name}.{order_by} {sort_order}"))
        total_count = query.count()
        pagination = query.paginate(page=page_no, per_page=limit, error_out=False)
        return pagination.items, total_count

    @classmethod
    def find_id_by_user(cls, application_id: int, user_id: str) -> Application:
        """Find application that matches the provided id."""
        result = (
            cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
            .outerjoin(Draft, cls.id == Draft.application_id)
            .filter(and_(cls.id == application_id, cls.created_by == user_id))
            .add_columns(
                cls.id,
                cls.application_status,
                cls.submission_id,
                cls.latest_form_id,
                cls.form_process_mapper_id,
                cls.process_instance_id,
                cls.created_by,
                cls.created,
                cls.modified,
                cls.modified_by,
                cls.is_resubmit,
                cls.event_name,
                cls.is_draft,
                case((cls.is_draft.is_(True), Draft.data), else_=None).label("data"),
                FormProcessMapper.form_name.label("application_name"),
                FormProcessMapper.process_key.label("process_key"),
                FormProcessMapper.process_name.label("process_name"),
                FormProcessMapper.process_tenant.label("process_tenant"),
            )
        )
        result = FormProcessMapper.tenant_authorization(query=result)
        return result.one_or_none()

    @classmethod
    def find_all_by_user_count(cls, user_id: str) -> Application:
        """Fetch all application."""
        return cls.query.filter(Application.created_by == user_id).count()

    @classmethod
    def find_by_form_id(cls, form_id, page_no: int, limit: int):
        """Fetch all application by form_id."""
        result = (
            cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
            .filter(cls.latest_form_id == form_id)
            .order_by(Application.id.desc())
        )
        if page_no == 0:
            result = FormProcessMapper.tenant_authorization(query=result)
        else:
            result = (
                FormProcessMapper.tenant_authorization(query=result)
                .paginate(page=page_no, per_page=limit, error_out=False)
                .items
            )
        return result

    @classmethod
    def find_by_form_names(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        cls,
        form_names: list(str),
        page_no: int,
        limit: int,
        order_by: str,
        sort_order: str,
        **filters,
    ):
        """Fetch applications list based on searching parameters for Reviewer."""
        query = cls.filter_conditions(**filters)
        query = query.filter(FormProcessMapper.form_name.in_(form_names))
        order_by, sort_order = validate_sort_order_and_order_by(order_by, sort_order)
        if order_by and sort_order:
            table_name = "application"
            if order_by == "form_name":
                table_name = "form_process_mapper"
            query = query.order_by(text(f"{table_name}.{order_by} {sort_order}"))
        total_count = query.count()
        pagination = query.paginate(page=page_no, per_page=limit, error_out=False)
        return pagination.items, total_count

    @classmethod
    def find_applications_by_auth_formids_user(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        cls,
        page_no: int,
        limit: int,
        order_by: str,
        sort_order: str,
        form_ids: str,
        user_name: str,
        **filters,
    ):
        """List applications for Reviewers.

        Based on application auth permissions and user who submitted the application.
        """
        # Get latest row for each form_id group
        filtered_form_query = FormProcessMapper.get_latest_form_mapper_ids()
        filtered_form_ids = [
            data.id for data in filtered_form_query if data.parent_form_id in form_ids
        ]
        query = cls.filter_conditions(**filters)
        query = FormProcessMapper.tenant_authorization(query=query)
        query = query.filter(
            or_(
                FormProcessMapper.id.in_(filtered_form_ids), cls.created_by == user_name
            )
        )
        query = cls.filter_draft_applications(query=query)
        order_by, sort_order = validate_sort_order_and_order_by(order_by, sort_order)
        if order_by and sort_order:
            table_name = "application"
            if order_by == "form_name":
                table_name = "form_process_mapper"
            query = query.order_by(text(f"{table_name}.{order_by} {sort_order}"))
        total_count = query.count()
        pagination = query.paginate(page=page_no, per_page=limit, error_out=False)
        return pagination.items, total_count

    @classmethod
    def find_auth_application_by_process_key(  # pylint: disable=too-many-arguments
        cls,
        process_key: str,
        application_id: int,
    ):
        """Fetch applications list based on searching parameters for Reviewer."""
        query = (
            cls.query.filter(Application.id == application_id)
            .join(
                FormProcessMapper,
                Application.form_process_mapper_id == FormProcessMapper.id,
            )
            .filter(FormProcessMapper.process_key.in_(process_key))
            .add_columns(
                cls.id,
                cls.application_status,
                cls.submission_id,
                cls.latest_form_id,
                cls.form_process_mapper_id,
                cls.process_instance_id,
                cls.created_by,
                cls.created,
                cls.modified,
                cls.modified_by,
                cls.is_resubmit,
                cls.event_name,
                FormProcessMapper.form_name.label("application_name"),
                FormProcessMapper.process_key.label("process_key"),
                FormProcessMapper.process_name.label("process_name"),
                FormProcessMapper.process_tenant.label("process_tenant"),
            )
        )
        query = FormProcessMapper.tenant_authorization(query=query)
        return query.first()

    @classmethod
    def find_id_by_form_names(cls, application_id: int, form_names):
        """Fetch applications by id."""
        return (
            cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
            .filter(
                and_(
                    FormProcessMapper.form_name.in_(form_names),
                    cls.id == application_id,
                )
            )
            .add_columns(
                cls.id,
                cls.application_status,
                cls.submission_id,
                cls.latest_form_id,
                cls.form_process_mapper_id,
                cls.process_instance_id,
                cls.created_by,
                cls.created,
                cls.modified,
                cls.modified_by,
                FormProcessMapper.form_name.label("application_name"),
                FormProcessMapper.process_key.label("process_key"),
                FormProcessMapper.process_name.label("process_name"),
                FormProcessMapper.process_tenant.label("process_tenant"),
            )
            .one_or_none()
        )

    @classmethod
    def find_by_form_id_user(cls, form_id: str, user_id: str, page_no: int, limit: int):
        """Fetch applications by form_id."""
        result = (
            cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
            .filter(and_(cls.latest_form_id == form_id, cls.created_by == user_id))
            .order_by(Application.id.desc())
        )
        if page_no == 0:
            result = FormProcessMapper.tenant_authorization(result)
        else:
            result = (
                FormProcessMapper.tenant_authorization(result)
                .paginate(page=page_no, per_page=limit, error_out=False)
                .items
            )
        return result

    @classmethod
    def find_by_form_ids(cls, form_ids, page_no: int, limit: int):
        """Fetch application based on multiple form ids."""
        result = cls.query.join(
            FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
        )
        if page_no == 0:
            result.filter(
                or_(cls.latest_form_id == form_id for form_id in form_ids)
            ).order_by(Application.id.desc())
        else:
            result.filter(
                or_(cls.latest_form_id == form_id for form_id in form_ids)
                .order_by(Application.id.desc())
                .paginate(page=page_no, per_page=limit, error_out=False)
                .items
            )
        return result

    @classmethod
    def find_all_by_form_id_count(cls, form_id: str):
        """Fetch all application."""
        query = cls.query.join(
            FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
        ).filter(
            cls.latest_form_id == form_id,
            cls.is_draft.is_(False),
        )
        return FormProcessMapper.tenant_authorization(query=query).count()

    @classmethod
    def find_all_by_form_id_user_count(cls, form_id, user_id: str):
        """Fetch all application."""
        query = (
            cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
            .filter(cls.latest_form_id == form_id)
            .filter(Application.created_by == user_id)
        )
        return FormProcessMapper.tenant_authorization(query=query).count()

    @classmethod
    @user_context
    def find_aggregated_applications(
        # pylint: disable-msg=too-many-arguments, too-many-locals, too-many-positional-arguments
        cls,
        from_date: str,
        to_date: str,
        page_no: int,
        limit: int,
        form_name: str,
        sort_by: str,
        sort_order: str,
        order_by: str,
        **kwargs,
    ):
        """Fetch aggregated applications."""
        user: UserContext = kwargs["user"]
        tenant_key: str = user.tenant_key

        def set_sort(sort_by, sort_order):
            if sort_order == "asc":
                return latest_form_name.c[sort_by].asc()
            return latest_form_name.c[sort_by].desc()

        order = "created"
        if order_by == MetricsState.MODIFIED.value:
            order = "modified"

        # to get the max form id to take the latest form name
        max_form_id = (
            db.session.query(
                FormProcessMapper.form_id.label("form_id"),
                FormProcessMapper.parent_form_id.label("parent_form_id"),
                FormProcessMapper.tenant,
                db.func.max(FormProcessMapper.id).label(
                    "id"
                ),  # pylint: disable=not-callable
            )
            .group_by(
                FormProcessMapper.form_id,
                FormProcessMapper.parent_form_id,
                FormProcessMapper.tenant,
            )
            .subquery("max_form_id")
        )

        subquery_application_count = (
            db.session.query(
                max_form_id.c.parent_form_id,
                max_form_id.c.tenant,
                db.func.max(max_form_id.c.id).label("id"),
                db.func.count(Application.id).label("application_count"),
            )
            .join(max_form_id, max_form_id.c.form_id == Application.latest_form_id)
            .filter(getattr(Application, order).between(from_date, to_date))
            .group_by(max_form_id.c.parent_form_id, max_form_id.c.tenant)
            .subquery("subquery_application_count")
        )
        # taking latest form name
        latest_form_name = (
            db.session.query(
                subquery_application_count.c.parent_form_id,
                FormProcessMapper.tenant.label("tenant"),
                FormProcessMapper.form_name.label("form_name"),
                subquery_application_count.c.application_count,
            )
            .join(
                subquery_application_count,
                subquery_application_count.c.id == FormProcessMapper.id,
            )
            .subquery("latest_form_name")
        )

        form_versions = (
            db.session.query(
                FormHistory.parent_form_id,
                FormHistory.form_id,
                FormHistory.id,
                func.row_number()  # pylint: disable=not-callable
                .over(
                    partition_by=FormHistory.parent_form_id,
                    order_by=FormHistory.created.asc(),
                )
                .label("form_id_index"),
            )
            .filter(text("change_log ->>'new_version' = 'true'"))
            .subquery("form_versions")
        )

        # taking all data
        result_proxy = (
            db.session.query(
                latest_form_name.c.parent_form_id,
                latest_form_name.c.application_count.label("submission_count"),
                latest_form_name.c.form_name,
                latest_form_name.c.tenant,
                func.array_agg(  # pylint: disable=not-callable
                    func.json_build_object(
                        "formId",
                        form_versions.c.form_id,
                        "version",
                        form_versions.c.form_id_index,
                    )
                ).label("form_versions"),
            )
            .select_from(form_versions)
            .join(
                latest_form_name,
                latest_form_name.c.parent_form_id == form_versions.c.parent_form_id,
            )
            .group_by(
                latest_form_name.c.parent_form_id,
                latest_form_name.c.application_count,
                latest_form_name.c.form_name,
                latest_form_name.c.tenant,
                form_versions.c.parent_form_id,
            )
            .filter(latest_form_name.c.tenant == tenant_key)
        )

        if form_name:
            result_proxy = result_proxy.filter(
                latest_form_name.c.form_name.ilike(f"%{form_name}%")
            )

        sort_by, sort_order = validate_sort_order_and_order_by(sort_by, sort_order)
        if sort_by and sort_order:
            sort_query = set_sort(sort_by, sort_order)
            result_proxy = result_proxy.order_by(sort_query)
        pagination = result_proxy.paginate(
            page=page_no, per_page=limit, error_out=False
        )
        total_count = result_proxy.count()
        return pagination.items, total_count

    @classmethod
    @user_context
    def find_aggregated_application_status_by_parent_form_id(
        cls, form_id: str, from_date: str, to_date: str, order_by: str, **kwargs
    ):
        """Fetch application status corresponding to parent form id."""
        user: UserContext = kwargs["user"]
        tenant_key: str = user.tenant_key
        sub_query_taking_form_ids = (
            db.session.query(FormProcessMapper.form_id, FormProcessMapper.tenant)
            .filter(FormProcessMapper.parent_form_id == form_id)
            .group_by(FormProcessMapper.form_id, FormProcessMapper.tenant)
            .subquery()
        )

        order = "created"
        if order_by == MetricsState.MODIFIED.value:
            order = "modified"

        result_proxy = (
            db.session.query(
                Application.application_status.label("application_status"),
                db.func.count(Application.id).label("count"),
            )
            .join(
                sub_query_taking_form_ids,
                sub_query_taking_form_ids.c.form_id == Application.latest_form_id,
            )
            .filter(
                and_(
                    getattr(Application, order) >= from_date,
                    getattr(Application, order) <= to_date,
                )
            )
            .filter(sub_query_taking_form_ids.c.tenant == tenant_key)
            .group_by(Application.application_status)
        )
        return result_proxy

    @classmethod
    @user_context
    def find_aggregated_application_status_by_form_id(
        cls, form_id: int, from_date: str, to_date: str, order_by: str, **kwargs
    ):
        """Get application status by form id."""
        user: UserContext = kwargs["user"]
        tenant_key: str = user.tenant_key
        if tenant_key is not None:
            # Incase of multi-tenant environment verify the form_id is authorized for a specific tenant.
            tenant_query = (
                db.session.query(FormProcessMapper.tenant)
                .filter(FormProcessMapper.form_id == form_id)
                .distinct()
            )
            tenant_match = (
                tenant_query.filter(FormProcessMapper.tenant == tenant_key).count() > 0
            )
            if not tenant_match:
                raise PermissionError(f"Access to resource-{form_id} is denied.")

        order = "created"
        if order_by == MetricsState.MODIFIED.value:
            order = "modified"

        result_proxy = (
            db.session.query(
                Application.application_status.label("application_status"),
                db.func.count(Application.id).label("count"),
            )
            .filter(
                and_(
                    getattr(Application, order) >= from_date,
                    getattr(Application, order) <= to_date,
                    Application.latest_form_id == form_id,
                )
            )
            .group_by(Application.application_status)
        )

        return result_proxy

    @classmethod
    def get_total_application_corresponding_to_mapper_id(
        cls, form_process_mapper_id: int
    ):
        """Returns the total applications corresponding to a form_process_mapper_id."""
        result_proxy = (
            db.session.query(
                func.count(Application.id).label(  # pylint: disable=not-callable
                    "count"
                )
            )
            .join(
                FormProcessMapper,
                FormProcessMapper.id == Application.form_process_mapper_id,
            )
            .filter(FormProcessMapper.id == form_process_mapper_id)
            .filter(Application.is_draft.is_(False))
            .one_or_none()
        )
        # returns a list of one element with count of applications
        return result_proxy[0]

    @classmethod
    def get_form_mapper_by_application_id(cls, application_id: int):
        """Fetch form process mapper details with application id."""
        query = (
            FormProcessMapper.query.with_entities(
                FormProcessMapper.process_key,
                FormProcessMapper.process_name,
                FormProcessMapper.process_tenant,
                FormProcessMapper.task_variable,
                FormProcessMapper.form_type,
                FormProcessMapper.id,
            )
            .join(cls, FormProcessMapper.id == cls.form_process_mapper_id)
            .filter(Application.id == application_id)
            .first()
        )

        return query

    @classmethod
    def filter_draft_applications(cls, query: Query):
        """Modifies the query to filter draft applications."""
        if not isinstance(query, Query):
            raise TypeError("Query object must be of type Query")
        return query.filter(cls.is_draft.is_(False))

    @classmethod
    def get_all_application_count(cls):
        """Retrieves all non draft application count."""
        query = FormProcessMapper.tenant_authorization(
            query=cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
        )
        query = cls.filter_draft_applications(query=query)
        return query.count()

    @classmethod
    def get_authorized_application_count(cls, process_key):
        """Retrieves authorized application count."""
        query = FormProcessMapper.tenant_authorization(
            query=cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
        )
        query = cls.filter_draft_applications(query=query)
        query = query.filter(FormProcessMapper.process_key.in_(process_key))
        return query.count()

    @classmethod
    def get_user_based_application_count(cls, user_id):
        """Retrieves user specific application count."""
        query = FormProcessMapper.tenant_authorization(
            query=cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
        )
        query = cls.filter_draft_applications(query=query)
        query = query.filter(Application.created_by == user_id)
        return query.count()

    @classmethod
    def find_form_parent_id_by_application_id(cls, application_id: int) -> Application:
        """Find form parent id for the provided application id."""
        return (
            db.session.query(FormProcessMapper.parent_form_id)
            .join(Application)
            .filter(Application.id == application_id)
            .scalar()
        )

    @classmethod
    def get_auth_application_count_by_form_id_user(cls, form_ids, user_name):
        """Retrieves authorized application count by form ids & submitted user."""
        # Get latest row for each form_id group
        filtered_form_query = FormProcessMapper.get_latest_form_mapper_ids()
        filtered_form_ids = [
            data.id for data in filtered_form_query if data.parent_form_id in form_ids
        ]
        query = FormProcessMapper.tenant_authorization(
            query=cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
        )
        query = query.filter(
            or_(
                FormProcessMapper.id.in_(filtered_form_ids), cls.created_by == user_name
            )
        )
        query = cls.filter_draft_applications(query=query)
        return query.count()

    @classmethod
    def get_application_by_formid_and_user_name(
        cls, formid: str, user_name: str
    ) -> Application:
        """Get application by checking formid and created by."""
        query = FormProcessMapper.tenant_authorization(
            query=cls.query.join(
                FormProcessMapper, cls.form_process_mapper_id == FormProcessMapper.id
            )
        )
        query = query.filter(
            and_(cls.latest_form_id == formid, cls.created_by == user_name)
        )
        return query.first()

    @classmethod
    def apply_submission_sorting(cls, query, sort_by, sort_order, submission_alias):
        """Sort by submission count or latest submission time."""
        order_func, nulls_func = (
            (desc, nulls_last) if "desc" in sort_order else (asc, nulls_first)
        )
        # Sort by latest submission time/submission count, treating NULLs first while ascending & last while descending
        if "latestSubmission" in sort_by:
            return query.order_by(
                nulls_func(order_func(submission_alias.c.latest_submission))
            )
        return query.order_by(
            nulls_func(order_func(submission_alias.c.submissions_count))
        )

    @classmethod
    @user_context
    def get_form_stats(cls, form_ids, query, sort_by, sort_order, **kwargs):
        """Get submission count and latest submission time."""
        user: UserContext = kwargs["user"]

        # Subquery for user's application history
        # Get most recent status update time for each application by this user
        user_history_subq = (
            db.session.query(
                ApplicationHistory.application_id,
                func.max(ApplicationHistory.created).label("latest_submission"),
            )
            .filter(ApplicationHistory.submitted_by == user.user_name)
            .group_by(ApplicationHistory.application_id)
            .subquery()
        )

        # Combined subquery for both stats
        # Get both count and latest time per form
        form_stats_subq = (
            db.session.query(
                FormProcessMapper.parent_form_id,
                func.count(cls.id).label("submissions_count"),  # Count of submissions
                func.max(
                    func.coalesce(
                        user_history_subq.c.latest_submission,  # Either status update time
                        cls.created,  # Or original creation time if there's no entry in history table
                    )
                ).label("latest_submission"),
            )
            .select_from(FormProcessMapper)
            .join(cls, cls.form_process_mapper_id == FormProcessMapper.id)
            .outerjoin(user_history_subq, user_history_subq.c.application_id == cls.id)
            .filter(
                FormProcessMapper.tenant == user.tenant_key,
                cls.created_by == user.user_name,
                cls.is_draft.is_(False),
                FormProcessMapper.parent_form_id.in_(form_ids),
            )
            .group_by(FormProcessMapper.parent_form_id)
            .subquery()
        )
        form_stats_alias = aliased(form_stats_subq)
        # Join with main query
        query = query.outerjoin(
            form_stats_alias,
            FormProcessMapper.parent_form_id == form_stats_alias.c.parent_form_id,
        )
        # Sort by submission count or latestSubmission
        if "submissionCount" in sort_by or "latestSubmission" in sort_by:
            query = cls.apply_submission_sorting(
                query, sort_by, sort_order, form_stats_alias
            )
        return query, form_stats_alias

    @classmethod
    def find_all_active_by_formid(
        cls,
        page_number=None,
        limit=None,
        sort_by=None,
        sort_order=None,
        search=None,
        form_ids=None,
        fetch_submissions_count=False,
        **filters,
    ):  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """Fetch all active form process mappers by authorized forms."""
        # Get latest row for each form_id group
        filtered_form_query = FormProcessMapper.get_latest_form_mapper_ids()
        filtered_form_ids = [
            data.id for data in filtered_form_query if data.parent_form_id in form_ids
        ]
        query = FormProcessMapper.filter_conditions(**filters)
        query = query.filter(
            FormProcessMapper.id.in_(filtered_form_ids),
        )
        query = FormProcessMapper.add_search_filter(query=query, search=search)
        query = FormProcessMapper.access_filter(query=query)
        query = add_sort_filter(
            sort_by=sort_by,
            sort_order=sort_order,
            query=query,
            model_name="form_process_mapper",
        )

        # Prepare the entities for the query
        entities = [
            FormProcessMapper.id,
            FormProcessMapper.process_key,
            FormProcessMapper.form_id,
            FormProcessMapper.form_name,
            FormProcessMapper.modified,
            FormProcessMapper.description,
            FormProcessMapper.parent_form_id,
        ]
        if fetch_submissions_count:
            # Get the submission count subquery
            query, submission_alias = cls.get_form_stats(
                form_ids, query, sort_by, sort_order
            )
            entities.extend(
                [
                    submission_alias.c.submissions_count,
                    submission_alias.c.latest_submission,
                ]
            )

        # Select the required columns
        query = query.with_entities(*entities)

        # Paginate the results
        total_count = query.count()
        limit = total_count if limit is None else limit
        query = query.paginate(page=page_number, per_page=limit, error_out=False)
        return query.items, total_count

    @classmethod
    def get_draft_by_parent_form_id(cls, parent_form_id: str) -> Draft:
        """Get all draft against one form id."""
        get_all_mapper_id = (
            db.session.query(FormProcessMapper.id)
            .filter(FormProcessMapper.parent_form_id == parent_form_id)
            .all()
        )
        result = cls.query.join(Draft, Draft.application_id == cls.id).filter(
            and_(
                cls.form_process_mapper_id.in_([id for id, in get_all_mapper_id]),
                cls.is_draft.is_(True),
            )
        )
        return FormProcessMapper.tenant_authorization(result).all()
