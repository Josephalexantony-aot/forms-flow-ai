import React from "react";
import Modal from "react-bootstrap/Modal";
import { useTranslation } from "react-i18next";

const MessageModal = React.memo((props) => {
    const { t } = useTranslation();
    const {
        modalTitle = null,
        modalOpen = false,
        message,
        onNo,
    } = props;

    return (
        <>
            <Modal data-testid="Warning-modal" show={modalOpen}>
                <Modal.Header>
                    <p>
                        <Modal.Title id="example-custom-modal-styling-title warning">
                            {modalTitle}
                        </Modal.Title>
                    </p>
                </Modal.Header>
                <Modal.Body>{message}</Modal.Body>
                <Modal.Footer>
                    <div className="buttons-row">
                        <button
                            type="button"
                            className="btn btn-primary"
                            data-testid="ok-button"
                            onClick={onNo}>
                            {t("Ok")}
                        </button>
                    </div>
                </Modal.Footer>
            </Modal>
        </>
    );
});

export default MessageModal;
