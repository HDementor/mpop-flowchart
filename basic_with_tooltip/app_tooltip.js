document.addEventListener('DOMContentLoaded', function () {
    fetch('data_simple.json')
      .then((response) => response.json())
      .then((json) => {
        const cy = cytoscape({
          container: document.getElementById('cy'),
          style: json.style,
          elements: json.elements,
          layout: {
            name: 'dagre',
            rankDir: 'LR',
          }
        });
  
        // Add right-click behavior for nodes
        cy.on('cxttap', 'node', function (e) {
          const url = this.data('link');
          if (url) {
            window.open(url, '_blank');
          }
        });
  
        // Tooltip setup using Cytoscape-Popper
        cy.nodes().forEach(node => {
          const popperRef = node.popperRef(); // Ensure cytoscape-popper is included
          const tooltipContent = document.createElement('div');
          tooltipContent.textContent = node.data('label');
          document.body.appendChild(tooltipContent);
  
          const tip = tippy(tooltipContent, {
            content: node.data('label'),
            trigger: 'manual',
            arrow: true,
          });
  
          node.on('mouseover', () => {
            tip.setProps({ getReferenceClientRect: popperRef.getBoundingClientRect });
            tip.show();
          });
  
          node.on('mouseout', () => {
            tip.hide();
          });
        });
      })
      .catch((err) => {
        console.error('Error loading data:', err);
      });
  });
  