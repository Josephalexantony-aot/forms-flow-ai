# Changelog for formsflow.ai

Mark  items as `Added`, `Changed`, `Fixed`, `Modified`, `Removed`, `Untested Features`, `Upcoming Features`, `Known Issues`


## 7.1.0 - 2025-07-01

`Added`

**forms-flow-web**
* Added new User Interfaces: for task page, submissions
* Added environment variables:
   * `ENABLE_COMPACT_FORM_VIEW` Set to true to reduce extra space between form components and display more components in the viewport.
   * `USER_NAME_DISPLAY_CLAIM` to specify if the app should use a different attribute than the default 'username' claim from Keycloak
   * `GRAPHQL_API_URL` to connect to the datalayer
   * `MF_FORMSFLOW_REVIEW_URL` for reviewer micro-frontend
   * `MF_FORMSFLOW_SUBMISSIONS_URL` for submissions micro-frontend

**formsflow-api**
* Below fields added to application list endpoint
   * Added parentFormId filter parameter to filter the submissions for a specific form
   * Added the includeDrafts parameter to include drafts along with submissions.
   * Added the onlyDrafts parameter to retrieve only drafts.
   * Added the createdUserSubmissions parameter to filter submissions created by a specific user.
* Added a new column, is_draft, to the application table to identify draft entries.
* Added Alembic script to update existing active drafts by setting is_draft to true in the application table.
* Added the includeSubmissionsCount=true parameter to the form list endpoint to include the submissions count.
* Added below endpoints
   * Public draft update: `/public/application/<id>`
   * Draft submit by id: `/application/<id>/submit`
   * Public draft submit by id: `/public/application/<id>/submit`
   * Delete draft by id: `/application/<id>`
* Added columns filter_type, parent_filter_id to the filter table.
* Added script to migrate existing filters to TASK filter type.
* Added variables(task_variables) as part of import and export.
* Added Endpoint `/filter/filter-preference ` for saving user's filter preference data
* Added new table called filter_preferences to handle filter preference of a user
* Added new table task_outcome_configuration to store workflow transition rules
* Added `/tasks/task-outcome-configuration` endpoint for task configuration storage
* Added `/tasks/task-outcome-configuration/<task_id>` endpoint for task configuration lookup
* Added new permissions and enhanced permission definitions with categories to `/permissions` endpoint
* Added new environment variables:
   * `USER_NAME_DISPLAY_CLAIM` to specify if the app should use a different attribute than the default 'username' claim from Keycloak
   * `FORMIO_JWT_EXPIRE` to handle formio jwt token expire time

**formsflow-bpm**
* Added new environment variables:
   * `USER_NAME_DISPLAY_CLAIM` to specify if the app should use a different attribute than the default 'username' claim from Keycloak
   * `SERVER_MAX_HTTP_REQUEST_HEADER_SIZE` to configure the maximum size of the HTTP request header

**formsflow-documents**
* Added new environment variable:
   * `ENABLE_COMPACT_FORM_VIEW` Set to true to reduce extra space between form components and display more components in the viewport.
   * `FORMIO_JWT_EXPIRE` to handle formio jwt token expire time

**forms-flow-idm**
* Added view_submissions permission to the service account roles to support export PDF with service account token
* Added new permissions to the forms-flow-ai realm
* To migrate the new roles(permissions) to the realm Refer [here](./forms-flow-idm/migration/README.md#710)

`Modified`

**forms-flow-web**
* Modified User Interfaces of:
   * Client Table
   * Draft and Submission list table
   * Form submission view
   * Permission selection modal

**formsflow-api**
* Modified the `/application/<id>` GET and UPDATE endpoints to support draft get and update.
* Updated the anonymous draft POST API URL from `/draft/public/create` to `/public/draft`.
* Updated the theme GET API URL from `/themes` to `/public/themes`.
* Updated API authorization with new permissions

`Removed`

**formsflow-api**
* Removed below endpoints
   * Get/Update/Delete draft by id: `/draft/<id>`
   * Draft list: `/draft`
   * Public draft update: `/draft/public/<id>`
   * Draft submit by id: `/draft/<id>/submit`
   * Public draft submit by id: `/draft/public/<id>/submit`
* Removed fields: order, resourceId, description, and taskVisibleAttributes from filter table

**formsflow-bpm**
* FormAccessTokenCacheListener is removed from the codebase (As outlined in the Removed section of the  forms-flow-bpm [v4.0.5](./CHANGELOG.md#405---2022-04-19))

*Upgrade notes:*

**forms-flow-web**
   * webpack version upgraded to 5.94.0

**forms-flow-api**
* Python version upgraded to 3.13.2

**forms-flow-idm**
   * Keycloak Version upgraded to 26.1.2

**forms-flow-documents**
   * Python version upgraded to 3.13.2


`Generic Changes`
* Added new micro-frontends: forms-flow-review, forms-flow-submissions

`Known Issues`

* If a form's version changes and it is already selected in an existing task filter, the user must reselect the form in the filter edit to ensure proper form name in UI.
* In Task Filters, specifying "Tasks Accessible To" either a role or an assignee is mandatory starting from version v7.1.0 when saving a filter. As a result, after upgrading from v7.0.0 to v7.1.0, any existing filters created in v7.0.0 or earlier that do not have a role or assignee selected will still function as expected, but cannot be updated unless one of these fields is provided.
* When a user views the details of a submission from the ANALYZE tab in the sidebar, the active tab is incorrectly highlighted as SUBMIT instead of ANALYZE.

## 7.0.4 - 2025-06-26

`Modified`

**forms-flow-documents**
* Migrated CSS and JS dependencies from CDN links to local static files
* Refactored `index.html` to reference local static assets for CSS and JS
* Increased PDF generation wait time to 60 seconds

## 7.0.3 - 2025-06-13

`Added`
**forms-flow-bpm**
* Addition of security level config to bpmn docker compose to resolve Inconsistent CSRF token behavior


## 7.0.2 - 2025-06-04
`Added`
**forms-flow-bpm**
* Addition of ssl certificate in bpm layer to work on secured environments and updated the docker file

## 7.0.1 - 2025-03-15

`Added`

* Additional Custom theme variables added for extensive customizations
* Added shared realm support for application

`Modified`
* Issue with Simple conditional logic option of formio components not returning component names fixed


## 7.0.0 - 2025-01-10

`Added`

**forms-flow-web**
* Added redesigned form and workflow UI for designer 
   * Layout and Flow listing
   * Layout and Flow Create/ Edit page:
      * Import, export, duplicate, delete, history, preview, authorization settings
* Added flow builder to design page
* Added new user settings option in sidebar
* Added new css variables to support dynamic theming of application using customTheme file
* Added advanced logic conditioning in formio component settings to allow chaining of conditions for forms
* Added the displayForRole custom property to the form component to display data for a specific role
* Added certain user data as hidden variables in the form design by default:
   * Current User
   * Submitter Email
   * Submitter First Name
   * Submitter Last Name
   * Current User Roles

**forms-flow-api**
   * Added new endpoints for:
      * Form validation: `/form/validate`
      * Layout + Flow import:  `/import`
      * Layout + Flow export:  `/form/<mapper_id>/export`
      * Flow migration - `/process/migrate`
      * Layout + Flow publish: `/form/<mapper_id>/publish` 
      * Layout + Flow unpublish:  `/form/<mapper_id>/unpublish`
      * List permissions:  `/roles/permissions`
      * Theme customization:
         * Create, Get, Update theme: `/themes`
      * Subflow and decision table redesign
         *  Create/List: `/process` 
         *  Get/Update/Delete by id:    `/process/<id>`
         *  Get by key:   `/process/<key>`
         *  Get history:   `/process/<key>/versions`
         *  Validate:  `/process/validate`
         *  Publish:  `/process/<id>/publish`
         *  Unpublish:  `/process/<id>/unpublish`


   * Added Alembic scripts to implement the following changes:
      * Created tables for theme customization(Themes), Process, and User
      * Updated the filter table to include filter_order, the form history table to add major_version and minor_version, and the form_process_mapper table to include prompt_new_version & is_migrated
      * Populated major_version and minor_version columns in existing form history records
      * Altered audit datetime fields to be timezone-aware
      * Updated the process_name format from process_name(process_key) to process_name
      * Increased the length of form_name, process_key, and process_name fields in the form_process_mapper table to 200


 
 **forms-flow-bpm**
* Added support to fetch secrets from Vault
* Added BPM authorizations dynamically upon startup
<br><br>

`Modified`

**formsflow-web**
* Modified  Flow and Layout to a one-to-one association, with the combination now referred to as a Form
* Modified Navbar and converted to Sidebar:
   * Categorized UI to menus and sub-menus based on functionality 
   * Menus visibility is controlled based on user permissions
   * Moved language selection to the user settings modal, accessible by clicking the username in the bottom-left corner of the sidebar
   * Moved client submission from the Forms menu to the Submit menu (Submit → Forms → All Forms)
   * Moved form design to Design menu
   * Moved Subflows (BPMN) and Decision Tables (DMN) to individual submenus under the Design
   * Moved Manage roles, users and dashboards under Manage menu
   * Moved Insights and Metrics  under Analyze menu
   * Moved Tasks under  Review menu

* Modified form history management to include major and minor versions
* Modified RBAC mechanism:
   * Users can create new roles with specific permissions for more granular application access control. Refer [here](https://aot-technologies.github.io/forms-flow-ai-doc/roles-permissions) for more
* Authorization updates:
   * Permissions options in settings for Designers are changed : 
      * 'All Designers' option is removed 
   * Permissions options in settings for reviewer to view submission are changed to generic view Submission permissions:
      * 'All Reviewers' changed to 'Submitter',
      * 'Specific Reviewers' changed to 'Submitter and specified roles'


**forms-flow-api**
* Modified authorization endpoints for:
   * updated  permissions
   * sub flow and decision table redesign
   * Form create, mapper create and authorization create apis combined into form-design

**forms-flow-bpm**
* Existing users, refer [here](./forms-flow-bpm/migration#migration-tasks-for-bpm) for forms-flow-bpm migration changes

**forms-flow-documents**
* Modified endpoint authorizations  based on updated  permission mechanism

**forms-flow-idm**
* Refer [here](./forms-flow-idm/README.md) for Permission matrix migration changes in IDM 
<br><br>


`Removed`

**formsflow-web**
* Removed workflow selection from form edit page

**forms-flow-api**
* Removed form_mapper create API
<br><br>

*Upgrade notes:*

**forms-flow-web**
* Npm package version upgraded to 16.20.0

**forms-flow-api**

   * Python version upgraded to 3.12.6

**forms-flow-bpm**

   * SpringBoot version upgraded to 3.3.5
   * Camunda version upgarded to 7.21
   * spring-websocket version upgarded to 6.1

**forms-flow-idm**

* Keycloak Version upgraded to 25.0.0


**forms-flow-documents**

   * Python version upgraded to 3.12.6

**forms-flow-data-analysis-api**

   * Python version upgraded to 3.12.6

**forms-flow-analytics**

   * Redash version upgraded to 24.04.0

<br><br>


`Generic Changes`
* Designer page redesign
* Workflow selection from edit page is not available now, instead users have to create workflow while form creation itself
* Added new micro-frontend : forms-flow-components
* Fixed security vulnerabilities
* Refer [version documentation](https://aot-technologies.github.io/forms-flow-ai-doc/#version_upgrade) for environment variable changes

`Known Issues`
* The language translation of the entire UI is not perfect at the moment, so some glitches may be expected.
* forms-flow-web test cases are not fully covered

#### <ins>Premium Features </ins>

`Added` 

**forms-flow-web**
* Added no-code creation
* Added regenerate option for form creation with Flow-E

**forms-flow-api**
* Added process_type  column to templates

**forms-flow-documents**
* Added export pdf for bundle

**forms-flow-data-analysis-api**
* Added regenerate support in chat bot form creation

`Modified`

**forms-flow-web**
* Modified premium icons
* Moved Bundle as separate sub-menu under Design menu in sidebar
* Moved Build using AI feature (Flow-E)  to form creation page from edit page.
* Moved select from template feature to form listing page from edit page.
* Modified design for save as template
* Modified the bundle submission logic to retrieve submission data for the currently viewed form instead of fetching all submission data.

**forms-flow-api**
* Updated the `bundles/execute-rules` API to expect only the currently edited data instead of the entire data. The API fetch the necessary data from Form.io to execute rule.

`Removed`

**forms-flow-web**
* Forms that should be included in the bundle no longer require selecting 'enable bundling' from the edit page.
* Removed short intro from template creation modal
<br><br>

## 6.0.2 - 2024-06-05

`Added`

**forms-flow-web-root-config**
* Added env variable `LANGUAGE` for default language setting

`Fixed`

**forms-flow-web-root-config**
* Fixed service worker cache issue

**forms-flow-bpm**
* Fixed white label error on login to bpm


`Modified`

**forms-flow-web**
* The tenant user's default language is set from their data, tenant data, or the default application language.
  

## 6.0.1 - 2024-05-21

`Added`

**forms-flow-web-root-config**
* Added resouce bundle for Spanish 
  
`Fixed`

**forms-flow-web-root-config**
* Fixed service worker cache issue
  
## 6.0.0 - 2024-04-05

`Added`

**forms-flow-web**

* Added user search by role for Admin
* Added option to add registered user to the tenant
* Implemented functionality to generate filters based on form


**forms-flow-bpm**

* Added new field to notify listener to support email address injection

**forms-flow-api**

* Added the feature to capture task variables on application creation without `FormBPMFilteredDataPipelineListener` during initial submission
* Added user search by role for Admin
* Added option to add registered user to the tenant

**forms-flow-data-analysis-api**

* Added environment variable API_LOG_ROTATION_WHEN for specifying the frequency of log file rotation
* Added environment variable API_LOG_ROTATION_INTERVAL for setting the time interval for log file rotation
* Added environment variable API_LOG_BACKUP_COUNT for determining the number of backup log files to keep

`Modified`

**forms-flow-web**
* Task filter enhancements: 
   * Updated default Tasks Filter to display tasks authorized for current logged-in user
   * Modified candidate group listing based on logged user access in filter create
   * Modified Assignee in create filter from manual input to select from list
   * Modified Candidate group label to User group/ User role
   * Modified definition key to workflow name select for workflow selection
   * Modified "Show task based on logged user roles" to "Display authorized tasks based on user roles" which is visible to admin
   users only, will be true by default
   * Task variable create UI and UX change
   * Adjusted task variables according to task attributes in card view 
   * Updated default All Tasks Filter to display tasks authorized for current logged-in user
* Modified user listings to exclusively display users associated with the respective tenant for multi-tenant admin

**forms-flow-api**

* Changes have been made to the Roles and Groups endpoint to accommodate modifications related to subgroups in Keycloak 23.

*Upgrade notes:*

**forms-flow-bpm**

   * SpringBoot version upgraded to 3.1.10
   * groovy version upgraded to 3.0.21
   * postgresql version upgraded to 42.7.2
   * graalvm version upgraded to 23.0.0
   * snakeyaml version upgraded to 2.2

**forms-flow-api**

   * Python version upgraded to 3.12.1

**forms-flow-documents**

   * Python version upgraded to 3.12.1

**forms-flow-data-analysis-api**

   * Python version upgraded to 3.11.7

`Generic Changes`

* Fixed security vulnerabilities

#### <ins>Premium Features </ins>

`Added` 

**froms-flow-web**
* Added IPASS integration
* Added task variables from forms of a bundle to filter creation

**forms-flow-data-analysis-api**
* Added new env variable `CHAT_BOT_CONTEXT_KEY` to define the context for chat bot

**forms-flow-bpm**
* Added `iPaasListener` to support IPASS integration

**forms-flow-api**
* Added new endpoints to support IPASS

`Modified`

**forms-flow-data-analysis-api**
* CHAT_URL port number updated

`Fixed`

**froms-flow-web**
* Fixed task details view of bundle in list view
  

## 5.3.1 - 2024-02-14

`Fixed`

**forms-flow-web**

* Fixed task page infinity loading issue
* Fixed task list filter API breaking on initial time
* Fixed tenant based all tasks not showing issue

**forms-flow-documents**

* Fixed security vulnerabilities

**forms-flow-data-analysis-api**

* Fixed security vulnerabilities

`Modified`

**forms-flow-api**

* Changes have been made to the Roles and Groups endpoint to accommodate modifications related to subgroups in Keycloak 23.

#### <ins>Premium Features </ins>

`Fixed`

* Fixed category listing for pre-built templates for multi-tenant environment.

`Added`

**forms-flow-bpm**

* Added new field injection `emailAddress` in Notify Listener to allow email addresses in addition to group names.


## 5.3.0 - 2023-11-24

`Added`

**forms-flow-web**

* Added new UI for forms, submissions, tasks, processes, dashboards, navbar
* Added RBAC support in form listing for reviewer
* Added RBAC support in submission(application) listing for client and reviewer
* Added form description to form
* Added a description input field for the form.
* Added create custom filter for task in task page
* Added environment variable `DATE_FORMAT` to change the date format
* Added environment variable `TIME_FORMAT` to change the time format
* Added environment variable `CUSTOM_THEME_URL` to override the theme
* Added environment variable `CUSTOM_RESOURCE_BUNDLE_URL` to customize resource bundle for internationalization 

**forms-flow-api**

* Added RBAC support in form listing for reviewer
* Added RBAC support in submission(application) listing for client and reviewer
* Added migration script to move existing task filters from forms-flow-bpm to forms-flow-api, checkout [here]( ./forms-flow-api/README.md#migration-script-for-existing-users)
* Added environment variable `API_LOG_ROTATION_WHEN` for specifying the frequency of log file rotation
* Added environment variable `API_LOG_ROTATION_INTERVAL` for setting the time interval for log file rotation
* Added environment variable `API_LOG_BACKUP_COUNT` for determining the number of backup log files to keep

**forms-flow-bpm**

* Added task filter custom implementation
* Added multi-modules

**forms-flow-documents**

* Added environment variable `API_LOG_ROTATION_WHEN` for specifying the frequency of log file rotation
* Added environment variable `API_LOG_ROTATION_INTERVAL` for setting the time interval for log file rotation
* Added environment variable `API_LOG_BACKUP_COUNT` for determining the number of backup log files to keep

`Modified`

**forms-flow-web**

* Modified Tasks page with List view and Card view of tasklist
* Modified Applications to Submissions in UI
* Modified accessibility enhancement
* Modified Name, Type, Path as advanced options while form create 
  
`Removed`

**forms-flow-web**

* Removed filter by form type from form listing table
 

`Generic Changes`

* Move task filters from forms-flow-bpm to forms-flow-web
* Support Resubmit/ Edit Submission dynamically in the application flow with respect to isResubmit Key

`Solution Component Upgrades`

**forms-flow-api**

* Flask upgraded to 2.3.3 and fixed security vulnerabilities
  
**forms-flow-web**

* Fixed security vulnerabilities

**forms-flow-bpm**

* Camunda upgraded to 7.20.0, SpringBoot upgraded to 3.1.5 and fixed security vulnerabilities

**forms-flow-documents**

* Flask upgraded to 2.3.3 and fixed security vulnerabilities

#### <ins>Premium Features </ins>

`Added`

**forms-flow-web**

* Added RBAC(Role Based Access Control) support in form bundling, refer [here](https://aot-technologies.github.io/forms-flow-ai-doc/#rbac).
* Added Templates feature, refer [here](https://aot-technologies.github.io/forms-flow-ai-doc/#templates) for more.
* Added AI chat assist support in form creation, refer [here](https://aot-technologies.github.io/forms-flow-ai-doc/#chatbot) for more.
* Added environment variables `ENABLE_CHATBOT`, `CHATBOT_URL` for AI chat assist support.

**forms-flow-data-analysis-api**

* Added environment variables `OPENAI_API_KEY`, `CHAT_BOT_MODEL_ID` for AI chat assist support.


**forms-flow-api**

* Added RBAC(Role Based Access Control) support in form bundling.

`Fixed`

**forms-flow-api**

* Fixed task variable updation issue on resubmit in form bundling.
  

## 5.2.1 - 2023-09-01

`Fixed`

**forms-flow-web**

* Fixed bpmn property panel css issue.

**forms-flow-documents**

* Fixed the problem of conflicting versions between Chrome and Chrome Driver when downloading forms.


## 5.2.0 - 2023-06-30

`Added`

**forms-flow-web**

* Added `Form bundling` premium feature, refer [here](https://aot-technologies.github.io/forms-flow-ai-doc/#formBundling) for more details.
* Added RBAC(Role Based Access Control) support in form listing for designer and client, for more details checkout [here](https://aot-technologies.github.io/forms-flow-ai-doc/#rbac).
* Added admin module for adding keycloak roles and user assignment.
* Added formsflow-admin group for RBAC support.


**forms-flow-web-root-config**

* Added micro-frontend integration using single-spa, for more details checkout [here](./forms-flow-web-root-config/README.md#integrate-micro-front-end-modules-into-host-applications).
* Added environment variables `MF_FORMSFLOW_WEB_URL`, `MF_FORMSFLOW_NAV_URL`, `MF_FORMSFLOW_SERVICE_URL`, `MF_FORMSFLOW_ADMIN_URL`, `MF_FORMSFLOW_THEME_URL` to get MicroFrontend Components Created.
* Added environment variables `ENABLE_FORMS_MODULE`, `ENABLE_TASKS_MODULE`, `ENABLE_DASHBOARDS_MODULE`, `ENABLE_PROCESSES_MODULE`, `ENABLE_APPLICATIONS_MODULE` to disable a particular module in forms-flow-web.
* Added environment variable `CUSTOM_THEME_URL` for providing theming configuration.


**forms-flow-bpm**

* Added migration to support new Role Based Access(RBAC) with existing camunda authorizations.

**forms-flow-api**

* Added RBAC(Role Based Access Control) support in form listing for designer and client, click [here](https://aot-technologies.github.io/forms-flow-ai-doc/#rbac) for more details.
* Added migration script for existing users to get all forms listed, checkout [here]( ./forms-flow-api/README.md#migration-script-for-existing-users).
* Added admin module for adding keycloak roles and user assignment.
* Added formsflow-admin group for RBAC support.


`Modified`

**forms-flow-web**

* Application history is modified to Application status and Request status.
* Environment variable `USER_ACCESS_PERMISSIONS` is replaced with `ENABLE_APPLICATION_ACCESS_PERMISSION_CHECK` to enable Role level permission.

**forms-flow-analytics**

* Redash upgraded from version 10.1.4 to 10.1.5.

`forms-flow-api`

*Upgrade notes:*

* Flask upgraded from version 2.1.3 to 2.3.2.


`Fixed`

**forms-flow-web**

* Fixed resubmit issue in form adapter for custom submission.

**forms-flow-bpm**

* Task list variables not updated on re-submission by client issue fixed.

`Generic Changes`

* forms-flow-web is replaced by forms-flow-web-root-config as the deafult web application, for the setup refer [here](./forms-flow-web-root-config)
* Added Micro-frontend feature to enable component level customisation  which includes
     * forms-flow-admin (includes functionalities available for the user with admin privilages)
     * forms-flow-navbar (trigger the routing, internationalization, and login/logout functionalities for all users)
     * forms-flow-service (contains all the common functionalties used by micro front-ends like authentication service, storage APIs etc.)
     * forms-flow-theme (contains the common style sheet shared by all micro-front-ends)<br>
        Refer the [forms-flow-ai-micro-front-ends](https://github.com/AOT-Technologies/forms-flow-ai-micro-front-end) repository for further details.
* Dashboard authorization is moved from designer role to admin user.

#### <ins>Premium Features </ins>

`Added`

**forms-flow-web**

* Added `form bundling` feature as a premium feature, refer [here](https://aot-technologies.github.io/forms-flow-ai-doc/#formBundling) for more details.

**forms-flow-bpm**

* Added CombineSubmissionBundleListener to support form bundling feature.
* Added RequestStateListener to support Request status.
* Added skip-sanitize flag to request header for calls from BPM to Form.io.

`Modified`

**forms-flow-web**

* To enable tracking of individual requests within the bundle, the application history has been updated to Application status and Request status.

`Generic changes`

* During the process of form bundling, it is necessary to configure task variables while designing each individual form.


## 5.1.1 - 2023-05-18

`Added`

**forms-flow-bpm**

* `External Task` APIs are exposed in bpm abstraction layer.

`Modified`

**forms-flow-bpm**

*Upgrade notes:*

* camunda upgraded from version 7.17.0 to 7.18.0.
* camunda-keycloak upgraded from version 2.2.3 to 7.18.0.
* camundaConnect upgraded from 1.5.0 to 1.5.4.
* camundaMail upgraded from 1.3.0 to 1.5.0.
* camunda-template-engines upgraded from 1.0.0 to 2.1.0
* spring boot upgraded from version 2.6.6 to  2.7.11.
* spring security Oauth2 upgraded from version 2.6.6 to 2.6.7.
* camunda-bpm-assert upgraded from 12.0 to 13.0.
* groovy upgraded from 3.0.13 to 3.0.17.
* graalVm upgraded from 22.1.0.1 to 22.3.2.
* jackson upgraded from version 2.14.0 to 2.15.0.


## 5.1.0 - 2022-01-18

`Added`

**forms-flow-web**

* Added form versoning.
* Added discard option for draft feature.
* Added form embedding.
* Added support for resources

**forms-flow-forms**

* Added environment variable `FORMIO_CLIENT_UI`.
* Added health check API-end point `/checkpoint`

**forms-flow-api**

* Added DB changes to accomodate form type, parent form id. 
* Added migration scripts in the alembic file to resolve schema conflicts while db upgrade and downgrade, check out [here](./forms-flow-api/migrations/versions/1a55b7674144_form_history.py).
* Added new table for form history
* Added new api to get form history by form id.
* Added new api to delete draft.
* Added new api to get the list of users for a role/group from keycloak.

**forms-flow-bpm**

* Added environment variables `REDIS_ENABLED`,`REDIS_HOST`,`REDIS_PORT`,`REDIS_PASSCODE` and `SESSION_COOKIE_SECURE`.

**forms-flow-documents**

* Added support for PDF templating.


`Modified`

**forms-flow-api**

* Updated certifi to 2022.12.7, protobuf to 3.20.2 and  joblib to 1.2.0.
* Modified swagger documentation.



**forms-flow-bpm**

*Upgrade notes:*

* spring boot upgraded from version 2.6.4. to  2.6.6.
* spring websocket upgraded from version 5.3.4 to 5.3.20.
* spring messaging upgraded from version 5.3.4 to 5.3.20.
* spring security Oauth2 upgraded from version 2.6.4. to 2.6.6.
* postgresql upgraded from version 42.4.1 to 42.4.3.
* jackson upgraded from version 2.13.3 to 2.14.0.


`Fixed`

**forms-flow-api**

* Fixed Python security vulnerabilities.

`Generic Changes`
* In Quick Installation:
<br> &nbsp;&nbsp;&nbsp;&nbsp;Fixed versions for databases.<br> &nbsp;&nbsp;&nbsp;&nbsp;Reduced script size.<br> &nbsp;&nbsp;&nbsp;&nbsp;Added IP confirmation to avoid IP issues.

* Moved form list of designer to forms-flow-api.

`Known Issues`

**forms-flow-bpm**
* Camunda Integration shows Invalid Credentials with formsflow.ai docker deployment, for more details refer [here](https://github.com/AOT-Technologies/forms-flow-ai/issues/978).
       
Note: Temporary fix added. Setting the value of environment variable `SESSION_COOKIE_SECURE` to `false` makes the camunda login works with ip.
For a production setup value should be true, which will work with Kubernetes and docker deployments with nginx.


## 5.0.2 - 2022-12-07

**forms-flow-web**

`Fixed`

* Frozen UI during form design.

## 5.0.1 - 2022-10-10

**forms-flow-web**

`Added`

* Added websocket support for multitenancy.

`Modified`

* Modified task page UI.
* Modified alignment of wizard.

`Removed`

* Removed environment variable `REACT_APP_FORMIO_JWT_SECRET` form [config.sample.js](./forms-flow-web/public/config/config.sample.js).

**forms-flow-api**

`Added`

* Return the role name as path for authorization.
* Added formsflow API support to start application with data.

**forms-flow-bpm**

`Added`

* Added new endpoints for process instance variables.
* Added web socket support files to build.



## 5.0.0 - 2022-09-02

`Added`

**forms-flow-web**

* Added pagination, search and sort for metrics page.
* Added default workflow for designer.
* Added Internationalization.
* Added multi-tenancy support.
* Added modal for submission details on metrics page.
* Added support for wizard forms.
* Added Export to PDF feature.
* Added application status `draft` for unfinished applications.
* Added Processes page for camunda web modeller.
* Added Form Adapter to support form submission data to other data stores than Mongo with custom data URLs.
* Added environment variable `MULTI_TENANCY_ENABLED`, `MT_ADMIN_BASE_URL`, `MT_ADMIN_BASE_URL_VERSION` to support multitenancy.
* Added environment variable `CUSTOM_SUBMISSION_URL`, `CUSTOM_SUBMISSION_ENABLED` for support form adapter.
* Added environment variables `DRAFT_ENABLED`, `DRAFT_POLLING_RATE` to manage draft feature. 
* Added environment variable `EXPORT_PDF_ENABLED`for pdf service.
* Added environment variable `PUBLIC_WORKFLOW_ENABLED` for enabling public workflow creation for multitenancy users.
* Added environment variable `DOCUMENT_SERVICE_URL`for document service.



**forms-flow-forms**

* Added new Repository , for more details checkout [here](https://github.com/AOT-Technologies/formio).
* Added environment variable `MULTI_TENANCY_ENABLED` to support mulitenancy.


**forms-flow-api**

* Added multi-tenancy support.
* Added support for default workflow with form.
* Added API support for `draft` feature.
* Added API support for `Form Adapter`.
* Added environment variable `MULTI_TENANCY_ENABLED`, `KEYCLOAK_ENABLE_CLIENT_AUTH` to support mulitenancy.
* Added new environment variable `FORMIO_JWT_SECRET`.

**forms-flow-bpm**

* Added default workflow.
* Added `Form Adapter` to support form submission data to other data stores than Mongo with custom data URLs.
* Added bpm gateway with jersey implementation.
* Added environment variable `MULTI_TENANCY_ENABLED`, `KEYCLOAK_ENABLE_CLIENT_AUTH`, `KEYCLOAK_WEB_CLIENTID`, `FORMSFLOW_ADMIN_URL` for multitenancy support.
* Added environment variable `CUSTOM_SUBMISSION_URL`, `CUSTOM_SUBMISSION_ENABLED` for support form adapter.



**forms-flow-documents**

* Added document API  to provide generate pdf with form submission data.
* Added environment variable `MULTI_TENANCY_ENABLED`, `KEYCLOAK_ENABLE_CLIENT_AUTH` to support mulitenancy .

**forms-flow-analytics**

* Added environment variable `REDASH_MULTI_ORG` to support multitenancy.



`Modified`

**forms-flow-web**

* Metrics page UI modified.
* Form page UI modified.
* Accessibility enhancement.
* service-worker updated.
* React build size optimized.

*Upgrade notes:*

* Environment variables modified `CAMUNDA_API_URL` to `BPM_API_URL`.
* Environment variables modified `REACT_APP_CAMUNDA_API_URI` to `REACT_APP_BPM_URL` in [config.sample.js](./forms-flow-web/public/config/config.sample.js)



**forms-flow-forms**

* Modified Docker-compose to point to create image from the [new Repository](https://github.com/AOT-Technologies/formio).

**forms-flow-api**

* Dependencies like utils, formio, JWT authentication moved to `forms-flow-api-utils`.
 
*Upgrade notes:*

* Environment variables modified ` BPM_API_BASE` to `BPM_API_URL`.


**forms-flow-bpm**

*Upgrade notes:*

* Camunda upgraded from 7.15 to 7.17.
* Java upgraded from  11 to 17.
* springboot upgraded from 2.4.8 to 2.6.4.
* camundaKeycloak upgraded from 2.2.1 to 2.2.3.
* camundaConnect upgraded from 7.15.0 to 1.5.0.
* camundaMail upgraded from 1.2.0 to 1.3.0.
* Environment variables modified `BPM_BASE_URL` to `BPM_API_URL`.
* formUrl parameter is changed to webFormUrl in DMN template.



`Removed`

**forms-flow-web**

* Removed View submissions button from reviewer form list and view submissions route.
* Removed the environment variables `CLIENT_ROLE_ID`, `DESIGNER_ROLE_ID`, `REVIEWER_ROLE_ID`,`ANONYMOUS_ID`, `USER_RESOURCE_ID`.
* Removed the environment variable `FORMIO_JWT_SECRET`.


`Generic Changes`

* Docker-compose files changed to single one.
* Added CI/CD pipeline.
* Environment variables updated with dynamic role-id fetching.
* Added new detailed documentation, checkout [here](https://aot-technologies.github.io/forms-flow-ai-doc).
## 4.0.6 - 2022-07-19

`Fixed`

**forms-flow-web**
* Fixed public form authentication check.

`Modified`

**forms-flow-data-analysis-api**

* Modified DataAnalysis API and Sentiment-analysis Jobs.

## 4.0.5 - 2022-04-19

`Added`

**forms-flow-web**

* Added `anonymous user` feature .
* Added count for Filter Tasks .
* Added form list page search and sort.
* Added new UI for task variable.
* Added form name as part of filename when downloaded.
* Added the status of the earlier version as inactive when a new version of the form is created/deleted.
* Added submitter name in the application history table.
* Added Cancel button for form edit.
* Added task variable in tasklist page at LHS.
* Added CD pipeline.

**forms-flow-api**

* Added public application create api for anonymous forms.
* Added migration scripts in the alembic file to resolve schema conflicts while db upgrade and downgrade, check out [here](./forms-flow-api/migrations/versions/80b8d5e95e9b_set_modification_date_on_create.py).
* Added new api for updating user locale attribute in Keycloak with the help of Keycloak admin API.
* Added form list page search and sort.
* Added CD pipeline.
* Added DB changes to accomodate task variable. 

**forms-flow-data-analysis-api**

* Added DataAnalysis API and Sentiment-analysis Jobs.

**forms-flow-idm**

* Added `manage-users` group to assigned client roles in realm-management.Check out the details at Service Accounts Tab from [here](./forms-flow-idm/keycloak/README.md#create-a-forms-flow-bpm-client).
* Added project specific custom login theme , check out the steps [here](./forms-flow-idm/keycloak/README.md#add-custom-login-theme).


**forms-flow-bpm**

* New (Task / Execution) Listener FormBpmFilteredDataPipelineListener Included for the effective form to bpm data copy.
* Added CD pipeline.

`Fixed`

**forms-flow-web**

* Uploaded forms cannot submit by client issue fixed .
* Application not getting in iOS issue fixed.
* Fixed process variable's data type in task filter.


**forms-flow-api**

* Postgres schema upgraded to enable updating the workflow after publising the form 
* Disabled internal workflows for  process API.

**forms-flow-bpm**

* Security context/authorization was not propogated to web-client while enabling asynchronous continutaion/intermediate timer events.
* Many minor performance optimizations and fixes are done.


`Modified`

**forms-flow-web**

* Modified application name search with lowercase and by intermediate search.
* Front-end support for the form process mapper versioning and database normalization.
* User is not be able to change the workflow of published form.
* Form Url support both pathname and formid to fetch the form.

**forms-flow-api**

* API support for application name search with lowercase and by intermediate search.
* Postgres database normalization and provided support for form process mapper versioning.

*Upgrade notes:*

`KEYCLOAK_BPM_CLIENT_SECRET` is not mandatory.
 Due to the architectural changes to the Postgres database, it is recommended to back up the data before the upgrade.

**forms-flow-bpm**

*Upgrade notes:*

`KEYCLOAK_BPM_CLIENT_SECRET` is not mandatory.


`Removed`

**forms-flow-web**

* Removed 'PDF' from display as option while creating form as designer.

**forms-flow-api**

*Upgrade notes:*

Environment variables `KEYCLOAK_ADMIN_USERNAME` and `KEYCLOAK_ADMIN_PASSWORD` are  removed since now the 
   admin APIs are accessed using the service account.
   
**forms-flow-bpm**

* FormAccessTokenCacheListener is deprecated ,will be removed from the codebase in the upcoming releases.
* formio-access-token.bpmn workflow is permanently removed from the codebase.

*Upgrade notes:*

* For the upgrading user's formio-access-token.bpmn workflow should be manually stopped and deleted using these instructions [from here](https://docs.camunda.org/manual/7.8/reference/rest/process-definition/delete-process-definition/).


`Generic Changes`

* Added docker based automated installation. For installation guide, check out [here](./deployment/docker/bundle).
* Existing users should build forms-flow-bpm,forms-flow-webapi and forms-flow-web together.

## 4.0.4 - 2021-12-27

`Added`

**forms-flow-bpm**

* Added test cases and code coverage.

*Upgrade notes:*

New environment variables `DATA_BUFFER_SIZE`, `IDENTITY_PROVIDER_MAX_RESULT_SIZE`.

**forms-flow-web**

* Admin page to map insights dashboards to keycloak groups.
* Added test cases and code coverage, check out the [details here](./forms-flow-web/README.md#code-coverage).

*Upgrade notes:*

New environment variables `FORMIO_JWT_SECRET`. It's highly recommended to change this environment variable for existing installations.

**forms-flow-api**

* Added `pagination`, `sorting` and `filtering` for Application Page.
* Added new APIs which acts as a gateway for calling forms-flow-analytics APIs.
* Added new API for modifying group details in Keycloak with the help of Keycloak admin APIs.
* Add application status list API.
* Added unit test cases and new script for CI operations.

*Upgrade notes:*

New environment variables `KEYCLOAK_ADMIN_USERNAME`, `KEYCLOAK_ADMIN_PASSWORD`, `INSIGHT_API_URL`, `INSIGHT_API_KEY`.


**forms-flow-analytics**

* Added Dashboard authorisation at Redash dashboard level.

**forms-flow-forms**

* Added indexes in Submission collection for applicationId, process_pid.
* Added authentication for publicly exposed urls.

*Upgrade notes:*

New environment variables `FORMIO_JWT_SECRET`. It's highly recommended to change this environment variable for existing installations.

**forms-flow-idm**

* Added new groups and mapper for Dashboard authorisation at Redash dashboard level.

*Upgrade notes:*

* To enable dashboards, and provide authorization the following changes are required in existing installations:

1. Create a new main group called `formsflow-analytics`, and create as many subgroups as you want to associate various dashboards from Admin UI(in Designer)
2. Create a new mapper under forms-flow-web client in Keycloak, by following below steps:

```
* Name = dashboard-mapper
* Mapper Type = User Attribute
* User Attribute = dashboards
* Token Claim Name = dashboards
* Add to ID Token = ON
* Add to access token = ON
* Add to userinfo = ON
* Multivalued = ON
* Aggregate attribute values = ON
* Click Save
```

3. Corresponding to each user, add the dashboard-groups you want to enable for dashboard authorization.
This will give users permission to as many dashboards which the group have been enabled with from Admin.

`Fixed`

**forms-flow-api**

* Fixed application metrics showing incorrect results by changing date to filtered based on timezone.

**forms-flow-bpm**

* Improved token creation logic using Oauth2RestTemplate.
* Code cleanup and optimization.

**forms-flow-web**

* Fixed total task count shown on the task LHS side and updated only after refreshing the page.
* Tasklist API updated.

`Modified`

**forms-flow-web**

*Upgrade notes:*

Removed environment variables `INSIGHT_API_URL`, `INSIGHT_API_KEY`

`Solution Component Upgrades`

**forms-flow-bpm**

* Camunda upgrade from `7.13.0` to `7.15.0`. 
* Upgraded springboot from `2.4.2` to `2.4.8`
* Upgraded spring-security-oauth2 from `2.4.2` to `2.4.8`

*Upgrade notes:*

After v4.0.4 version upgrade, Run the migrations with [upgrade file](./forms-flow-bpm/upgrade/process-engine_7.13_to_7.15.sql).

**forms-flow-analytics**

* Upgraded redash library to version from `9.0.0-beta` to `10.1.0`

*Upgrade notes:*

After v4.0.4 version upgrade, run the following command first to run the necessary migrations with the command:

```
docker-compose -f docker-compose-linux.yml run --rm server manage db upgrade
docker-compose -f docker-compose-linux.yml up --force-recreate --build
```
In case you want to downgrade to the v9.0-beta of forms-flow-analytics component after formsflow.ai version upgrade.
To update the migrations and rebuild formsflow.ai. Use [the below commands which was used in setup](./forms-flow-analytics/README.md/#running-the-application). 
Also note that we are not supporting downgrade to any version below Redash v9.0(which has be used from formsflow.ai v4.0 onwards).

**forms-flow-forms**

* Formio upgrade from `2.0.0-rc.34` to `2.3.0`.

`Known Issues`

* In case you are facing mongodb connection refused error for forms-flow-forms, downgrade to the next lowest mongo stable [version](https://docs.mongodb.com/manual/release-notes/)
* Consoles related to <http://localhost:3001/current> Api Failing. The console messages can be ignored. Please refer to [Issue-#106](https://github.com/AOT-Technologies/forms-flow-ai/issues/106) for more details.

## 4.0.3 - 2021-10-22

`Added`

**forms-flow-bpm**

* Added new postman collections for camunda API.
* Runtime logger level updation

**forms-flow-web**

* Added upload/download forms feature.
* Added a feature to search submissions in metrics based on created or modified date range.

**forms-flow-api**

* Better logging for Python API including coloured logs and API time details.
* Add pessimistic Database disconnection handling mechanism.

`Fixed`

**forms-flow-bpm**

* Fixed the issue of Oauth2 RestTemplate was recreating each time, so the session was getting created so many times.
* Exception handling & Retry for External form submission listener in ExternalFormSubmissionListener
* Usage issue fixed with ApplicationAuditListener.

**forms-flow-analytics**

* Resolve analytics component breaking due to [SIGSEV Memory issue](https://github.com/AOT-Technologies/forms-flow-ai/issues/149).

**forms-flow-web**

* Fixed server side pagination for `Task` page.
* Fixed Items per page dropdown in the form page for designer.

`Modified`

**forms-flow-bpm**

* Upgraded Camunda BPM Identity Keycloak to 2.2.1

**forms-flow-api**

* Add orderBy field to `metrics` API to display API based on created date and modified date.
* Changed default timezone to UTC time instead of being set as users local time.

**forms-flow-web**

* Footer was modified to display formsflow.ai with the version number.
* Optimized task list page by limiting the number of backend calls.

## 4.0.2 - 2021-07-23

`Added`

**forms-flow-bpm**

* Added task listener events as configurable one's in application property. New property added is websocket.messageEvents .

`Fixed`

**forms-flow-analytics**

* Fixed the issue of new datasource failing on creating.

**forms-flow-bpm**

* Approver action dropdown appearing on the clerk's task section once the approver returns the form is fixed for the `New Business License Application form`.

**forms-flow-idm**

* Removed additional parameters from the default configuration, which was causing keycloak import to fail in v11.0.

**forms-flow-web**

* Fixed in the `Tasks` section on completing a particular task, the task list is not being removed from LHS.
* Solution vulnerability fixes.
* Resolved the issue of form data is not being updated from cache on claiming the form.
* Identified & removed redundant calls on updating the task details.

`Modified`

**forms-flow-api**

* Rename Application Audit to Application History(without affecting database table).
* Removed Sentiment Analysis component and database, which will be separate micro-service in upcoming release.

**forms-flow-bpm**

* Refined the keycloak group query to improve API performance.
* Formio Access Token Cache (Internal) workflow is modified to start after deployment and added scripts for cleanup.

**forms-flow-web**

* Application status component created as a hidden element by default during form design.

`Generic Changes`

* Added gitter community

## 4.0.1 - 2021-07-13

`Added`

**forms-flow-api**

* Support for allowing CORS with multiple comma-separated origins.
* Added authorization on the application details page based on user roles.

**forms-flow-bpm**

* Added new workflows - `One-Step Approval Process` and `Two-Step Approval Process`.

**forms-flow-forms**

* Added new forms- `Create New Business License Application` and `Freedom of Information and Protection of Privacy`.

**forms-flow-web**

* Show/hide Application Menu based on keycloak group.
* Show/hide View Submissions button in form webpage based on keycloak group.
* Add 404 page.
* Add 403 page.

`Fixed`

**forms-flow-analytics**

* Fixed the failing installation of the analytics component.

**forms-flow-api**

* Fix application details API not displaying values to client users.
* Fixed the issue of not creating applications when called from the BPM side with process-instance-id.

**forms-flow-bpm**

* Fix done for authentication issue with Keycloak in the Keycloak configuration.
* Fix done for single result query fetching multiple record's during formio REST call.

**forms-flow-web**

* Resolve Last Modified column on the client Application page is not working.
* Fix Application search icons breaking.
* Resolve Mime type issue in the webpage.

`Modified`

**forms-flow-bpm**

* formio token generation cycle reduced from 24 hours to 3.50 Hours.
* Modified checked exception's on Listener services to Runtime exception.
* Modified application logging package to Camunda base package level.

**forms-flow-web**

* Modify WebSocket implementation to support reconnection in Task Menu.
* Footer was modified to display formsflow.ai with the version number.

`Generic Changes`

* Improved the README to document supported version for Keycloak.
* Updated [usage docs](./USAGE.md) with the latest form and workflow.
* v1.0.7 release for `camunda-formio-tasklist-vue`,a Vue.js-based package for easy integration of formsflow.ai to existing projects. To know more details checkout [formsflow-ai-extension repository](https://github.com/AOT-Technologies/forms-flow-ai-extensions/tree/master/camunda-formio-tasklist-vue)

`Known Issues`

* Consoles related to <http://localhost:3001/current> Api Failing. The console messages can be ignored. Please refer to [Issue-#106](https://github.com/AOT-Technologies/forms-flow-ai/issues/106) for more details.

## 4.0.0 - 2021-06-11

`Added`

* Added support for http calls which introduces the ability to make http calls across components for quicker and easier setup. Earlier versions required SSL support which required a lot of time and effort to setup, with a need for Keycloak server with SSL support.
* User can *claim/view* the Tasklist in realtime. It provides live updates to tasks, allowing teams to collaborate on a single task list in real time. Used websockets support under the hood to make real time communication(component: forms-flow-web, forms-flow-bpm)
* Automated installation steps for keycloak setup. It provides a bundled, pre-configured keycloak package for a local setup to simplify the installation process
* Automated manual steps for resource id generation, included batch and shell scripts to simplify the process.
* New UI for formsflow.ai based on Vue.js for easy integration of formsflow.ai to existing projects. To know more details checkout [formsflow-ai-extension repository](https://github.com/AOT-Technologies/forms-flow-ai-extensions/tree/master/camunda-formio-tasklist-vue) and to install our [NPM package go here](https://www.npmjs.com/package/camunda-formio-tasklist-vue).(component: forms-flow-ai-extensions)
* New API for health check has been included. (component : forms-flow-api)
* Added confirmation messages to notify the users on save actions. (component: forms-flow-web)
* Users can click on External shared links (eg. from email) to get redirected to a particular task/submission/form if the user has right permissions. (component: forms-flow-web)
* Claiming of tasks are restricted to users belonging to reviewer group(formsflow/formsflow-reviewer) of keycloak.(component: forms-flow-web)
* Application/Submission view for client role users are restricted to own submission view.(component: forms-flow-bpm, forms-flow-web)
* Added Semantic UI css for forms design (component: forms-flow-web)
* Listeners are well-documented with information on purpose, how-it-works and how-to-use (component : forms-flow-bpm) [Link](./forms-flow-bpm/starter-examples/listeners/listeners-readme.md)
* Support to associate an unique form at every manual task in workflow process (Component: forms-flow-bpm)

`Modified`

* Task dashboard has been revamped with new look and feel- which would allow more control on data and stream updates.
* Enhanced Form Process Mapper API and Application API endpoints (component : forms-flow-api)
* Improved exception handling of python to provide meaningful error messages (component : forms-flow-api)
* Improved README for better readability and easy installation.
* The Task menu has been moved to Header section. In Task Section, filters are available in the main menu and a new Dashboard section has been added which includes metrics and Insights. (component: forms-flow-web)
* Dynamic property to set Application Name and logo in the header. (component: forms-flow-web)
* Default route for user having reviewer role is pointed to tasks page and that of client/designer is to forms page.(component: forms-flow-web)
* Removed *edit/delete* submission buttons from submission list view of reviewers.

`Fixed`

* Cosmetic changes to show success message after loading is completed.
* Custom component (Text Area with analytics) not retaining the value after submission. (component: forms-flow-forms)
* UI layout fixes (component: forms-flow-web)

`Solution Component Upgrades`

* React library upgraded to latest version-17.0.2 and fixed security vulnerabilities (Component : forms-flow-web)
* Spring boot upgraded to latest version-2.4.2 (Component : forms-flow-bpm)
* Redash upgraded to latest version:v9 (component : forms-flow-analytics)
* Fixed Python security vulnerabilities and updated flask to 1.1.4 version (component : forms-flow-api)
* Fixed Form.io security vulnerabilities. (component : forms-flow-forms)

`Known Issues`

* Consoles related to <http://localhost:3001/current> Api Failing. The console messages can be ignored. Please refer to [Issue-#106](https://github.com/AOT-Technologies/forms-flow-ai/issues/106) for more details.

## 3.1.0 - 2020-12-17

`Modified`

* Formio upgraded to latest version-2.0.0.rc34 (Component : forms-flow-forms)
* In application & task dashboard, the process diagram navigation is highlighted on the diagram (Component : forms-flow-web)
* Made cosmetic changes to menu icons (Component: forms-flow-web)
* Update on swagger documentation (Component: forms-flow-api)
* For the designer's edit scenario, by default the workflow selection & association is rendered as read-only with an option to toggle and edit(Component: forms-flow-web)

`Untested Features`

* Support to associate an unique form at every manual task in workflow process (Component: forms-flow-bpm)

`Fixed`

* Support to access forms-flow-ai solution in mobile(Component: forms-flow-web)
* Forms flow Edit/submission Routing Fix for User with Multiple Role (Component: forms-flow-web)

`Upcoming Features`

* Refactoring python api to use module *flask-resk-jsonapi* (Component: forms-flow-api)
* Enhanced sorting, searching and pagination  (Component: forms-flow-web)

`Known Issues`

* Custom component (Text Area with analytics) not retaining the value after submission
* Cosmetic changes to show success message after loading is completed

## 3.0.1 - 2020-10-08

`Modified`

* In application dashboard, the "Application Status" column search component has been enhanced to show all possible values in dropdown (Component : forms-flow-web)
* In application dashboard, the button label has been modified to show as "Acknowledge" for status "Awaiting Acknowledgement" (Component : forms-flow-web)

## 3.0.0 - 2020-10-07

`Added`

* Logo & UI Styling
* Introduced Applications menu
* Versioning of form submissions
* Task menu - Process Diagram, Application History
* UI for configuration of forms with workflow (Designer)
* Custom component `Text Area with analytics` (with configurable topics)
* Sentiment analysis API using nltk and spacy

`Known Issues`

* Custom component (Text Area with analytics) not retaining the value after submission
* Cosmetic changes to show success message after loading is completed

## 2.0.1 - 2020-07-27

`Added`

* This file (CHANGELOG.md)
* CONTRIBUTING.md

## 2.0.0 - 2020-07-24

`Added`

* ReDash implementation under forms-flow-analytics
* Deployment folder with docker and nginx
* formsflow.ai UI task dashboard
* formsflow.ai UI metrics dashboard
* Single component installations with docker and docker-compose
* Native windows intallation docker-compose-windows.yml  
* Native Linux installation docker-compose-linux.yml

`Removed`

* forms-flow-db folder

`Changed`

* All README.md files cleaned up throughout project
* Environment variables rationalised and renamed to be globally generic

## 1.0.0 - 2020-04-15

`Added`

* Initial release
