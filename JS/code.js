/*
let ele = {
  nodes: [
    { data: { id: 'a' } },
    { data: { id: 'b' } },
    { data: { id: 'c' } },
    { data: { id: 'd' } },
    { data: { id: 'e' } }
  ],

  edges: [
    { data: { id: 'a"e', weight: 1, source: 'a', target: 'e' } },
    { data: { id: 'ab', weight: 3, source: 'a', target: 'b' } },
    { data: { id: 'be', weight: 4, source: 'b', target: 'e' } },
    { data: { id: 'bc', weight: 5, source: 'b', target: 'c' } },
    { data: { id: 'ce', weight: 6, source: 'c', target: 'e' } },
    { data: { id: 'cd', weight: 2, source: 'c', target: 'd' } },
    { data: { id: 'de', weight: 7, source: 'd', target: 'e' } }
  ]
}*/

//cytoscape.use(klay)

let uri = 'output.json';
let ele = {nodes : [], edges : []};
let nodes_in = {};
let edges_in = {};
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
        pnId = s[j].rawPattern + s[j].initX.toString() + s[j].initY.toString() + s[j].width.toString() + s[j].height.toString()
        cNode = { 
          data: { 
            id: pnId,
            weight: 1
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
                id: peID, // decide what an ID object should be
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
    let cy = cytoscape({
      container: $('#cy'),
      boxSelectionEnabled: false,
      autounselectify: true,
      style: cytoscape.stylesheet()
        .selector('node')
          .style({
            'content': 'data(weight)'
          })
        .selector('edge')
          .style({
              'content' : 'data(weight)',
              'curve-style': 'bezier',
              'target-arrow-shape': 'triangle',
              'width': 4,
              'line-color': '#ddd',
              'target-arrow-color': '#ddd'
          })
        .selector('.highlighted')
          .style({
              'background-color': '#61bffc',
              'line-color': '#61bffc',
              'target-arrow-color': '#61bffc',
              'transition-property': 'background-color, line-color, target-arrow-color',
              'transition-duration': '0.5s'
          }),
      elements: ele,
      layout: {
        name: 'breadthfirst',
        padding: 150
      }
    });
}});

