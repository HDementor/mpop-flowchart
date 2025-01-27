from flask import Flask, jsonify, request
from flask_cors import CORS
import networkx as nx
import pandas as pd
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File paths
CSV_FILE = os.path.join(os.getcwd(), 'data/mpop-tidytable.csv')
JSON_FILE = os.path.join(os.getcwd(), 'data/mpop-tidytable.json')
LOGS_DIR = os.path.join(os.getcwd(), 'backend/logs')

# Ensure the logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuration flags
logging_enabled = False
debug_enabled = True

# Valid CSS colors
COLOR_MAP = {
    'darkgrey': '#A9A9A9',
    'lightred': '#FFA07A',
    'lightbrown': '#D2B48C',
    'tanbrown': '#D2B48C',
    'lightblue': '#ADD8E6',
    'purple': '#90EE90',
    'yellow': '#FFFF00'
}

# Helper function to log responses
def log_response(api_call, response_data):
    if not logging_enabled:
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"response_{api_call}_{timestamp}.json")
    with open(log_file, 'w') as f:
        json.dump(response_data, f, indent=2)

# Helper function to print debug logs
def debug_log(message):
    if debug_enabled:
        print(f"DEBUG: {message}")

# Helper function to check if a node has trial_code descendants
# def does_node_have_trial_code_descendants(G, node):
#     for descendant in nx.descendants(G, node):
#         debug_log(f"Checking descendant node {descendant}")
#         if G.nodes[descendant]['type'] == 'trial_code':
#             debug_log(f"Node {node} has trial_code descendants")
#             return True
#     return False
def does_node_have_trial_code_descendants(G, node):
    debug_log(f"Checking if node {node} has trial_code descendants")
    if node not in G.nodes:
        debug_log(f"Node {node} does not exist in the graph.")
        return False

    try:
        for descendant in nx.descendants(G, node):
            debug_log(f"Checking descendant node {descendant}")
            if 'type' in G.nodes[descendant] and G.nodes[descendant]['type'] == 'trial_code':
                debug_log(f"Node {node} has trial_code descendants")
                return True
    except Exception as e:
        debug_log(f"Error while checking descendants for node {node}: {e}")
        return False

    debug_log(f"Node {node} has no trial_code descendants")
    return False


# Helper function to convert CSV to Cytoscape-compatible JSON format
def csv_to_cytoscape_json():
    try:
        debug_log(f"Attempting to read CSV file from: {CSV_FILE}")

        if not os.path.exists(CSV_FILE):
            debug_log("CSV file not found.")
            return {"error": "CSV file not found."}

        df = pd.read_csv(CSV_FILE)
        debug_log(f"CSV file read successfully. Columns: {list(df.columns)}")

        G = nx.DiGraph()

        # Build the graph from the CSV
        for _, row in df.iterrows():
            if pd.notna(row['oncology_category']):
                oncology_category_id = row['oncology_category']
                G.add_node(oncology_category_id, id=oncology_category_id, label=row['oncology_category'], type='oncology_category', color=COLOR_MAP['darkgrey'], outline='black', classes='')

            if pd.notna(row['study_type']):
                study_type_id = f"{row['study_type']}_{row['oncology_category']}"
                color = COLOR_MAP['lightbrown'] if row['study_type'] == 'Interventional' else COLOR_MAP['tanbrown']
                G.add_node(study_type_id, id=study_type_id, label=row['study_type'], type='study_type', color=color, outline='black', classes='hidden')

            if pd.notna(row['trial_phase']):
                trial_phase_id = f"{row['trial_phase']}_{row['study_type']}_{row['oncology_category']}"
                G.add_node(trial_phase_id, id=trial_phase_id, label=row['trial_phase'], type='trial_phase', color=COLOR_MAP['lightblue'], outline='black', classes='hidden')

            if pd.notna(row['therapy_line']):
                therapy_line_id = f"{row['therapy_line']}_{row['trial_phase']}_{row['study_type']}_{row['oncology_category']}"
                G.add_node(therapy_line_id, id=therapy_line_id, label=row['therapy_line'], type='therapy_line', color=COLOR_MAP['purple'], outline='black', classes='hidden')

            if pd.notna(row['trial_code']):
                trial_code_id = row['trial_code']  # Trial codes are not made unique
                # Use the hyperlink and trial description from the CSV
                hyperlink = row['hyperlink'] if pd.notna(row['hyperlink']) else 'https://default-link.com'
                trial_description = row['trial_description'] if pd.notna(row['trial_description']) else 'No description available'
                G.add_node(trial_code_id, id=trial_code_id, label=row['trial_code'], type='trial_code', color=COLOR_MAP['lightred'], outline='black', description=trial_description, hyperlink=hyperlink, classes='hidden')

            # Add edges
            if pd.notna(row['oncology_category']) and pd.notna(row['study_type']):
                G.add_edge(oncology_category_id, study_type_id, arrow=True, classes='hidden')
            if pd.notna(row['study_type']) and pd.notna(row['trial_phase']):
                G.add_edge(study_type_id, trial_phase_id, arrow=True, classes='hidden')
            if pd.notna(row['trial_phase']) and pd.notna(row['therapy_line']):
                G.add_edge(trial_phase_id, therapy_line_id, arrow=True, classes='hidden')
            if pd.notna(row['therapy_line']) and pd.notna(row['trial_code']):
                G.add_edge(therapy_line_id, trial_code_id, arrow=True, classes='hidden')

        # Convert NetworkX graph to Cytoscape-compatible format
        nodes = []
        edges = []

        for node, attr in G.nodes(data=True):
            classes = attr.pop('classes', '')  # Remove 'classes' from data
            nodes.append({"data": attr, "classes": classes})

        for source, target, attr in G.edges(data=True):
            classes = attr.pop('classes', '')  # Remove 'classes' from data
            edges.append({"data": {"source": source, "target": target, **attr}, "classes": classes})

        json_output = {"elements": {"nodes": nodes, "edges": edges}}
        debug_log(f"Generated JSON: {json.dumps(json_output, indent=2)}")

        return json_output

    except Exception as e:
        debug_log(f"Error in csv_to_cytoscape_json: {e}")
        return {"error": str(e)}

@app.route('/csv-to-json', methods=['GET'])
def convert_csv_to_json():
    try:
        data = csv_to_cytoscape_json()

        if "error" in data:
            debug_log("Error returned from csv_to_cytoscape_json.")
            return jsonify(message=data["error"]), 500

        debug_log(f"Writing JSON output to file: {JSON_FILE}")
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f)

        log_response('csv-to-json', data)
        return jsonify(message="CSV converted to Cytoscape-compatible JSON."), 200
    except Exception as e:
        log_response('csv-to-json', {"error": str(e)})
        debug_log(f"Exception in convert_csv_to_json: {e}")
        return jsonify(message=str(e)), 500

@app.route('/csv-to-json-stubbed', methods=['GET'])
def convert_csv_to_json_stubbed():
    try:
        data = csv_to_cytoscape_json_stubbed()

        if "error" in data:
            debug_log("Error returned from csv_to_cytoscape_json_stubbed.")
            return jsonify(message=data["error"]), 500

        debug_log(f"Writing JSON output to file: {JSON_FILE}")
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f)

        log_response('csv-to-json-stubbed', data)
        return jsonify(message="CSV converted to Cytoscape-compatible JSON with stubbing."), 200
    except Exception as e:
        log_response('csv-to-json-stubbed', {"error": str(e)})
        debug_log(f"Exception in convert_csv_to_json_stubbed: {e}")
        return jsonify(message=str(e)), 500

# Stubbed JSON helper function
def csv_to_cytoscape_json_stubbed():
    try:
        debug_log(f"Attempting to read CSV file from: {CSV_FILE}")

        if not os.path.exists(CSV_FILE):
            debug_log("CSV file not found.")
            return {"error": "CSV file not found."}

        df = pd.read_csv(CSV_FILE)
        debug_log(f"CSV file read successfully. Columns: {list(df.columns)}")

        G = nx.DiGraph()

        # Build the graph from the CSV
        for _, row in df.iterrows():
            if pd.notna(row['oncology_category']):
                oncology_category_id = row['oncology_category']
                G.add_node(oncology_category_id, id=oncology_category_id, label=row['oncology_category'], type='oncology_category', color=COLOR_MAP['darkgrey'], outline='black', classes='')

            if pd.notna(row['study_type']):
                study_type_id = f"{row['study_type']}_{row['oncology_category']}"
                color = COLOR_MAP['lightbrown'] if row['study_type'] == 'Interventional' else COLOR_MAP['tanbrown']
                G.add_node(study_type_id, id=study_type_id, label=row['study_type'], type='study_type', color=color, outline='black', classes='hidden')

            if pd.notna(row['trial_phase']):
                trial_phase_id = f"{row['trial_phase']}_{row['study_type']}_{row['oncology_category']}"
                #debug_log(f"Creating trial_phase node with columns: {row['trial_phase']}_{row['study_type']}_{row['oncology_category']}")
                G.add_node(trial_phase_id, id=trial_phase_id, label=row['trial_phase'], type='trial_phase', color=COLOR_MAP['lightblue'], outline='black', classes='hidden')
                #debug_log(f"Successfully Created trial_phase node with columns: {row['trial_phase']}_{row['study_type']}_{row['oncology_category']}")

            if pd.notna(row['therapy_line']):
                therapy_line_id = f"{row['therapy_line']}_{row['trial_phase']}_{row['study_type']}_{row['oncology_category']}"
                G.add_node(therapy_line_id, id=therapy_line_id, label=row['therapy_line'], type='therapy_line', color=COLOR_MAP['purple'], outline='black', classes='hidden')

            if pd.notna(row['trial_code']):
                trial_code_id = row['trial_code']  # Trial codes are not made unique
                # Use the hyperlink and trial description from the CSV
                hyperlink = row['hyperlink'] if pd.notna(row['hyperlink']) else 'https://default-link.com'
                trial_description = row['trial_description'] if pd.notna(row['trial_description']) else 'No description available'
                G.add_node(trial_code_id, id=trial_code_id, label=row['trial_code'], type='trial_code', color=COLOR_MAP['lightred'], outline='black', description=trial_description, hyperlink=hyperlink, classes='hidden')

            # Add edges
            if pd.notna(row['oncology_category']) and pd.notna(row['study_type']):
                G.add_edge(oncology_category_id, study_type_id, arrow=True, classes='hidden')
            if pd.notna(row['study_type']) and pd.notna(row['trial_phase']):
                #debug_log(f"Creating trial_phase edge with columns: {trial_phase_id}")
                G.add_edge(study_type_id, trial_phase_id, arrow=True, classes='hidden')
                #debug_log(f"Successfullly Created trial_phase edge with columns: {trial_phase_id}")
            if pd.notna(row['trial_phase']) and pd.notna(row['therapy_line']):
                #debug_log(f"Creating trial_phase edge with columns: {trial_phase_id}")
                G.add_edge(trial_phase_id, therapy_line_id, arrow=True, classes='hidden')
                #debug_log(f"Successfullly Created trial_phase edge with columns: {trial_phase_id}")
            if pd.notna(row['therapy_line']) and pd.notna(row['trial_code']):
                G.add_edge(therapy_line_id, trial_code_id, arrow=True, classes='hidden')

        # # Stub out branches without trial_codes
        # for node in list(G.nodes):
        #     debug_log(f"Checking node id {node}")
        #     if G.nodes[node]['type'] == 'trial_code':
        #         debug_log(f"Skipping trial_code node id {node}")
        #         continue
        #     debug_log(f"About to check if node id {node} has trial_code descendants")
        #     if not does_node_have_trial_code_descendants(G, node):
        #         debug_log(f"No trial codes found for node id {node}")
        #         no_trials_available_id = f"{node}_no_trials_available"
        #         G.add_node(no_trials_available_id, id=no_trials_available_id, label="No Trials", type='no_trials_available', color=COLOR_MAP['yellow'], outline='black', classes='hidden')

        #         # Remove all outbound edges from this node
        #         for _, target in list(G.out_edges(node)):
        #             debug_log(f"Removing edge from {node} to {target}")
        #             G.remove_node(target)
        #             debug_log(f"Removed edge from {node} to {target}")
        #         G.add_edge(node, no_trials_available_id, arrow=True, classes='hidden')

        removed_nodes = set()  # Track nodes that have been removed

        def remove_all_descendants(G, node):
            """Recursively remove all descendants of a given node."""
            for descendant in list(nx.descendants(G, node)):
                if descendant not in removed_nodes:
                    debug_log(f"Removing descendant node {descendant}")
                    G.remove_node(descendant)
                    removed_nodes.add(descendant)

        for node in list(G.nodes):
            if node in removed_nodes:
                debug_log(f"Skipping node {node} because it was removed earlier.")
                continue
            if G.nodes[node]['type'] == 'trial_code':
                continue
            if not does_node_have_trial_code_descendants(G, node):
                no_trials_available_id = f"{node}_no_trials_available"
                G.add_node(no_trials_available_id, id=no_trials_available_id, label="No Trials Available", type='no_trials_available', color=COLOR_MAP['yellow'], outline='black', classes='hidden')

                # Remove all outbound edges from this node and recursively remove descendants
                for _, target in list(G.out_edges(node)):
                    debug_log(f"Removing edge from {node} to {target}")
                    remove_all_descendants(G, target)  # Remove all downstream nodes
                    G.remove_node(target)  # Remove the immediate target node
                    removed_nodes.add(target)
                G.add_edge(node, no_trials_available_id, arrow=True, classes='hidden')

        # Convert NetworkX graph to Cytoscape-compatible format
        nodes = []
        edges = []

        for node, attr in G.nodes(data=True):
            classes = attr.pop('classes', '')  # Remove 'classes' from data
            nodes.append({"data": attr, "classes": classes})

        for source, target, attr in G.edges(data=True):
            classes = attr.pop('classes', '')  # Remove 'classes' from data
            edges.append({"data": {"source": source, "target": target, **attr}, "classes": classes})

        json_output = {"elements": {"nodes": nodes, "edges": edges}}
        debug_log(f"Generated Stubbed JSON: {json.dumps(json_output, indent=2)}")

        return json_output

    except Exception as e:
        #debug_log(f"Error in csv_to_cytoscape_json_stubbed: {e}")
        debug_log(f"Error processing node {node}: {str(e)}")
        return {"error": str(e)}

@app.route('/oncology_category/<category_name>', methods=['GET'])
def get_oncology_category(category_name):
    try:
        debug_log(f"Fetching oncology category: {category_name}")

        if not os.path.exists(JSON_FILE):
            debug_log("JSON file not found. Aborting.")
            error_response = {"message": "JSON file not found. Please convert CSV first."}
            log_response(f'oncology_category_{category_name}', error_response)
            return jsonify(error_response), 400

        with open(JSON_FILE, 'r') as f:
            data = json.load(f)

        if category_name == 'All':
            log_response('oncology_category_All', data)
            return jsonify(data), 200

        if category_name == 'All_fully_expanded':
            log_response('oncology_category_All_fully_expanded', data)
            return jsonify(data), 200

        if category_name == 'Tumor_Agnostic':
            category_name = 'Tumor Agnostic'
        else:
            category_name = category_name.replace('_', '/')

        filtered_nodes = set()
        filtered_edges = []

        for element in data['elements']['edges']:
            if category_name in element['data']['source']:
                filtered_edges.append(element)
                filtered_nodes.add(element['data']['source'])
                filtered_nodes.add(element['data']['target'])

        filtered_elements = {
            "elements": {
                "nodes": [
                    el for el in data['elements']['nodes']
                    if el['data']['id'] in filtered_nodes
                ],
                "edges": filtered_edges
            }
        }
        log_response(f'oncology_category_{category_name}', filtered_elements)
        return jsonify(filtered_elements), 200

    except Exception as e:
        error_response = {"message": str(e)}
        log_response(f'oncology_category_{category_name}', error_response)
        debug_log(f"Exception in get_oncology_category: {e}")
        return jsonify(error_response), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999)
