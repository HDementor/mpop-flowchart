document.addEventListener('DOMContentLoaded', () => {
  const cyContainer = document.getElementById('cy');
  const logsContainer = document.getElementById('logs');
  const renderGraphBtn = document.getElementById('render-graph');
  const convertCsvBtn = document.getElementById('convert-csv');
  const clearLogsBtn = document.getElementById('clear-logs'); // New button
  const categorySelect = document.getElementById('oncology-category');

  const BACKEND_URL = 'http://127.0.0.1:9999';

  let cy;

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async function sleep_and_log() {
    console.log("Start");
    await sleep(2000); // Wait for 2 seconds
    console.log("End"); 
  }
  const logMessage = (message) => {
    const logEntry = document.createElement('div');
    logEntry.textContent = message;
    logsContainer.appendChild(logEntry);
    console.log(message);
    logsContainer.scrollTop = logsContainer.scrollHeight; // Auto-scroll to the latest log
  };

  // Clear Logs Button
  clearLogsBtn.addEventListener('click', () => {
    logsContainer.innerHTML = '';
    console.log('Logs cleared.'); // Optional debugging log
  });

  // Function to process CSV-to-JSON conversion
  const convertCsvToJson = () => {
    logMessage('Converting CSV to JSON with updated unique IDs...');

    fetch(`${BACKEND_URL}/csv-to-json`)
      .then((response) => {
        logMessage(`Response status: ${response.status}`);
        logMessage('CSV-to-JSON conversion completed.');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .catch((err) => {
        logMessage(`Error converting CSV: ${err.message}`);
        console.error('Error details:', err);
      });
  };

  const renderGraph = (data) => {
    logMessage('API Response Data: ' + JSON.stringify(data, null, 2));

    if (!data || !data.elements || !data.elements.nodes || !data.elements.edges) {
      logMessage('Error: Invalid data received.');
      return;
    }

    const elements = [
      ...data.elements.nodes.map(node => ({
        data: {
          ...node.data,
          label: node.data.label.replace(/\//g, '/ '), // Insert space after '/' for wrapping
        },
        classes: categorySelect.value === 'All' && node.data.type !== 'oncology_category' ? 'hidden' : ''
      })),
      ...data.elements.edges.map(edge => ({
        data: edge.data,
        classes: categorySelect.value === 'All' ? 'hidden' : ''
      }))
    ];

    if (categorySelect.value === 'All_fully_expanded') {
      elements.forEach(element => {
        element.classes = '';
      });
    }

    cy = cytoscape({
      container: cyContainer,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'shape': 'round-rectangle',
            'background-color': 'data(color)',
            'border-color': 'data(outline)',
            'label': 'data(label)',
            'text-valign': 'center',
            'font-size': '12px',
            'padding': '10px',
            "width": 100,
            "height": 40,
            "text-wrap": "wrap",
            "text-max-width": "90px",
            "color": "#000",
            "border-width": 1
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#ccc',
            'arrow-scale': 1.2,
            'curve-style': 'bezier'
          }
        },
        {
          "selector": ".hidden",
          "style": {
            "display": "none"
          }
        }
      ],
      layout: {
        name: 'dagre',
        rankDir: 'LR',
        nodeSep: 20,
        edgeSep: 10,
        rankSep: 20
      }
    });

    cy.on('mouseover', 'node[type="trial_code"]', function (evt) {
      const node = evt.target;
      const description = node.data('description');
      const tooltip = document.createElement('div');
      tooltip.id = 'tooltip';
      tooltip.textContent = description;
      tooltip.style.position = 'absolute';
      tooltip.style.left = evt.originalEvent.pageX + 'px';
      tooltip.style.top = evt.originalEvent.pageY + 'px';
      tooltip.style.padding = '5px';
      tooltip.style.backgroundColor = '#fff';
      tooltip.style.border = '1px solid #000';
      tooltip.style.zIndex = 1000;
      document.body.appendChild(tooltip);
    });

    cy.on('mouseout', 'node[type="trial_code"]', function () {
      const tooltip = document.getElementById('tooltip');
      if (tooltip) {
        tooltip.remove();
      }
    });

    cy.on('cxttap', 'node[type="trial_code"]', function (e) {
      const hyperlink = this.data('hyperlink');
      if (hyperlink) {
        window.open(hyperlink, '_blank');
      }
    });

    cy.on('tap', 'node', (evt) => {
      const nodeId = evt.target.id();
      logMessage(`Node clicked: ${nodeId}`);

      const clickedNode = cy.getElementById(nodeId);

      if (clickedNode) {
        logMessage(`Handling click for node: ${nodeId}`);
        toggleDownstream(nodeId);
      }
    });

    logMessage('Updated Cytoscape Data: ' + JSON.stringify(elements, null, 2));
  };

  renderGraphBtn.addEventListener('click', () => {
    const category = categorySelect.value;
    logMessage(`Fetching data for category: ${category}`);
    fetch(`${BACKEND_URL}/oncology_category/${category}`)
      .then((response) => {
        logMessage(`Response status: ${response.status}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (data && typeof data === 'object') {
          sleep_and_log();
          renderGraph(data);
          logMessage(`Rendered graph for category: ${category}`);
        } else {
          logMessage('Error: Unexpected response format.');
        }
      })
      .catch((err) => {
        logMessage(`Error rendering graph: ${err.message}`);
        console.error('Error details:', err);
      });
  });

  convertCsvBtn.addEventListener('click', convertCsvToJson);
});
