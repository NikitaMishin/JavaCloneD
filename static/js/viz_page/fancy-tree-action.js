let OSName = "Unknown OS";
if (navigator.appVersion.indexOf("Win") !== -1) OSName = "Windows";
if (navigator.appVersion.indexOf("Mac") !== -1) OSName = "MacOS";
if (navigator.appVersion.indexOf("X11") !== -1) OSName = "UNIX";
if (navigator.appVersion.indexOf("Linux") !== -1) OSName = "Linux";
if (OSName === "Unknown OS") OSName = "Windows";
let CLIPBOARD = null;


// #TODo create custom event to notify about changes

/**
 * Remove selected nodes
 * @param treeId tree id
 * @param shouldDeleteDuplicates should or should not also delete duplicates with same refKey
 * @param forceRender Rerender tree to update html markup
 * @returns {boolean} if not selected then false otherwise process operation and returns true
 */
function removeSelectedNodes(treeId, shouldDeleteDuplicates = false, forceRender = true) {
    let tree = $("#" + treeId).fancytree("getTree");
    let toDelete = tree.getSelectedNodes();
    alert(toDelete.length);
    if (toDelete.length === 0) return false;
    toDelete.forEach(function (node) {
        if (shouldDeleteDuplicates) {
            _removeDuplicateNodes(treeId, node.refKey);
        }
        if (node.parent != null) {
            node.remove();
        }
    });
    if (forceRender) $("#" + treeId).fancytree("getRootNode").render(true, true);
    // notify

    return true;
}


/**
 * Remove duplicated nodes in tree which have same refKey
 * @param treeId tree id
 * @param refKey
 * @returns {boolean}
 */
function _removeDuplicateNodes(treeId, refKey) {
    let tree = $("#" + treeId).fancytree("getTree");
    let clones = tree.getNodesByRef(refKey);
    if (clones == null) return false;
    clones.map(function (node) {
        if (node && !node.data.root && node.parent) {
            node.remove();
        }
    });
    return true;
}


/**
 *
 * @param e
 * @returns {boolean}
 */
function onKeyDownTree(e) {
    let command = null;
    switch ($.ui.fancytree.eventToString(e)) {
        case "ctrl+return":
        case "meta+return":
        case "return":
            //again higighligj
            command = "display";
            let focusNode = $('#' + 'tree').fancytree("getTree").getFocusNode();
            focusNode.trigger();
            $(window.contextMenu).show();
            break;
        case "ctrl+c":
        case "meta+c": // mac
            command = "copy";
            break;
        case "ctrl+v":
        case "meta+v": // mac
            command = "paste";
            break;
        case "ctrl+x":
        case "meta+x": // mac
            command = "cut";
            break;
        case "del":
        case "meta+backspace": // mac
            command = "remove";
            break;
        case "ctrl+shift+n":
            command = "new";
            break;
        case "ctrl+e":
        case "ctrl+shift+e": // mac
            command = "edit";
            break;
        case "ctrl+up":
        case "ctrl+shift+up": // mac
            command = "moveUp";// move in current catalogue up
            break;
        case "ctrl+down":
        case "ctrl+shift+down":// move in current catalogue up
            command = "moveDown";
            break;
        case "ctrl+right":
        case "ctrl+shift+right": // move on inner level
            command = "indent";
            break;
        case "ctrl+left":
        case "ctrl+shift+left": // mac
            command = "outdent"; // move on outer level
    }
    if (command) {
        $(this).trigger("nodeCommand", {command: command});
        return false;//false to prevent default handling
    }

}

/**
 *
 * @param e
 * @param data
 */
function onNodeCommand(e, data) {
    let tree = $(this).fancytree("getTree");
    let node = tree.getActiveNode();
    switch (data.command) {
        case "addChild":
        case "addSibling":
        case "indent":
        case "moveDown":
        case "moveUp":
        case "outdent":
        case "remove":
        case "rename":
            tree.applyCommand(data.command, node);
            break;
        case "cut":
            CLIPBOARD = {mode: data.command, data: node};
            break;
        case "copy":
            CLIPBOARD = {
                mode: data.command,
                data: node.toDict(function (n) {
                    delete n.key;
                }),
            };
            break;
        case "clear clipboard":
            CLIPBOARD = null;
            break;
        case "paste":
            if (CLIPBOARD.mode === "cut") {
                // refNode = node.getPrevSibling();
                CLIPBOARD.data.moveTo(node, "child");
                CLIPBOARD.data.setActive();
            } else if (CLIPBOARD.mode === "copy") {
                node.addChildren(
                    CLIPBOARD.data
                ).setActive();
            }
            break;
        default:
            alert("Unhandled command: " + data.command);
            return;
    }
}

/**
 *
 * @param event
 * @param data
 */
function activateHandlerTreeNode(event, data) {
    let node = data.node;
    let backendNodeId = node.data.backendNode;

    let parents = dataFromServer[window.componentId]['markups'][backendNodeId]['parents'];
    let childrens = dataFromServer[window.componentId]['markups'][backendNodeId]['childrens'];
    let current = dataFromServer[window.componentId]['markups'][backendNodeId]['current'];

    setupMarkupForSelectedNode(parents,childrens,current);

    d3GraphTriggerFocusOnNode(backendNodeId);

}