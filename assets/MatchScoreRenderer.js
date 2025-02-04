var dagcomponentfuncs = (window.dashAgGridComponentFunctions =
  window.dashAgGridComponentFunctions || {});

// Component to display match score as a battery icon
// Used by the following columns: match_score
dagcomponentfuncs.MatchScoreRenderer = function (props) {
  let value = props.value;
  if (!props.value || !Number.isInteger(props.value)) {
    value = 0;
  }

  let bucket = "Low";
  let className = "fa-solid fa-battery-quarter match-icon low-match";
  if (props.value > 75) {
    bucket = "High";
    className = "fa-solid fa-battery-full match-icon high-match";
  } else if (props.value > 50) {
    bucket = "High";
    className = "fa-solid fa-battery-three-quarters match-icon high-match";
  } else if (props.value > 25) {
    className = "fa-solid fa-battery-half match-icon low-match";
  } else if (props.value > 0) {
    className = "fa-solid fa-battery-quarter match-icon low-match";
  } else if (props.value === 0) {
    bucket = "None";
    className = "fa-solid fa-battery-empty match-icon";
  }

  const content = React.createElement(
    "span",
    { title: props.value },
    React.createElement("i", { className: className }, null),
    bucket
  );

  return React.createElement("div", null, content);
};
