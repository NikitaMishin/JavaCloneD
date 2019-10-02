/**
 * Removes graph and tree then triggers loading data from backend for initialization of new graph and tree
 * @param componentId id of component from backend side
 */
function createNewMarkup(componentId, groupName) {
    removeTreeControl();
    deleteGraph('graph');
    //TODO trouble with recursion
    buildView(dataFromServer[componentId]['src_data'], dataFromServer[componentId]['source_nodes_idx'], componentId,dataFromServer[componentId]['graph']);
    $('#group_header').html(
        'Group name ' + '&laquo;' + groupName + '&raquo;'
    )

}

