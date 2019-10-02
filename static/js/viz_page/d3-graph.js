/**
 * D3-force directed graph
 * interaction with other components described in other files
 */


let notNeighbourOpacityGraphNode = 0.05;
let lineColorDefault = '#999';
let lineColorParent = 'red';
let lineColorChildren = 'green';


function deleteGraph(svgId) {
    $('#' + svgId).html('');
}

/**
 *
 * @param divId
 * @param graph
 * @param width
 * @param height
 */
function createGraph(divId, graph, width, height) {
    let selector = '#' + divId;
    // let colors = d3.scaleOrdinal(d3.schemeCategory10);
    let colors = (_) => '#1C6699';
    let currentZoom = 1.0;

    const graphEventHandlers = {
        opacity: 0.2,
        focusOnNode: function (id) {
            actions.clicked(utilFunctions.getNodeById(id));
        },
        highlightNeighbours: function (id) {
            let parents = new Set(linkData.filter(elem => elem.target.id === id).map(elem => elem.source.id)),
                childrens = new Set(linkData.filter(elem => elem.source.id === id).map(elem => elem.target.id));

            node.filter((obj) => obj.id === id)
                .transition().duration(150).selectAll('circle').attr('r', 6.5);
            node.transition().duration(150).style('opacity', function (obj) {
                return parents.has(obj.id) || childrens.has(obj.id) || obj.id === id ? 1 : notNeighbourOpacityGraphNode;
            });

            //order is important
            link
                .transition().duration(0).style('stroke',
                obj => {
                    if (obj.source.id === id) return lineColorChildren;
                    if (obj.target.id === id) return lineColorParent;
                    return lineColorDefault;
                })
                .transition().duration(0).attr('marker-end',
                obj => {
                    if (obj.source.id === id) return utilFunctions.getMarker(lineColorChildren);
                    if (obj.target.id === id) return utilFunctions.getMarker(lineColorParent);
                    return utilFunctions.getMarker(lineColorDefault);
                })

                .transition().duration(150).style('opacity',
                obj => obj.source.id === id || obj.target.id === id ? 1 : notNeighbourOpacityGraphNode
            );


        },

        highlightSourceTarget: function (source_id, target_id) {
            node.transition().duration(500).style('opacity', function (obj) {
                return +obj.id === source_id || +obj.id === +target_id ? 1 : notNeighbourOpacityGraphNode;
            });

            link
                .transition().duration(0).attr('marker-end',
                obj =>
                    obj.source.id === source_id && obj.target.id === target_id ?
                        utilFunctions.getMarker(lineColorParent) : utilFunctions.getMarker(lineColorDefault))
                .transition().duration(150).style('stroke',
                obj => obj.source.id === source_id && obj.target.id === target_id ? lineColorParent : lineColorDefault)
                .transition().duration(150).style('opacity',
                obj => obj.source.id === source_id && obj.target.id === target_id ? 1 : notNeighbourOpacityGraphNode);


        },

        removeHighlighting: function () {
            node.transition().duration(150).selectAll('circle').attr('r', 5);
            node.transition().duration(500).style('opacity', 1);

            link
                .transition().duration(0).attr('marker-end', utilFunctions.getMarker(lineColorDefault))
                .transition().duration(0).style('stroke', lineColorDefault)
                .transition().duration(500).style('opacity', 1);
        }
    };
    window.graphvEventHandlreds = graphEventHandlers;

    const utilFunctions = {
        getMarker: (color) => {
            if (color === lineColorParent) {
                return 'url(#arrowhead_parent)'
            } else if (color === lineColorChildren) {
                return 'url(#arrowhead_children)'
            } else {
                return 'url(#arrowhead_default)'
            }
        },
        terminationTime: Date.now(),
        svgWidth: () => $(selector).width(),//+getComputedStyle(document.getElementById('container_graph')).width.replace('px',''),
        svgHeight: () => $(selector).height(),//+getComputedStyle(document.getElementById('container_graph')).height.replace('px',''),
        getNodeById: id => nodeData.find(elem => +elem.id === +id),
        setSimulationTerminationTime: (ms) => utilFunctions.terminationTime = Date.now() + ms,
        stopSimulationAfterMs: ms => {
            if (Date.now() + ms >= utilFunctions.terminationTime) {
                utilFunctions.setSimulationTerminationTime(ms);
            }
            setTimeout(() => {
                if (Date.now() >= utilFunctions.terminationTime) {
                    simulation.stop()
                }
            }, ms);
        }
    };


    const actions = {
        dragged: {
            //https://stackoverflow.com/questions/42605261/d3-event-active-purpose-in-drag-dropping-circles
            // if statements for multitouch
            dragStarted: function (d) {
                if (!d3.event.active) {
                    simulation.alphaTarget(0.3).restart();
                    //   utilFunctions.setSimulationTerminationTime(hours);
                }
                d.fx = d.x;
                d.fy = d.y;
            },
            dragged: function (d) {
                d.fx = d3.event.x;
                d.fy = d3.event.y;
            },
            dragEnded: function (d) {
                if (!d3.event.active) {
                    simulation.alphaTarget(0);
                }
                d.fx = null;
                d.fy = null;
            }
        },

        clicked: function (source) {
            //TODO https://jsfiddle.net/Tokker/mwm1sxhh/21/ with g also changed nested nodes while i think they shouldnot

            let x = -source.x * currentZoom + utilFunctions.svgWidth() / 2;
            let y = -source.y * currentZoom + utilFunctions.svgHeight() / 2;
            svg.transition().duration(1500)
                .call(zoom.transform, d3.zoomIdentity.translate(x, y).scale(currentZoom));
        },
        zoomed: function () {
            currentZoom = d3.event.transform.k;
            let x = d3.event.transform.x;
            let y = d3.event.transform.y;
            container.attr("transform", "translate(" + x + "," + y + ") scale(" + currentZoom + ")");
        },

        update: function (links, nodes) {

            link = container.append('g').selectAll(".link")
                .data(links)
                .enter()
                .append("line")
                .attr("class", "link")
                .attr('marker-end', 'url(#arrowhead_default)');

            node = container.append('g').selectAll(".node")
                .data(nodes)
                .enter()
                .append("g")
                .attr("class", "node")
                .on('click', actions.clicked)
                .on('mouseover', graph_node => graphEventHandlers.highlightNeighbours(graph_node.id))
                .on('mouseleave', graphEventHandlers.removeHighlighting)
                .call(d3.drag()
                    .on("start", actions.dragged.dragStarted)
                    .on("drag", actions.dragged.dragged)
                    .on("end", actions.dragged.dragEnded)
                );


            node.append("circle")
                .attr("r", 5)
                .style("fill", function (d, i) {
                    return colors(i);
                });

             let labels = node.append("text")
                 .text(function(d) {
                     return d.name;
                 })
                 .attr('x', 6)
                 .attr('y', -5)
                 .attr('pointer-events','none');


            simulation
                .nodes(nodes)
                .on("tick", actions.ticked);

            simulation.force("link")
                .links(links);

            nodeData = node.data();
            linkData = link.data();
        },

        ticked: function () {
            link
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node
                .attr("transform", function (d) {
                    return "translate(" + d.x + ", " + d.y + ")";
                })
        }

    };


    let zoom = d3.zoom().on("zoom", actions.zoomed);
    let svg = d3.select("svg").call(zoom),
        node,
        nodeData,
        link,
        linkData;


//add encompassing group for the zoom
    let container = svg.append("g")
        .attr("class", "everything")
        .attr('id', 'container');

    svg.style('width', width)
        .style('height', height);


    //https://github.com/d3/d3-force
    //define arrowhead
    container.append("g").append('defs').append('marker')
        .attrs({
            'id': 'arrowhead_default',
            'viewBox': '-0 -4 8 8',
            'refX': 11,
            'refY': 0,
            'orient': 'auto',
            'markerWidth': 10,
            'markerHeight': 10,
            'xoverflow': 'visible'
        })
        .append('svg:path')
        .attr('d', 'M 0,-3 L 8 ,0 L 0,3')
        .attr('fill', lineColorDefault)
        .style('stroke', 'none');

    container.append("g").append('defs').append('marker')
        .attrs({
            'id': 'arrowhead_children',
            'viewBox': '-0 -4 8 8',
            'refX': 11,
            'refY': 0,
            'orient': 'auto',
            'markerWidth': 10,
            'markerHeight': 10,
            'xoverflow': 'visible'
        })
        .append('svg:path')
        .attr('d', 'M 0,-3 L 8 ,0 L 0,3')
        .attr('fill', lineColorChildren)
        .style('stroke', 'none');

    container.append("g").append('defs').append('marker')
        .attrs({
            'id': 'arrowhead_parent',
            'viewBox': '-0 -4 8 8',
            'refX': 11,
            'refY': 0,
            'orient': 'auto',
            'markerWidth': 10,
            'markerHeight': 10,
            'xoverflow': 'visible'
        })
        .append('svg:path')
        .attr('d', 'M 0,-3 L 8 ,0 L 0,3')
        .attr('fill', lineColorParent)
        .style('stroke', 'none');

    let simulation = d3.forceSimulation()
    //specifies that id is the link variable
        .force("link", d3.forceLink().id(function (d) {
            return d.id;
        }).distance(30).strength(1))
        //  nodes repel from each other which prevents overlap
        .force("charge", d3.forceManyBody().strength(-1000))
        // x and y — pull nodes towards the centre with x stronger so nodes fill the landscape vertical better
        .force("x", d3.forceX(utilFunctions.svgWidth() / 2).strength(0.8))
        .force("y", d3.forceY(utilFunctions.svgHeight() / 2).strength(0.2));


    actions.update(graph.links, graph.nodes);

    $(window).resize(() => {
        svg.style('width', $(selector).width() + 'px');
        svg.style('height', $(selector).height() + 'px');
    });

    //TODO not forget to mention
    svg.attr('pointer-events','all');
}

/**
 * returns nodes of current graph
 */
function getNodes() {
    return d3.selectAll('g .node');
}

/**
 * returns edges of current graph
 */
function getEdges() {
    return d3.selectAll('g .link')
}
function getGraphSvg() {
    return d3.select("svg");

}
