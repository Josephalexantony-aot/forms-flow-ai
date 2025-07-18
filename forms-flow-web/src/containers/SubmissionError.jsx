import React from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import { useTranslation } from "react-i18next";

const SubmissionError = React.memo((props) => {
  const { modalOpen = false, onConfirm, message } = props;
  const { t } = useTranslation();
  return (
    <>
      <Modal show={modalOpen}>
        <Modal.Header>
          <Modal.Title><p>Error</p></Modal.Title>
        </Modal.Header>
        <Modal.Body>{message}</Modal.Body>
        <Modal.Footer>
          <div className="buttons-row">
            <Button type="button" className="btn btn-default" onClick={onConfirm}>
              {t("Ok")}
            </Button>
          </div>
        </Modal.Footer>
      </Modal>
    </>
  );
});

export default SubmissionError;
