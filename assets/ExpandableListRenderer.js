var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

// Component to render an array of values as an expandable list
// Used by the following columns: samples
dagcomponentfuncs.ExpandableListRenderer = function (props) {
  const [isExpanded, setIsExpanded] = React.useState(false);

  if (
    !Array.isArray(props.value) ||
    (Array.isArray(props.value) && props.value.length === 0)
  ) {
    let value = null;
    // Samples column has a special case where we display a custom msg if the value is None but pii_entity is defined
    if (props.colDef.field === "samples" && !!props.data["pii_entity"]) {
      value = "PII detected in metadata";
      return React.createElement(
        "div",
        { style: { "font-style": "italic" } },
        value
      );
    }

    return React.createElement("div", { className: "none-value" }, "None");
  }

  const args = isExpanded ? props.value : props.value.join(",");

  const handleClick = () => {
    setIsExpanded(!isExpanded);
  };

  const styles = {
    container: { cursor: "pointer" },
    collapsed: {
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis",
    },
    expanded: {
      whiteSpace: "normal",
      overflowWrap: "anywhere",
      paddingLeft: "20px",
      margin: 0,
    },
    arrowIcon: { marginRight: "5px" },
  };

  const content = isExpanded
    ? React.createElement(
        "div",
        null,
        React.createElement(
          "ul",
          { style: styles.expanded },
          args.map((item, index) =>
            React.createElement(
              "li",
              { key: index, style: { listStyleType: "disc" } },
              item
            )
          )
        )
      )
    : React.createElement(
        "div",
        { style: styles.collapsed },
        React.createElement("span", null, args)
      );

  return React.createElement(
    "div",
    { onClick: handleClick, style: styles.container },
    content
  );
};
