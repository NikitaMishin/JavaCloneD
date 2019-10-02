/**
 * Triggers Highlight neighbour and focus to node by click and mouseover
 * @param id
 */
function d3GraphTriggerFocusOnNode(id) {
    //TODO change in method to id not object by lambda functions
    window.graphvEventHandlreds.focusOnNode(id);
    window.graphvEventHandlreds.highlightNeighbours(id)
}

/**
 * Removes highlightning of neighbour
 */
function d3GraphTriggerRemoveHighlight() {
    window.graphvEventHandlreds.removeHighlighting();
}

/**
 * Highlight
 * @param fromId
 * @param toId
 */
function d3GraphTriggerHighlightSourceTarget(fromId, toId) {
    window.graphvEventHandlreds.highlightSourceTarget(fromId, toId);
}

/**
 *
 * @param treeId
 * @param nodeId
 * @returns {boolean}
 */
function fancyTreeTriggerFocusOnNode(treeId, nodeId) {
    let focusNode = $('#' + treeId).fancytree("getTree").getFocusNode();
    let tree = $("#" + treeId).fancytree("getTree");

    //tree.selectAll(false);
    if (focusNode) {

        let childrenFancyTreeNode = [];
        focusNode.visit(node => childrenFancyTreeNode.push({backendId: node.data.backendNode, key: node.key}));

        let parentFancyTreeNodes = focusNode.getParentList(false, true);
        let backendIds = parentFancyTreeNodes
            .map(node => node.data.backendNode).concat(childrenFancyTreeNode.map(elem => elem.backendId));
        let keysIds = parentFancyTreeNodes
            .map(node => node.key).concat(childrenFancyTreeNode.map(elem => elem.key));

        let indexOf = backendIds.indexOf(nodeId);
        if (indexOf !== -1) {
            // focus on node in current branch
            tree.getNodeByKey(keysIds[indexOf]).setFocus();
            tree.getNodeByKey(keysIds[indexOf]).setActive();
            //tree.getNodeByKey(keysIds[indexOf]).setSelected();

            //TODO change on backedn

            let parents = dataFromServer[window.componentId]['markups'][nodeId]['parents'];
            let childrens = dataFromServer[window.componentId]['markups'][nodeId]['childrens'];
            let current = dataFromServer[window.componentId]['markups'][nodeId]['current'];
            setupMarkupForSelectedNode(parents, childrens, current);

            return true;
        }
    }

    tree.getNodeByKey(tree.getNodesByRef(nodeId)[0].key).setFocus();
    tree.getNodeByKey(tree.getNodesByRef(nodeId)[0].key).setActive();
    //tree.getNodeByKey(tree.getNodesByRef(nodeId)[0].key).setSelected();
    let parents = dataFromServer[window.componentId]['markups'][nodeId]['parents'];
    let childrens = dataFromServer[window.componentId]['markups'][nodeId]['childrens'];
    let current = dataFromServer[window.componentId]['markups'][nodeId]['current'];
    setupMarkupForSelectedNode(parents, childrens, current);
//    window.backend.trigger_load_html_markup_display(window.componentId, nodeId);
}




