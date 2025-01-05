
# Dynamic Flowchart (using javascript)

This repository contains a dynamic flowchart (graph)

## Getting Started

1. **Clone or download** this repository to your local machine:
   ```bash
   git clone https://github.com/your-username/dynamic-flowchart.git
   ```

2. **Install a local development server with auto-reload.** 
   
   1. Ensure you have [Node.js](https://nodejs.org/) installed.  
   2. In your project folder, initialize an npm project if you haven’t already:
      ```bash
      cd dynamic-flowchart
      npm init -y
      ```
   3. Install **live-server** as a dev dependency:
      ```bash
      npm install live-server --save-dev
      ```
   4. Start **live-server** via `npx`:
      ```bash
      npx live-server
      ```
      This will open your browser at `http://127.0.0.1:8080`, loading `index.html`.
   

3. You should see the Cytoscape graph with nodes and edges defined in `data.json`.

## Updating the Graph

- If you edit `data.json` or any of the files, the page should automatically reload if using **live-server**. Otherwise, you can manually refresh the page.

## Hosting on GitHub Pages

You can easily host this static site on **GitHub Pages**:

1. Commit your changes and push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```
2. Go to your repository **Settings** on GitHub.  
3. Under **"Pages"** (or **"Pages and Branches"**), select the **branch** you want to deploy from (typically `main`) and choose the root folder (`/`).  
4. Wait a few seconds; GitHub Pages will provide a URL like:
   ```
   https://your-username.github.io/dynamic-flowchart/
   ```
5. Navigate to that URL, and you’ll see your app!

> **Note**: Because everything is static and in the same repository, you shouldn’t run into cross-origin request issues. However, if you do, consider placing all static data and files in the same GitHub Pages environment.
