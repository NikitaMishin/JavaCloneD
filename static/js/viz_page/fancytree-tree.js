function createTreeControl(divId, sourceNodesIds, treeId, backendNodeIdToNode) {
    let selector = '#' + divId;

    function prepareData() {
        let globalCounter = 0;

        function build(id) {
            let refNode = backendNodeIdToNode.get(id);
            globalCounter++;
            return {
                backendNode: id,
                key: globalCounter,
                folder: refNode.folder,
                title: refNode.title,
                children: refNode.children.map(function (idx) {
                    return build(idx);
                }),
                refKey: id
            };
        }

        return sourceNodesIds.map(build)
    }

    window.treeControl =
        $(selector)
            .fancytree({
                extensions: [ //"multi",
                    "glyph",
                    //"childcounter",
                     "clones"],
                glyph: {
                    preset: "awesome5",
                    map: {
                        // Override distinct default icons here
                        expanderClosed: "fa fa-plus",
                        expanderOpen: "fa fa-minus",
                        folder: "fa fa-tree",
                        folderOpen: "fa fa-tree",
                        doc: "fa fa-leaf"
                    }
                },

                // childcounter: {
                //     deep: true,
                //     hideZeros: true,
                //     hideExpanded: false
                // },
                //
                // multi: {
                //     // other modes not implemented yet
                //     mode: "sameParent",
                // },
                checkbox: false,
                keyboard: true, // Support keyboard navigation
                idPrefix: "tree_node_", // Used to generate node idÂ´s like <span id='fancytree-id-<key>'>
                generateIds: false, // Generate id attributes like <span id='fancytree-id-KEY'>
                focusOnSelect: true, // Set focus when node is checked by a mouse click
                selectMode: 2,
                //icon: false,
                source: prepareData(),
                renderNode: function (event, data) {
                    let node = data.node;
                    if (node.data) {
                    }
                },


            });


    $(".fancytree-container").addClass("fancytree-connectors");

}

function removeTreeControl() {
    $(":ui-fancytree").fancytree("destroy");
}