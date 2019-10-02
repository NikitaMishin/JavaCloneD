/**
 * Called from backend side
 * build view for source data
 * register handlers
 *
 * @param src_data
 * @param sourceNodesIds
 * @param componentId
 * @param graph
 */
function buildView(src_data, sourceNodesIds, componentId, graph) {
    window.componentId = componentId;

    let backendNodeIdToNode = new Map(src_data.map(function (node) {
        return [node.backendId, node]
    }));


    createTreeControl('tree', sourceNodesIds, componentId, backendNodeIdToNode);

    window.treeControl
        //.on("keydown", onKeyDownTree)
        //.on("nodeCommand", onNodeCommand)
        .on("fancytreefocus", activateHandlerTreeNode);
//        .on("fancytreeactivate", activateHandlerTreeNode);


    createGraph('visualisation', graph, $('#visualisation').width(), $('#visualisation').height());
    getNodes().on('click', obj => {
        fancyTreeTriggerFocusOnNode('tree', obj.id)
    });
    getGraphSvg().on('mouseenter',()=>{
        window.graphvEventHandlreds.removeHighlighting();
    });


}





