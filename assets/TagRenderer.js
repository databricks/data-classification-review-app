var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

// Component to render a single tag. Does not support list of values (yet)
// Used by the following columns: pii_entity
dagcomponentfuncs.TagRenderer = function (props) {
  if (!props.value) {
    return React.createElement("div", null, null);
  }

  const formattedValue =
    props.colDef.field === "pii_entity" ? "system_" + props.value : props.value;

  return React.createElement(
    "div",
    { className: "custom-tag-parent" },
    React.createElement(
      "div",
      { className: "custom-tag-child" },
      formattedValue
    )
  );
};
