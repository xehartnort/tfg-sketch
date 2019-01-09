
const uri = 'oscilator100.json';
const layoutOptionsB = {
  name: 'breadthfirst',
  fit: true, // whether to fit the viewport to the graph
  directed: false,
  padding: 100,
  spacingFactor: 2.5, // 1.75 positive spacing factor, larger => more space between nodes (N.B. n/a if causes overlap)
  nodeDimensionsIncludeLabels: true //, // Excludes the label when calculating node bounding boxes for the layout algorithm
}
/*const layoutOptionsC = {
  name: 'cose',
  fit: true, // whether to fit the viewport to the graph
  directed: true, // whether the tree is directed downwards (or edges can point in any direction if false)
  spacingFactor: 6, // 1.75 positive spacing factor, larger => more space between nodes (N.B. n/a if causes overlap)
  avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
  nodeDimensionsIncludeLabels: true // Excludes the label when calculating node bounding boxes for the layout algorithm
}*/
let ele = {nodes : [], edges : []};
let nodes_in = {};
let edges_in = {};
let cy;
let poda = true;
const pruned_nodes = [];
const pruned_edges = [];
const weight_cut = 5;
$('#prune').click(()=>{
  if (poda){
    if (pruned_edges.length === 0 && pruned_nodes.length === 0){
      // el código de poda se tiene que ejecutar solamente una vez jeje
      let edges = cy.edges();
      for(let i=0; i<edges.length; i++){
        if (edges[i].data('weight') <= weight_cut){
          pruned_edges.push(cy.remove(edges[i]));
        }
      }
      let nodes = cy.nodes();
      for(let i=0; i<nodes.length; i++){
        if (nodes[i].data('weight') <= weight_cut){
          pruned_nodes.push(cy.remove(nodes[i]));
        }
      }
      const root = cy.nodes().filter( (ele) => {
        return ele.data('type') === 'root';
      });
      for(let i=0; i<nodes.length; i++){
        if (nodes[i].data('type') === 'son'){
          if (nodes[i].edgesWith(root).length == 0){
            pruned_nodes.push(cy.remove(nodes[i]));
          }
        }
        let c = nodes[i].connectedEdges();
        if (c.length == 0){
          pruned_nodes.push(cy.remove(nodes[i]));
        }else if (c.length == 1 && c[0].isLoop()){
          pruned_nodes.push(cy.remove(nodes[i]));
        }
      }
    }else{
      for(let i=0; i<pruned_nodes.length; i++){
        cy.remove(pruned_nodes[i]);
      }
      for(let i=0; i<pruned_edges.length; i++){
        cy.remove(pruned_edges[i]);
      }    
      poda = false;
    }
    cy.layout(layoutOptionsB).run();
  }else{
    for(let i=0; i<pruned_nodes.length; i++){
      pruned_nodes[i].restore();
    }
    for(let i=0; i<pruned_edges.length; i++){
      pruned_edges[i].restore();
    }
    poda = true;
    cy.layout(layoutOptionsB).run();
  }
});
$.ajax({
  url: uri, 
  success: function(result){
    let s;
    let pnId;
    let peID;
    for (let i=0; i<result.length; i++){
      s = result[i].steps
      let lastNode = undefined;
      let cNode = undefined;
      let cEdge = undefined;
      for (let j=0; j<s.length; j++){
        pnId = s[j].rawPattern + s[j].initX.toString() + s[j].initY.toString(); // + s[j].width.toString() + s[j].height.toString()
        cNode = { 
          data: { 
            id: pnId,
            type: s[j].type,
            weight: 1,
            icon: result[i]+s[j].icon,
            color: result[i].color
          }
        };
        if (nodes_in[pnId] === undefined){
          nodes_in[pnId] = ele.nodes.length;
          ele.nodes.push(cNode);
        }else{
          let pos = nodes_in[pnId];
          ele.nodes[pos].data.weight +=1
        }
        if (lastNode !== undefined){
          peID = pnId+lastNode.data.id;
          if (edges_in[peID] === undefined){
            edges_in[peID] = ele.edges.length;
            cEdge = { 
              data: {
                id: peID, 
                source: lastNode.data.id, 
                target: pnId,
                weight: 1
              }
            };
            ele.edges.push(cEdge);
          }else{
            let pos = edges_in[peID];
            ele.edges[pos].data.weight +=1
          }
        }
        lastNode = cNode;
      }
    }
    cy = cytoscape({
      container: $('#cy'),
      boxSelectionEnabled: false,
      autounselectify: true,
      style: cytoscape.stylesheet()
        .selector('node')
          .style({
            'shape': 'rectangle', // por el css hay que añadir propiedades al background image
            'border-width': 0,
            'background-color': 'data(color)',
            'background-fit': 'contain',
            'background-image': 'data(icon)'
          })
        .selector('edge')
          .style({
              'content' : 'data(weight)',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'width': 4
          })
        /*.selector('.highlighted')
          .style({
              'background-color': '#61bffc',
              'line-color': '#61bffc',
              'target-arrow-color': '#61bffc'
          })*/,
      elements: ele,
      layout: layoutOptionsB
    });
}});

