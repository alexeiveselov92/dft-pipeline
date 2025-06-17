"""Documentation command for DFT"""

import click
from pathlib import Path
from datetime import datetime


def generate_docs(serve: bool) -> None:
    """Generate and optionally serve documentation"""
    
    if not Path("dft_project.yml").exists():
        click.echo("Error: Not in a DFT project directory. Run 'dft init' first.")
        return
    
    try:
        from ...core.config import ProjectConfig, PipelineLoader
        
        project_config = ProjectConfig()
        pipeline_loader = PipelineLoader(project_config)
        
        pipelines = pipeline_loader.load_all_pipelines()
        
        # Create docs directory
        docs_dir = Path(".dft/docs")
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML documentation
        html_content = generate_html_docs(project_config, pipelines)
        
        docs_file = docs_dir / "index.html"
        docs_file.write_text(html_content, encoding='utf-8')
        
        click.echo(f"📚 Documentation generated: {docs_file}")
        
        if serve:
            click.echo("🌐 Starting documentation server...")
            import webbrowser
            import http.server
            import socketserver
            import os
            
            os.chdir(docs_dir)
            
            PORT = 8080
            Handler = http.server.SimpleHTTPRequestHandler
            
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                click.echo(f"📖 Documentation available at: http://localhost:{PORT}")
                webbrowser.open(f"http://localhost:{PORT}")
                
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    click.echo("\n📚 Documentation server stopped")
        
    except Exception as e:
        click.echo(f"Error generating docs: {e}")


def generate_html_docs(project_config, pipelines) -> str:
    """Generate HTML documentation"""
    
    # Generate dependency graph data
    graph_data = generate_dependency_graph(pipelines)
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{project_config.project_name} - DFT Documentation</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            background: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header h1 {{ margin: 0; font-size: 2.5rem; }}
        .header p {{ margin: 0.5rem 0 0 0; opacity: 0.9; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        .tab {{
            flex: 1;
            padding: 1rem 2rem;
            cursor: pointer;
            border: none;
            background: white;
            font-size: 1rem;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}
        .tab:hover {{ background: #f8f9fa; }}
        .tab.active {{ 
            background: #667eea; 
            color: white; 
            border-bottom-color: #4c63d2;
        }}
        
        /* Tab content */
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        /* Pipeline cards */
        .pipeline {{ 
            background: white; 
            border-radius: 8px; 
            margin: 1.5rem 0; 
            padding: 1.5rem; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .pipeline:hover {{ transform: translateY(-2px); }}
        .pipeline h3 {{ 
            margin-top: 0; 
            color: #2d3748; 
            border-bottom: 2px solid #e2e8f0; 
            padding-bottom: 0.5rem;
        }}
        .step {{ 
            margin: 0.75rem 0; 
            padding: 1rem; 
            background: linear-gradient(to right, #f7fafc, #edf2f7); 
            border-radius: 6px; 
            border-left: 4px solid #667eea;
        }}
        .tags {{ 
            color: #718096; 
            font-size: 0.9em; 
            margin: 0.5rem 0;
        }}
        .tags .tag {{
            background: #e2e8f0;
            color: #4a5568;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
            margin-right: 0.5rem;
        }}
        .depends {{ color: #e53e3e; font-weight: 500; }}
        
        /* Graph styles */
        .graph-container {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .graph-node {{
            fill: #667eea;
            stroke: #4c63d2;
            stroke-width: 2;
        }}
        .graph-text {{ 
            fill: white; 
            font-size: 12px; 
            text-anchor: middle; 
            dominant-baseline: middle;
        }}
        .graph-edge {{ 
            stroke: #a0aec0; 
            stroke-width: 2; 
            marker-end: url(#arrowhead);
        }}
        
        /* Stats */
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #718096; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {project_config.project_name}</h1>
        <p>DFT Project Documentation - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(pipelines)}</div>
                <div class="stat-label">Pipelines</div>
            </div>
            <div class="stat">
                <div class="stat-number">{sum(len(p.steps) for p in pipelines)}</div>
                <div class="stat-label">Total Steps</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len([p for p in pipelines if p.depends_on])}</div>
                <div class="stat-label">With Dependencies</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('pipelines')">📋 Pipelines</button>
            <button class="tab" onclick="showTab('graph')">🔗 Dependencies</button>
            <button class="tab" onclick="showTab('overview')">📊 Overview</button>
        </div>
        
        <div id="pipelines" class="tab-content active">
"""
    
    for pipeline in pipelines:
        tags_html = ""
        if pipeline.tags:
            tags_html = '<div class="tags">' + ''.join([f'<span class="tag">{tag}</span>' for tag in pipeline.tags]) + '</div>'
        
        depends_html = ""
        if pipeline.depends_on:
            depends_html = f'<div class="depends">⚠️ Depends on: {", ".join(pipeline.depends_on)}</div>'
        
        html += f"""
    <div class="pipeline">
        <h3>🔄 {pipeline.name}</h3>
        {tags_html}
        {depends_html}
        
        <h4>Steps ({len(pipeline.steps)}):</h4>
"""
        
        for step in pipeline.steps:
            depends = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
            
            # Get the specific type
            step_type = ""
            if step.source_type:
                step_type = f"<br><em>Source: {step.source_type}</em>"
            elif step.processor_type:
                step_type = f"<br><em>Processor: {step.processor_type}</em>"
            elif step.endpoint_type:
                step_type = f"<br><em>Endpoint: {step.endpoint_type}</em>"
            
            html += f"""
        <div class="step">
            <strong>{step.id}</strong> - {step.type}{depends}
            {step_type}
        </div>
"""
        
        html += "</div>"
    
    html += """
        </div>
        
        <div id="graph" class="tab-content">
            <div class="graph-container">
                <h2>🔗 Pipeline Dependencies</h2>
                <p>Visual representation of pipeline dependencies and data flow</p>
                
                <div style="margin: 1rem 0; text-align: left;">
                    <label for="pipeline-selector" style="font-weight: 500; margin-right: 1rem;">Focus on pipeline:</label>
                    <select id="pipeline-selector" onchange="updateGraph()" style="padding: 0.5rem; border-radius: 4px; border: 1px solid #e2e8f0;">
                        <option value="all">All Pipelines</option>""" + ''.join([f'<option value="{p.name}">{p.name}</option>' for p in pipelines]) + """
                    </select>
                </div>
                
                <div id="graph-svg-container">
                    <svg width="800" height="500" viewBox="0 0 800 500" id="dependency-graph">
                        <defs>
                            <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                             refX="9" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="#a0aec0" />
                            </marker>
                        </defs>
                        <g id="graph-content">
                            """ + graph_data + """
                        </g>
                    </svg>
                </div>
                
                <div style="margin-top: 1rem; text-align: left; font-size: 0.9rem; color: #718096;">
                    <h4>Legend:</h4>
                    <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
                        <div><span style="display: inline-block; width: 12px; height: 12px; background: #667eea; border-radius: 2px; margin-right: 0.5rem;"></span>Pipeline</div>
                        <div><span style="display: inline-block; width: 20px; height: 2px; background: #a0aec0; margin-right: 0.5rem; position: relative; top: 5px;"></span>Dependency</div>
                        <div><span style="color: #e53e3e;">●</span> Selected pipeline and dependencies</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="overview" class="tab-content">
            <div class="graph-container">
                <h2>📊 Project Overview</h2>
                <div style="text-align: left; max-width: 600px; margin: 0 auto;">
                    <h3>🏗️ Architecture</h3>
                    <p>This DFT project contains <strong>{len(pipelines)} pipelines</strong> with a total of <strong>{sum(len(p.steps) for p in pipelines)} steps</strong>.</p>
                    
                    <h3>📈 Pipeline Types</h3>
                    <ul>
                        <li><strong>Independent:</strong> {len([p for p in pipelines if not p.depends_on])} pipelines</li>
                        <li><strong>Dependent:</strong> {len([p for p in pipelines if p.depends_on])} pipelines</li>
                    </ul>
                    
                    <h3>🔧 Step Types</h3>
                    <ul>
                        <li><strong>Sources:</strong> {sum(len([s for s in p.steps if s.type == 'source']) for p in pipelines)}</li>
                        <li><strong>Processors:</strong> {sum(len([s for s in p.steps if s.type == 'processor']) for p in pipelines)}</li>
                        <li><strong>Endpoints:</strong> {sum(len([s for s in p.steps if s.type == 'endpoint']) for p in pipelines)}</li>
                    </ul>
                    
                    <h3>🏷️ Tags</h3>
                    <p>Common tags: {', '.join(sorted(set(tag for p in pipelines for tag in p.tags)))}</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Pipeline data for graph filtering
        const pipelinesData = """ + generate_pipeline_json(pipelines) + """;
        
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
        
        function updateGraph() {
            const selectedPipeline = document.getElementById('pipeline-selector').value;
            const graphContent = document.getElementById('graph-content');
            
            if (selectedPipeline === 'all') {
                // Show all pipelines
                generateFullGraph();
            } else {
                // Show focused view
                generateFocusedGraph(selectedPipeline);
            }
        }
        
        function generateFullGraph() {
            const graphContent = document.getElementById('graph-content');
            graphContent.innerHTML = `""" + graph_data.replace('`', '\\`') + """`;
        }
        
        function generateFocusedGraph(pipelineName) {
            const pipeline = pipelinesData.find(p => p.name === pipelineName);
            if (!pipeline) return;
            
            // Find all related pipelines (upstream and downstream)
            const relatedPipelines = new Set([pipelineName]);
            
            // Add upstream dependencies
            if (pipeline.depends_on) {
                pipeline.depends_on.forEach(dep => relatedPipelines.add(dep));
            }
            
            // Add downstream dependencies
            pipelinesData.forEach(p => {
                if (p.depends_on && p.depends_on.includes(pipelineName)) {
                    relatedPipelines.add(p.name);
                }
            });
            
            // Generate focused graph
            let focusedGraph = '';
            const positions = {};
            const relatedList = Array.from(relatedPipelines);
            
            // Simple vertical layout for focused view
            relatedList.forEach((name, index) => {
                const x = 400; // Center horizontally
                const y = 100 + index * 100;
                positions[name] = {x, y};
            });
            
            // Draw edges
            relatedList.forEach(name => {
                const p = pipelinesData.find(p => p.name === name);
                if (p && p.depends_on) {
                    p.depends_on.forEach(dep => {
                        if (positions[dep] && positions[name]) {
                            const x1 = positions[dep].x;
                            const y1 = positions[dep].y + 25;
                            const x2 = positions[name].x;
                            const y2 = positions[name].y - 25;
                            focusedGraph += `<line class="graph-edge" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" />`;
                        }
                    });
                }
            });
            
            // Draw nodes
            relatedList.forEach(name => {
                const pos = positions[name];
                const isSelected = name === pipelineName;
                const nodeColor = isSelected ? '#e53e3e' : '#667eea';
                const strokeColor = isSelected ? '#c53030' : '#4c63d2';
                
                focusedGraph += `<rect class="graph-node" fill="${nodeColor}" stroke="${strokeColor}" x="${pos.x-80}" y="${pos.y-15}" width="160" height="30" rx="15" />`;
                focusedGraph += `<text class="graph-text" x="${pos.x}" y="${pos.y}">${name.length > 20 ? name.substring(0, 20) + '...' : name}</text>`;
            });
            
            document.getElementById('graph-content').innerHTML = focusedGraph;
        }
    </script>
</body>
</html>
"""
    
    return html


def generate_dependency_graph(pipelines) -> str:
    """Generate SVG dependency graph"""
    
    # Simple layout - place pipelines in a grid
    graph_svg = ""
    positions = {}
    
    # Calculate positions
    independent = [p for p in pipelines if not p.depends_on]
    dependent = [p for p in pipelines if p.depends_on]
    
    # Position independent pipelines at the top
    x_start = 100
    y_start = 100
    x_spacing = 150
    y_spacing = 100
    
    for i, pipeline in enumerate(independent):
        x = x_start + (i % 4) * x_spacing
        y = y_start + (i // 4) * y_spacing
        positions[pipeline.name] = (x, y)
    
    # Position dependent pipelines below
    for i, pipeline in enumerate(dependent):
        x = x_start + (i % 4) * x_spacing
        y = y_start + 200 + (i // 4) * y_spacing
        positions[pipeline.name] = (x, y)
    
    # Draw edges (dependencies)
    for pipeline in pipelines:
        if pipeline.depends_on:
            for dep in pipeline.depends_on:
                if dep in positions:
                    x1, y1 = positions[dep]
                    x2, y2 = positions[pipeline.name]
                    graph_svg += f'<line class="graph-edge" x1="{x1}" y1="{y1+25}" x2="{x2}" y2="{y2-25}" />'
    
    # Draw nodes
    for pipeline_name, (x, y) in positions.items():
        # Node background
        graph_svg += f'<rect class="graph-node" x="{x-60}" y="{y-15}" width="120" height="30" rx="15" />'
        # Node text
        display_name = pipeline_name[:15] + "..." if len(pipeline_name) > 15 else pipeline_name
        graph_svg += f'<text class="graph-text" x="{x}" y="{y}">{display_name}</text>'
    
    return graph_svg


def generate_pipeline_json(pipelines) -> str:
    """Generate JSON data for JavaScript"""
    import json
    
    pipeline_data = []
    for pipeline in pipelines:
        pipeline_data.append({
            'name': pipeline.name,
            'depends_on': pipeline.depends_on if pipeline.depends_on else [],
            'tags': pipeline.tags if pipeline.tags else []
        })
    
    return json.dumps(pipeline_data)