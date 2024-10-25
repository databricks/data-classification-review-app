var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});

// Component to render an array of values as an expandable list
dagcomponentfuncs.ExpandableListRenderer = function (props) {
    const [isExpanded, setIsExpanded] = React.useState(false);

    if (!Array.isArray(props.value)) {
        return React.createElement('div', null, null);
    }

    const args = isExpanded ? props.value : props.value.join(',')
    
    const handleClick = () => {
        setIsExpanded(!isExpanded);
    };
    
    // Styling objects
    const styles = {
        container: { cursor: 'pointer' },
        collapsed: { whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
        expanded: { whiteSpace: 'normal', overflowWrap: 'anywhere', paddingLeft: '20px', margin: 0 },
        arrowIcon: { marginRight: '5px' },
    };
    
    // Content for collapsed and expanded states
    const content = isExpanded
        ? React.createElement(
            'div',
            null,
            React.createElement(
            'ul',
            { style: styles.expanded },
            args.map((item, index) =>
                React.createElement(
                'li',
                { key: index, style: { listStyleType: 'disc' } },
                item
                )
            )
            )
        )
        : React.createElement(
            'div',
            { style: styles.collapsed },
            React.createElement('span', null, args)
        );
    
    return React.createElement('div', { onClick: handleClick, style: styles.container }, content);
};

