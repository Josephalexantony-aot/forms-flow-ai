import React, { useCallback, useEffect, useState } from "react";
import { Card, Col, Row, Tab, Tabs } from "react-bootstrap";
import {
  reloadTaskFormSubmission,
  setBPMTaskDetailLoader,
  setSelectedTaskID,
} from "../../../actions/bpmTaskActions";
import {
  fetchServiceTaskList,
  getBPMGroups,
  getBPMTaskDetail,
  onBPMTaskFormSubmit,
} from "../../../apiManager/services/bpmTaskServices";
import { useDispatch, useSelector } from "react-redux";
import Loading from "../../../containers/Loading";
import ProcessDiagram from "../../BPMN/ProcessDiagramHook";
import {
  getFormIdSubmissionIdFromURL,
  getFormUrlWithFormIdSubmissionId,
  getProcessDataObjectFromList,
} from "../../../apiManager/services/formatterService";
import History from "../../Application/ApplicationHistory";
import FormEdit from "../../../routes/Submit/Submission/Item/Edit";
import FormView from "../../../routes/Submit/Submission/Item/View";
import LoadingOverlay from "react-loading-overlay-ts";
import { getForm, getSubmission, Formio, resetSubmission } from "@aot-technologies/formio-react";
import { CUSTOM_EVENT_TYPE } from "../constants/customEventTypes";
import { getTaskSubmitFormReq } from "../../../apiManager/services/bpmServices";
import { useParams } from "react-router-dom";
import { push } from "connected-react-router";
import {
  resetFormData,
  setFormSubmissionLoading,
} from "../../../actions/formActions";
import { useTranslation } from "react-i18next";
import {
  CUSTOM_SUBMISSION_URL,
  CUSTOM_SUBMISSION_ENABLE,
  MULTITENANCY_ENABLED,
} from "../../../constants/constants";
import { getCustomSubmission } from "../../../apiManager/services/FormServices";
import { getFormioRoleIds } from "../../../apiManager/services/userservices";
import  NoTaskSelectedMessage  from "../../../components/ServiceFlow/NoTaskSelected";

import { bpmActionError } from "../../../actions/bpmTaskActions";
import { setCustomSubmission } from "../../../actions/checkListActions";
import TaskHeaderListView from "./TaskHeaderListView";
const ServiceFlowTaskDetails = React.memo(() => {
  const { t } = useTranslation();
  const { taskId } = useParams();
  const bpmTaskId = useSelector((state) => state.bpmTasks.taskId);
  const task = useSelector((state) => state.bpmTasks.taskDetail);
  const processList = useSelector((state) => state.bpmTasks.processList);
  const isTaskLoading = useSelector(
    (state) => state.bpmTasks.isTaskDetailLoading
  );
  const isTaskUpdating = useSelector(
    (state) => state.bpmTasks.isTaskDetailUpdating
  );
  const reqData = useSelector((state) => state.bpmTasks.listReqParams);
  const taskFormSubmissionReload = useSelector(
    (state) => state.bpmTasks.taskFormSubmissionReload
  );
  const dispatch = useDispatch();
  const currentUser = useSelector(
    (state) => state.user?.userDetail?.preferred_username || ""
  );
  const selectedFilter = useSelector((state) => state.bpmTasks.selectedFilter);
  const firstResult = useSelector((state) => state.bpmTasks.firstResult);
  const [processKey, setProcessKey] = useState("");
  const [processTenant, setProcessTenant] = useState(null);
  const [processInstanceId, setProcessInstanceId] = useState("");
  const tenantKey = useSelector((state) => state.tenants?.tenantId);
  const redirectUrl = MULTITENANCY_ENABLED ? `/tenant/${tenantKey}/` : "/";
  const error = useSelector((state) => state.bpmTasks.error);


  useEffect(() => {
    if (taskId) {
      dispatch(setSelectedTaskID(taskId));
    }
  }, [taskId, dispatch]);

  useEffect(() => {
    if (bpmTaskId) {
      dispatch(setBPMTaskDetailLoader(true));
      dispatch(getBPMTaskDetail(bpmTaskId));
      dispatch(getBPMGroups(bpmTaskId));
    }
    return () => {
      Formio.clearCache();
    };
  }, [bpmTaskId, dispatch]);

  useEffect(() => {
    if (error) {
      dispatch(push('/404'));
    }
    return () => {
      dispatch(bpmActionError(''));
    };
  }, [error,dispatch]);

  useEffect(() => {
    if (processList.length && task?.processDefinitionId) {
      const pKey = getProcessDataObjectFromList(
        processList,
        task?.processDefinitionId
      );
      setProcessKey(pKey["key"]);
      setProcessTenant(pKey["tenantId"]);
    }
  }, [processList, task?.processDefinitionId]);

  useEffect(() => {
    if (task?.processInstanceId) {
      setProcessInstanceId(task?.processInstanceId);
    }
  }, [task?.processInstanceId]);

  const getFormSubmissionData = useCallback(
    (formUrl) => {
      const { formId, submissionId } = getFormIdSubmissionIdFromURL(formUrl);
      Formio.clearCache();
      dispatch(resetFormData("form"));
      function fetchForm() {
        dispatch(
          getForm("form", formId, (err) => {
            if (!err) {
              if (CUSTOM_SUBMISSION_URL && CUSTOM_SUBMISSION_ENABLE) {
                dispatch(setCustomSubmission({}));
                dispatch(getCustomSubmission(submissionId, formId));
              } else {
                dispatch(resetSubmission("submission"));
                dispatch(getSubmission("submission", submissionId, formId));
              }
              dispatch(setFormSubmissionLoading(false));
            } else {
              if (err === "Bad Token" || err === "Token Expired") {
                dispatch(resetFormData("form"));
                dispatch(
                  getFormioRoleIds((err) => {
                    if (!err) {
                      fetchForm();
                    } else {
                      dispatch(setFormSubmissionLoading(false));
                    }
                  })
                );
              } else {
                dispatch(setFormSubmissionLoading(false));
              }
            }
          })
        );
      }
      fetchForm();
    },
    [dispatch]
  );

  useEffect(() => {
    if (task?.formUrl) {
      getFormSubmissionData(task?.formUrl);
    }
  }, [task?.formUrl, dispatch, getFormSubmissionData]);

  useEffect(() => {
    if (task?.formUrl && taskFormSubmissionReload) {
      dispatch(setFormSubmissionLoading(false));
      getFormSubmissionData(task?.formUrl);
      dispatch(reloadTaskFormSubmission(false));
    }
  }, [
    task?.formUrl,
    taskFormSubmissionReload,
    dispatch,
    getFormSubmissionData,
  ]);

  const reloadTasks = () => {
    dispatch(setBPMTaskDetailLoader(true));
    dispatch(setSelectedTaskID(null)); // unSelect the Task Selected
    dispatch(fetchServiceTaskList(reqData,null,firstResult)); //Refreshes the Tasks
    dispatch(push(`${redirectUrl}task-old/`));
  };

  const reloadCurrentTask = () => {
    if (selectedFilter && task?.id) {
      dispatch(setBPMTaskDetailLoader(true));
      dispatch(
        getBPMTaskDetail(task.id, (err, taskDetail) => {
          if (!err) {
            dispatch(setFormSubmissionLoading(true));
            getFormSubmissionData(taskDetail?.formUrl);
          }
        })
      ); // Refresh the Task Selected
      dispatch(getBPMGroups(task.id));
      dispatch(fetchServiceTaskList(reqData,null,firstResult)); //Refreshes the Tasks

    }
  };

  const onCustomEventCallBack = (customEvent) => {
    switch (customEvent.type) {
      case CUSTOM_EVENT_TYPE.RELOAD_TASKS:
        reloadTasks();
        break;
      case CUSTOM_EVENT_TYPE.RELOAD_CURRENT_TASK:
        reloadCurrentTask();
        break;
      case CUSTOM_EVENT_TYPE.ACTION_COMPLETE:
        onFormSubmitCallback(customEvent.actionType);
        break;
      default:
        return;
    }
  };

  const onFormSubmitCallback = (actionType = "") => {
    if (bpmTaskId) {
      dispatch(setBPMTaskDetailLoader(true));
      const { formId, submissionId } = getFormIdSubmissionIdFromURL(
        task?.formUrl
      );
      const formUrl = getFormUrlWithFormIdSubmissionId(formId, submissionId);
      const origin = `${window.location.origin}${redirectUrl}`;
      const webFormUrl = `${origin}form/${formId}/submission/${submissionId}`;
      dispatch(
        onBPMTaskFormSubmit(
          bpmTaskId,
          getTaskSubmitFormReq(
            formUrl,
            task?.applicationId,
            actionType,
            webFormUrl
          ),
          (err) => {
            if (!err) {
              reloadTasks();
            } else {
              dispatch(setBPMTaskDetailLoader(false));
            }
          }
        )
      );
    } else {
      reloadCurrentTask();
    }
  };

  if (!bpmTaskId) {
    return (
      <NoTaskSelectedMessage />
    );
  } else if (isTaskLoading) {
    return (
      <div className="service-task-details">
        <Loading />
      </div>
    );
  } else {
    /*TODO split render*/
    return (
      <div className="service-task-details">
        <LoadingOverlay active={isTaskUpdating} spinner text={t("Loading...")}>
        <Card className="me-2 bg-light">
                        <Card.Body>
                            <div className="d-flex justify-content-between">
                            <Col>
                                    <Row className="ms-0 task-header">{task?.name}</Row>
                                    <Row className="ms-0 fs-5 fw-normal">
                                        <span className="application-id" title={t("Flow")} style={{wordBreak:"break-all"}}>
                                            {" "}
                                            {
                                                getProcessDataObjectFromList(processList,
                                                    task?.processDefinitionId)
                                                    ?.name
                                            }
                                        </span>
                                    </Row>
                                    <Row className="ms-0">
                                        <span title={t("Submission Id")} className="application-id">
                                            {t("Submission Id")}# {task?.applicationId}
                                        </span>
                                    </Row>
                                    <Row className="ms-0 me-0 mt-3 justify-content-around">
                                    <TaskHeaderListView
                                        task={task} taskId={task?.id} groupView={true}
                                    />
                                    </Row>
                                </Col>
                           </div>
                        </Card.Body>
                    </Card>   
          <Tabs defaultActiveKey="form" id="service-task-details" mountOnEnter>
          
            <Tab eventKey="form" title={t("Form")}>
              <LoadingOverlay
                active={task?.assignee !== currentUser}
                spinner={false}
                styles={{
                  overlay: (base) => ({
                    ...base,
                    background: "rgba(0, 0, 0, 0.2)",
                    cursor: "not-allowed !important",
                  }),
                }}
              >
                {task?.assignee === currentUser ? (
                  <FormEdit
                    onFormSubmit={onFormSubmitCallback}
                    onCustomEvent={onCustomEventCallBack}
                  />
                ) : (
                  <FormView showPrintButton={false} />
                )}
              </LoadingOverlay>
            </Tab>
            <Tab eventKey="history" title={t("History")}>
              <History applicationId={task?.applicationId} />
            </Tab>
            <Tab eventKey="diagram" title={t("Diagram")}>
              <div>
                <ProcessDiagram
                  processKey={processKey}
                  processInstanceId={processInstanceId}
                  tenant={processTenant}
                  // markers={processActivityList}
                />
              </div>
            </Tab>
          </Tabs>
        </LoadingOverlay>
      </div>
    );
  }
});

export default ServiceFlowTaskDetails;
