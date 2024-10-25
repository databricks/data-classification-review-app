var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

// Component to render a single tag. Does not support list of values (yet)
dagcomponentfuncs.TagRenderer = function (props) {
    if (!props.value) {
      return React.createElement('div', null, null);
    }

    const formattedValue = "system_pii_" + props.value;
    
    return React.createElement(
      'div',
      { className: 'custom-tag-parent' },
      React.createElement('div', { className: 'custom-tag-child' }, formattedValue)
    );};

