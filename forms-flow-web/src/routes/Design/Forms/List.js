import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { connect, useSelector, useDispatch } from "react-redux";
import CreateFormModal from "../../../components/Modals/CreateFormModal.js";
import { toast } from "react-toastify";
import { addTenantkey } from "../../../helper/helper";
import {
  selectRoot,
  deleteForm,
} from "@aot-technologies/formio-react";
import Loading from "../../../containers/Loading";
import { MULTITENANCY_ENABLED, MAX_FILE_SIZE } from "../../../constants/constants";
import {
  setBPMFormListLoading,
  setFormDeleteStatus,
  setBpmFormSearch,
  setBPMFormListPage,
  setBpmFormSort,
  setFormSuccessData
} from "../../../actions/formActions";
import { fetchBPMFormList } from "../../../apiManager/services/bpmFormServices";
import {
  setFormCheckList,
  setFormSearchLoading,
} from "../../../actions/checkListActions";
import { useTranslation, Translation } from "react-i18next";
import { unPublishForm } from "../../../apiManager/services/processServices";
import FormTable from "./../../../components/Form/constants/FormTable.js";
import ClientTable from "./../../../components/Form/constants/ClientTable";
import _ from "lodash";
import _camelCase from "lodash/camelCase";
import {
  formCreate,
  formImport,
  validateFormName,
} from "../../../apiManager/services/FormServices";
import userRoles from "../../../constants/permissions.js";
import FileService from "../../../services/FileService";
import {
  FormBuilderModal,
  ImportModal,
  CustomSearch,
  CustomButton,
  useSuccessCountdown
} from "@formsflow/components";
import { HelperServices } from '@formsflow/service';
import { useMutation } from "react-query";
import { addHiddenApplicationComponent } from "../../../constants/applicationComponent";
import { navigateToDesignFormEdit } from "../../../helper/routerHelper.js";
import FilterSortActions from "../../../components/CustomComponents/FilterSortActions.js";

const List = React.memo((props) => {
  const { createDesigns, createSubmissions, viewDesigns } = userRoles();
  const { t } = useTranslation();
  const searchText = useSelector((state) => state.bpmForms.searchText);
  const tenantKey = useSelector((state) => state.tenants?.tenantId);
  const [search, setSearch] = useState(searchText || "");
  const [showBuildForm, setShowBuildForm] = useState(false);
  const [importFormModal, setImportFormModal] = useState(false);
  const [importError, setImportError] = useState("");
  const [importLoader, setImportLoader] = useState(false);
  const [showSortModal, setShowSortModal] = useState(false);
  const { successState, startSuccessCountdown } = useSuccessCountdown();


  const handleFilterIconClick = () => {
    setShowSortModal(true); // Open the SortModal
  };

  const handleSortModalClose = () => {
    setShowSortModal(false); // Close the SortModal
  };

  const handleSortApply = (selectedSortOption, selectedSortOrder) => {
    
    const resetSortOrders = HelperServices.getResetSortOrders(optionSortBy);
    dispatch(
      setBpmFormSort({
        ...resetSortOrders,
        activeKey: selectedSortOption,
        [selectedSortOption]: { sortOrder: selectedSortOrder },
      })
    );
    setShowSortModal(false);
  };

  const ActionType = {
    BUILD: "BUILD",
    IMPORT: "IMPORT",
  };

  const UploadActionType = {
    IMPORT: "import",
    VALIDATE: "validate",
  };

  const [nameError, setNameError] = useState("");
  const dispatch = useDispatch();
  const submissionAccess = useSelector(
    (state) => state.user?.submissionAccess || []
  );

  const [formSubmitted, setFormSubmitted] = useState(false);

  /* --------- validate form title exist or not --------- */
  const {
    mutate: validateFormTitle, // this function will trigger the API call
    isLoading: validationLoading,
    // isError: error,
  } = useMutation(({ title }) => validateFormName(title), {
    onSuccess: ({ data }, { createButtonClicked, ...variables }) => {
      if (data && data.code === "FORM_EXISTS") {
        setNameError(data.message); // Set exact error message
      } else {
        setNameError("");
        // if the modal clicked createButton, need to call handleBuild
        if (createButtonClicked) {
          handleBuild(variables);
        }
      }
    },
    onError: (error) => {
      const errorMessage =
        error?.response?.data?.message ||
        "An error occurred while validating the form name.";
      setNameError(errorMessage); // Set the error message from the server
    },
  });

  useEffect(() => {
    setSearch(searchText);
  }, [searchText]);

  useEffect(() => {
    if (!search?.trim()) {
      dispatch(setBpmFormSearch(""));
    }
  }, [search]);
  const handleSearch = () => {
    dispatch(setBpmFormSearch(search));
    dispatch(setBPMFormListPage(1));
  };
  const handleClearSearch = () => {
    setSearch("");
    dispatch(setBpmFormSearch(""));
  };
  const { forms, getFormsInit } = props;
  const isBPMFormListLoading = useSelector((state) => state.bpmForms.isActive);
  const designerFormLoading = useSelector(
    (state) => state.formCheckList.designerFormLoading
  );

  const pageNo = useSelector((state) => state.bpmForms.formListPage);
  const limit = useSelector((state) => state.bpmForms.limit);
  const formSort = useSelector((state) => state.bpmForms.sort);
  const formAccess = useSelector((state) => state.user?.formAccess || []);
  const searchFormLoading = useSelector(
    (state) => state.formCheckList.searchFormLoading
  );
  const [newFormModal, setNewFormModal] = useState(false);
  const [description, setDescription] = useState("");
  const [formTitle, setFormTitle] = useState("");
  const  optionSortBy = [
    { value: "formName", label: t("Form Name") },
    { value: "visibility", label: t("Visibility") },
    { value: "status", label: t("Status") },
    { value: "modified", label: t("Last Edited") },
  ];
  useEffect(() => {
    dispatch(setFormCheckList([]));
  }, [dispatch]);

  useEffect(() => {
    dispatch(setBPMFormListLoading(true));
  }, []);

  const fetchForms = () => {
    let filters = {pageNo, limit, formSort, formName:searchText};
    dispatch(setFormSearchLoading(true));
    dispatch(fetchBPMFormList({...filters}));
  };
  const onClose = () => {
    setNewFormModal(false);
  };
  const onCloseimportModal = () => {
    setImportError("");
    setImportFormModal(false);
  };
  const onCloseBuildModal = () => {
    setShowBuildForm(false);
    setNameError("");
    setFormSubmitted(false);
  };
  const handleAction = (actionType) => {
    switch (actionType) {
      case ActionType.BUILD:
        setShowBuildForm(true);
        break;
      case ActionType.IMPORT:
        setImportFormModal(true);
        break;
    }
    onClose();
  };

  const handleImport = async (fileContent, actionType) => {

    if (fileContent.size > MAX_FILE_SIZE) {
      setImportError(
        `File size exceeds the ${
          MAX_FILE_SIZE / (1024 * 1024)
        }MB limit. Please upload a smaller file.`
      );
      return;
    }

    let data;
    if (
      [UploadActionType.VALIDATE, UploadActionType.IMPORT].includes(actionType)
    ) {
      data = { importType: "new", action: actionType };
    } else {
      console.error("Invalid UploadActionType provided");
      return;
    }

    if (actionType === UploadActionType.IMPORT) {
      setImportLoader(true);
      setFormSubmitted(true);
    }

    try {
      const dataString = JSON.stringify(data);
      const res = await formImport(fileContent, dataString);
      const { data: responseData } = res;
      const formId = responseData.mapper?.formId;

      setImportLoader(false);
      setFormSubmitted(false);

      if (actionType === UploadActionType.VALIDATE) {
        const formExtracted = await FileService.extractFileDetails(fileContent);

        if (Array.isArray(formExtracted?.forms)) {
          setFormTitle(formExtracted?.forms[0]?.formTitle || "");
          setDescription(
            formExtracted?.forms[0]?.formDescription || ""
          );
        }
      } else if (formId) {
        navigateToDesignFormEdit(dispatch, tenantKey, formId);
      }
    } catch (err) {
      setImportLoader(false);
      setFormSubmitted(false);
      setImportError(err?.response?.data?.message);
    }
  };

  useEffect(() => {
    fetchForms();
  }, [
    getFormsInit,
    dispatch,
    createDesigns,
    pageNo,
    limit,
    formSort,
    searchText,
  ]);

  const validateForm = ({ title }) => {
    if (!title || title.trim() === "") {
      return "This field is required";
    }
    return null;
  };

  const validateFormNameOnBlur = ({ title, ...rest }) => {
    //the reset variable contain title, description, display  also sign for clicked in create button
    const error = validateForm({ title });

    if (error) {
      setNameError(error);
      return;
    }
    validateFormTitle({ title, ...rest });
  };

  const handleBuild = ({ description, display, title }) => {
    setFormSubmitted(true);
    const error = validateForm({ title });
    if (error) {
      setNameError(error);
      return;
    }
    const name = _camelCase(title);
    const newForm = {
      display,
      tags: ["common"],
      submissionAccess: submissionAccess,
      componentChanged: true,
      newVersion: true,
      components: [],
      access: formAccess,
      title,
      name,
      description,
      path: name.toLowerCase(),
    };
    newForm.components = addHiddenApplicationComponent(newForm).components;

    if (MULTITENANCY_ENABLED && tenantKey) {
      newForm.tenantKey = tenantKey;
      newForm.path = addTenantkey(newForm.path, tenantKey);
      newForm.name = addTenantkey(newForm.name, tenantKey);
    }
    formCreate(newForm)
      .then((res) => {
        const form = res.data;
        dispatch(setFormSuccessData("form", form));
        startSuccessCountdown(() => {
          navigateToDesignFormEdit(dispatch, tenantKey, form._id);
        },2);
      })
      .catch((err) => {
        let error;
        if (err.response?.data) {
          error = err.response.data;
          console.log(error);
          setNameError(error?.errors?.name?.message);
        } else {
          error = err.message;
          setNameError(error?.errors?.name?.message);
        }
      })
      .finally(() => {
        setFormSubmitted(false);
      });
  };

  const handleRefresh = () => {
  fetchForms();
  };
  const renderTable = () => {
    if (createDesigns || viewDesigns) {
      return <FormTable />;
    }
    if (createSubmissions) {
      return <ClientTable />;
    }
    return null;
  };


  return (
    <>
      {(forms?.isActive || designerFormLoading || isBPMFormListLoading) &&
      !searchFormLoading ? (
        <div data-testid="Form-list-component-loader">
          <Loading />
        </div>
      ) : (
        <>
          {(
              <div className="table-bar">
                <div className="filters">
                  <CustomSearch
                    search={search}
                    setSearch={setSearch}
                    handleSearch={handleSearch}
                    handleClearSearch={handleClearSearch}
                    placeholder={t("Search Form Name and Description")}
                    searchLoading={searchFormLoading}
                    title={t("Search Form Name and Description")}
                    dataTestId="form-search-input"
                  />
                </div>
                <div className="actions">
                  <FilterSortActions
                    showSortModal={showSortModal}
                    handleFilterIconClick={handleFilterIconClick}
                    handleRefresh={handleRefresh}
                    handleSortModalClose={handleSortModalClose}
                    handleSortApply={handleSortApply}
                    optionSortBy={optionSortBy}
                    defaultSortOption={formSort.activeKey}
                    defaultSortOrder={formSort[formSort.activeKey]?.sortOrder || "asc"}
                    filterDataTestId="form-list-filter"
                    filterAriaLabel="Filter the form list"
                    refreshDataTestId="form-list-refresh"
                    refreshAriaLabel="Refresh the form list"
                  />

                  {createDesigns && (
                    <CustomButton
                      label={t("New Form & Flow")}
                      onClick={() => setNewFormModal(true)}
                      dataTestId="create-form-button"
                      ariaLabel="Create Form"
                      action
                    />
                  )}
                  <CreateFormModal
                    newFormModal={newFormModal}
                    actionType={ActionType}
                    onClose={onClose}
                    onAction={handleAction}
                  />
                  <FormBuilderModal
                    modalHeader={t("Build New Form")}
                    nameLabel={t("Form Name")}
                    descriptionLabel={t("Form Description")}
                    showBuildForm={showBuildForm}
                    isSaveBtnLoading={formSubmitted}
                    isFormNameValidating={validationLoading}
                    onClose={onCloseBuildModal}
                    onAction={handleAction}
                    primaryBtnAction={handleBuild}
                    setNameError={setNameError}
                    nameValidationOnBlur={validateFormNameOnBlur}
                    nameError={nameError}
                    buildForm={true}
                    showSuccess={successState?.showSuccess} // ✅ Pass success state
                    successCountdown={successState?.countdown} // ✅ Pass countdown
                  />
                  {importFormModal && (
                    <ImportModal
                      importLoader={importLoader}
                      importError={importError}
                      showModal={importFormModal}
                      uploadActionType={UploadActionType}
                      formName={formTitle}
                      formSubmitted={formSubmitted}
                      description={description}
                      onClose={onCloseimportModal}
                      handleImport={handleImport}
                      headerText={t("Import New Form")}
                      primaryButtonText={t("Confirm and Edit Form")}
                      fileType=".json"
                    />
                  )}
                </div>
              </div>
          )}
         {renderTable()}
        </>
      )}
    </>
  );
});
List.propTypes = {
  forms: PropTypes.object,
  getFormsInit: PropTypes.bool,
};
const mapStateToProps = (state) => {
  return {
    forms: selectRoot("forms", state),
    userRoles: selectRoot("user", state).roles || [],
    modalOpen: selectRoot("formDelete", state).formDelete.modalOpen,
    formId: selectRoot("formDelete", state).formDelete.formId,
    formName: selectRoot("formDelete", state).formDelete.formName,
    isFormWorkflowSaved: selectRoot("formDelete", state).isFormWorkflowSaved,
    tenants: selectRoot("tenants", state),
    path: selectRoot("formDelete", state)?.formDelete.path,
  };
};

// eslint-disable-next-line no-unused-vars
const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onYes: (
      e,
      formId,
      formProcessData,
      formCheckList,
      applicationCount,
      fetchForms
    ) => {
      e.currentTarget.disabled = true;
      if (!applicationCount) {
        dispatch(deleteForm("form", formId));
      }
      if (formProcessData.id) {
        dispatch(
          unPublishForm(formProcessData.id, (err) => {
            if (err) {
              toast.error(
                <Translation>
                  {(t) =>
                    t(
                      `${_.capitalize(
                        formProcessData?.formType
                      )} deletion unsuccessful`
                    )
                  }
                </Translation>
              );
            } else {
              toast.success(
                <Translation>
                  {(t) =>
                    t(
                      `${_.capitalize(
                        formProcessData?.formType
                      )} deleted successfully`
                    )
                  }
                </Translation>
              );
              const newFormCheckList = formCheckList.filter(
                (i) => i.formId !== formId
              );
              dispatch(setFormCheckList(newFormCheckList));
            }
            fetchForms();
          })
        );
      }
      const formDetails = {
        modalOpen: false,
        formId: "",
        formName: "",
      };
      dispatch(setFormDeleteStatus(formDetails));
    },
    onNo: () => {
      const formDetails = { modalOpen: false, formId: "", formName: "" };
      dispatch(setFormDeleteStatus(formDetails));
    },
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(List);
