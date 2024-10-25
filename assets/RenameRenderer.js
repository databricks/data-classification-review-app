var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

// Component to simply rename the value and render as div
dagcomponentfuncs.RenameRenderer = function (props) {
    if (!props.value) {
      return React.createElement('div', null, null);
    }

    let renamedValue = props.value;
    if (Array.isArray(props.value) && props.value.length > 0) {
      const detections = [];    
      for (const val of props.value) {
        if (val === "pii_detected_in_row") {
          detections.push("row");
        }
        else if (val === "pii_detected_in_metadata") {
          detections.push("metadata");
        }
      }
    
      if (detections.length > 0) {
        renamedValue = "PII detected in " + detections.join(" and ");
      }
    } else {
      if (props.value === "apply_tag") {
        renamedValue = "Applied tag";
      } else if (props.value === "reject") {
        renamedValue = "Rejected";
      }
    }
    
    return React.createElement(
      'div',
      {title: renamedValue},
      renamedValue
    );};

