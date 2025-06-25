import React from "react";
import { useDispatch } from "react-redux";
import { setDraftDelete } from "../../actions/draftActions";
import { useTranslation } from "react-i18next";
import PropTypes from "prop-types";

const DraftOperations = ({ row }) => {  
  const dispatch = useDispatch();
  const { t } = useTranslation();
  const deleteDraft = () => {
    dispatch(
      setDraftDelete({
        modalOpen: true,
        draftId: row.id,
        draftName: row.applicationName,
      })
    );
  };

  return (
    <>
      <div>
        <span className="ms-2">
          <span>
            <button
              data-testid={`draft-delete-button-${row.id}`}
              className="btn btn-link text-danger mt-2"
              onClick={() => deleteDraft()}
            >
              {t("Delete Draft")}
            </button>
            &nbsp;
          </span>
        </span>
      </div>
    </>
  );
};

DraftOperations.propTypes = {
  row: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    applicationName: PropTypes.string.isRequired,
  }).isRequired,
};

export default DraftOperations;
