import React from "react";
import NoFilterSelectedImage from "./undraw_to_do_re_jaef.svg";
import { Translation } from "react-i18next";

function NoTaskSelectedMessage() {
  return (
    <div className="d-flex flex-column h-100 align-items-center justify-content-center">
      <img
        src={NoFilterSelectedImage}
        style={{ width: "100%", height: "150PX" }}
      />
      <h3 className="text-center">
        <Translation>{(t) => t("Select a task from the List.")}</Translation>
      </h3>
      <p className="text-center">
        <Translation>
          {(t) =>
            t(
              "Choose a task from the list; your selection directs your current activity."
            )
          }
        </Translation>
      </p>
    </div>
  );
}
export default NoTaskSelectedMessage;
