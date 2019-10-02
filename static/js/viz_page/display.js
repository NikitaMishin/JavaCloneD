/**
 * @param parents of kind [{
 *     backendId: int,
 *     markup:{
 *     'signature_from':str,
 *     'signature_to':str,
 *     'diff':str,
 *     ''with_variation: str
 *     }
 * }]
 * @param childrens of kind [{
 *     backendId: int,
 *     markup:string
 * }]
 * @param current [{
 *     backendId: int,
 *     markup:string
 * }]
 */
function setupMarkupForSelectedNode(parents, childrens, current) {

    // биндимся на


    // анбиндимсся
    let radioButton = $('input[type=radio][name=highlightmode]');
    radioButton.off();
    radioButton.on('change', () => {
        let value = parseInt($('input[type=radio][name=highlightmode]:checked').val());
        $('.carousel-item div[mode!=' + value + ']').hide();
        $('.carousel-item div[mode=' + value + ']').show();

    });


    /**
     * Sets markup for currently viewing mode
     */
    function setCurrent() {
        $('#mode_1_selected_node_node').html('<i>'+current.markup['signature'] +'</i>' +  '<hr>' + current.markup['body'])
    }

    let spac = (backendId, item, isActive,from) => {
        let start = isActive ? '<div class="carousel-item active" ' + 'backendId=' + item.backendId + '>' :
            '<div class="carousel-item" ' + 'backendId=' + item.backendId + '>';
        return start +
            '<div mode="0" style="display: none">'
            + '<i>' + item.markup[from ? 'signature_from' : 'signature_to' ] + '</i>' + '<hr>' + item.markup['no_highlight'] +
            '</div>' +
            //'<div mode="1" style="display: none">'
            //+ item.markup['signature_from'] + '<br>' + item.markup['diff'] +
            //'</div>' +
            '<div mode="2" style="display: none">'
            + '<i> '  + item.markup[from ? 'signature_from' : 'signature_to'] + '</i>'+ '<hr>' + item.markup['with_variation'] +
            '</div>' +
            '</div>'
    };


    /**
     *
     * @param selectorCarouselDiv
     * @param data of kind [{
     *     backendId:int,
     *     markup:string
     * }]
     */
    function setCarouselParent(selectorCarouselDiv, data) {
        $(selectorCarouselDiv + ' .carousel-item').remove();
        data.forEach((item, index) => {
            if (index === 0) {
                $(selectorCarouselDiv).append(spac(item.backendId, item, true,true));
            } else {
                $(selectorCarouselDiv).append(spac(item.backendId, item, false,true));
            }
        });
    }

    function setCarouselChildren(selectorCarouselDiv, data) {
        $(selectorCarouselDiv + ' .carousel-item').remove();
        data.forEach((item, index) => {
            if (index === 0) {
                $(selectorCarouselDiv).append(spac(item.backendId, item, true,false));
            } else {
                $(selectorCarouselDiv).append(spac(item.backendId, item, false,false));
            }
        });
    }

    let selectorChildrenCarousel = '#carouselChildMode1',
        selectorParentCarousel = '#carouselParentMode1';
    $(selectorChildrenCarousel).off('slid.bs.carousel'); //unregister previous handler
    $(selectorParentCarousel).off('slid.bs.carousel');//unregister previous handler

    setCurrent();
    setCarouselParent('#mode_1_selected_node_parents', parents);
    setCarouselChildren('#mode_1_selected_node_childrens', childrens);
    let currentMode = $("input[name='highlightmode']:checked").val();
    $('.carousel-item div[mode=' + currentMode + ']').show();

    let currentNodeId = current.backendId;
    //args swapped cause we highlight exactly source -> target link
    $(selectorChildrenCarousel).on('slid.bs.carousel', (event) =>
        window.graphvEventHandlreds.highlightSourceTarget(parseInt(currentNodeId), parseInt($(event.relatedTarget).attr('backendId'))));
    $(selectorParentCarousel).on('slid.bs.carousel', (event) =>
        window.graphvEventHandlreds.highlightSourceTarget(parseInt($(event.relatedTarget).attr('backendId')), parseInt(currentNodeId)));

}