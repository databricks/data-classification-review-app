var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

// Component to simply rename the value and render as div
// Used by the following columns: review_status
dagcomponentfuncs.RenameRenderer = function (props) {
  if (!props.value) {
    return React.createElement("div", null, null);
  }

  let renamedValue = props.value;
  if (props.colDef.field === "review_status") {
    if (props.value === "applied_tag") {
      renamedValue = "Applied tag";
    } else if (props.value === "rejected") {
      renamedValue = "Rejected";
    }
  }

  return React.createElement("div", { title: renamedValue }, renamedValue);
};
