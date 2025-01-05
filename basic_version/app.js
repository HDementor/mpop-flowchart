document.addEventListener('DOMContentLoaded', function () {
    fetch('data.json')
      .then((response) => response.json())
      .then((json) => {
        const cy = cytoscape({
          container: document.getElementById('cy'),
          style: json.style,
          elements: json.elements,
          layout: {
            name: 'dagre',
            rankDir: 'LR',
            nodeSep: 20,
            edgeSep: 10,
            rankSep: 30
          }
        });
  
        function isHidden(id) {
          return cy.getElementById(id).hasClass('hidden');
        }
  
        function show(id) {
          cy.getElementById(id).removeClass('hidden');
        }
  
        function hide(id) {
          cy.getElementById(id).addClass('hidden');
        }
  
        function setNodeColor(node, fill, outline) {
          node.style('background-color', fill);
          node.style('border-color', outline);
        }
  
        // Click handler for Breast to toggle Node B and its edge
        cy.on('tap', 'node[id="Breast"]', () => {
          const nodeBreast = cy.getElementById('Breast');
          const nodeB = cy.getElementById('B');
          const edgeBreastB = cy.getElementById('Breast-B');
  
          if (isHidden('B')) {
            // Show Node B and edge
            setNodeColor(nodeBreast, '#5bc0de', '#001f3f');
            show('B');
            show('Breast-B');
            edgeBreastB.style({
              'line-color': '#001f3f',
              'target-arrow-color': '#001f3f'
            });
          } else {
            // Hide Node B and edge
            setNodeColor(nodeBreast, '#ccc', '#000');
            hide('B');
            hide('Breast-B');
  
            // Also hide B's children and their edges
            hide('C'); hide('B-C');
            hide('D'); hide('B-D');
            hide('E'); hide('B-E');
          }
  
          cy.layout({ name: 'dagre', rankDir: 'LR' }).run();
        });
  
        // Click handler for Node B to toggle its children and edges
        cy.on('tap', 'node[id="B"]', () => {
          const nodeB = cy.getElementById('B');
          const edgeBreastB = cy.getElementById('Breast-B');
          const edges = ['B-C', 'B-D', 'B-E'];
  
          if (isHidden('C')) {
            // Expand B's children
            setNodeColor(nodeB, '#5bc0de', '#001f3f');
            show('C'); show('B-C');
            show('D'); show('B-D');
            show('E'); show('B-E');
  
            // Ensure Breast->B edge remains visible
            edgeBreastB.style({
              'line-color': '#001f3f',
              'target-arrow-color': '#001f3f'
            });
          } else {
            // Collapse B's children
            setNodeColor(nodeB, '#ccc', '#000');
            hide('C'); hide('B-C');
            hide('D'); hide('B-D');
            hide('E'); hide('B-E');
          }
  
          cy.layout({ name: 'dagre', rankDir: 'LR' }).run();
        });
  
        // Disable clicks for other L1 nodes
        cy.on('tap', 'node', (evt) => {
          const node = evt.target;
          const nodeId = node.id();
  
          if (nodeId !== "Breast" && nodeId !== "B") {
            evt.stopPropagation();
          }
        });
      })
      .catch((err) => {
        console.error('Error fetching/using data.json:', err);
      });
  });
  