"""Documentation command for DFT"""

import click
from pathlib import Path


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
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{project_config.project_name} - DFT Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .pipeline {{ border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 5px; }}
        .step {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 3px; }}
        .tags {{ color: #666; font-size: 0.9em; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>📊 {project_config.project_name}</h1>
    <p><strong>DFT Project Documentation</strong></p>
    
    <h2>📋 Pipelines ({len(pipelines)})</h2>
"""
    
    for pipeline in pipelines:
        html += f"""
    <div class="pipeline">
        <h3>🔄 {pipeline.name}</h3>
        
        {f'<div class="tags">Tags: {", ".join(pipeline.tags)}</div>' if pipeline.tags else ''}
        {f'<div>Depends on: {", ".join(pipeline.depends_on)}</div>' if pipeline.depends_on else ''}
        
        <h4>Steps:</h4>
"""
        
        for step in pipeline.steps:
            depends = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
            
            # Get the specific type
            step_type = ""
            if step.source_type:
                step_type = f"<br>Source: {step.source_type}"
            elif step.processor_type:
                step_type = f"<br>Processor: {step.processor_type}"
            elif step.endpoint_type:
                step_type = f"<br>Endpoint: {step.endpoint_type}"
            
            html += f"""
        <div class="step">
            <strong>{step.id}</strong> - {step.type}{depends}
            {step_type}
        </div>
"""
        
        html += "</div>"
    
    html += """
</body>
</html>
"""
    
    return html