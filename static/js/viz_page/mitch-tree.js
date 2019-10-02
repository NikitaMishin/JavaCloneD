/**
 *
 * @param fancyTreeJsonedData
 * @param backendNodeIdToNode
 */
function buildTreeGraph(fancyTreeJsonedData, backendNodeIdToNode) {

    function f(dict) {
        if ('children' in dict) {
            return dict['children'].map(function (node) {
                return prepareData(node);
            })
        } else {
            return []
        }
    }

    function prepareData(dict) {
        //TODO bug with missing refKey
        return {
            title: dict['title'],
            text: backendNodeIdToNode.get(dict['data']['backendNode']).text,
            id: dict['key'],
            backendId: dict['data']['backendNode'],
            children: f(dict)
        }
    }


    fancyTreeJsonedData.title = 'Tree';
    let data = {
        title: 'Root',
        text: 'System root',
        id: -1,
        backendId: -1,
        children: fancyTreeJsonedData.children.map(function (node) {
            return prepareData(node);
        })
    };


    window.treePlugin = new d3.mitchTree.boxedTree()
        .setData(data)
        .setElement(document.getElementById("visualisation"))
        .setIdAccessor(function (data) {

            return data.id;
        })
        .setChildrenAccessor(function (data) {
            return data.children;
        })
        .setBodyDisplayTextAccessor(function (data) {
            return data.text;
        })
        .setTitleDisplayTextAccessor(function (data) {
            return data.title;
        })
        .setOrientation('topToBottom')
        .setMargins({
            top: 20,
            right: 20,
            bottom: 20,
            left: 20
        })
        .setMinScale(0.2)
        .initialize();
}

function onNodeClickMitchTree(event) {
    let tree = $("#tree").fancytree('getTree');
    let data = event.nodeDataItem.data;
    let parent = event.nodeDataItem.parent;
    tree.activateKey(data.id, {noEvents: true});
    let backendTreeId = window.componentId;
    let backendNodeId = data.backendId;
    let backendParentId = undefined;

    if (parent === null) {
        backendParentId = -1;
    } else {
        backendParentId = parent.data.backendId;
    }
    if (window.backend && backendNodeId !== -1) {
        window.backend.trigger_load_html_markup_display(backendTreeId, backendNodeId, backendParentId);
    }

}