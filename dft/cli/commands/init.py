"""Initialize DFT project command"""

import click
from pathlib import Path


def init_project(project_name: str, pipelines_dir: str) -> None:
    """Initialize a new DFT project"""
    
    project_path = Path(project_name)
    
    if project_path.exists():
        click.echo(f"Error: Directory '{project_name}' already exists")
        return
    
    try:
        # Create project structure
        project_path.mkdir()
        (project_path / pipelines_dir).mkdir()
        (project_path / "tests").mkdir()
        (project_path / "output").mkdir()  # Create output directory
        (project_path / ".dft").mkdir()
        (project_path / ".dft" / "logs").mkdir()  # Create logs directory
        
        # Create dft_project.yml
        project_config = f"""# DFT Project Configuration
project_name: {project_name}
version: '1.0'

# Pipeline configuration
pipelines_dir: {pipelines_dir}

# Default variables
vars:
  target: dev

# State management configuration
state:
  # Whether to ignore state files in git (recommended for development)
  # Set to false for production/GitOps workflows where state should be versioned
  ignore_in_git: true

# Database and service connections (use environment variables for secrets)
connections:
  postgres_default:
    type: postgresql
    host: "{{{{ env_var('DB_HOST', 'localhost') }}}}"
    port: "{{{{ env_var('DB_PORT', '5432') }}}}"
    database: "{{{{ env_var('DB_NAME', 'analytics') }}}}"
    user: "{{{{ env_var('DB_USER', 'postgres') }}}}"
    password: "{{{{ env_var('DB_PASSWORD', '') }}}}"

# Logging configuration
logging:
  level: INFO
  dir: .dft/logs
"""
        
        (project_path / "dft_project.yml").write_text(project_config)
        
        # Create example pipeline
        example_pipeline = f"""# Example pipeline configuration
pipeline_name: example_pipeline
tags: [example, daily]

steps:
  - id: extract_data
    type: source
    source_type: csv
    config:
      file_path: "data/sample.csv"
  
  - id: validate_data
    type: processor
    processor_type: validator
    depends_on: [extract_data]
    config:
      required_columns: [id, name]
      row_count_min: 1
  
  - id: save_results
    type: endpoint
    endpoint_type: csv
    depends_on: [validate_data]
    config:
      file_path: "output/processed_{{{{ today() }}}}.csv"
"""
        
        (project_path / pipelines_dir / "example_pipeline.yml").write_text(example_pipeline)
        
        # Create .env template
        env_template = """# Environment variables for DFT project
# Copy this file to .env and fill in your values

# Database connections
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analytics
DB_USER=postgres
DB_PASSWORD=your_password_here

# API keys
SLACK_TOKEN=xoxb-your-slack-token
API_KEY=your_api_key_here
"""
        
        (project_path / ".env.example").write_text(env_template)
        
        # Create sample data directory
        (project_path / "data").mkdir()
        
        # Create gitignore - will be updated based on state config
        gitignore = """.dft/logs/
.env
output/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
"""
        
        # Add state to gitignore based on config (default is ignore_in_git: true)
        gitignore += ".dft/state/\n"
        
        (project_path / ".gitignore").write_text(gitignore)
        
        # Update gitignore based on state configuration
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(project_path)
            from .gitignore import update_gitignore_for_state
            from dft.core.config import ProjectConfig
            
            project_config = ProjectConfig("dft_project.yml")
            update_gitignore_for_state(project_config)
        except Exception as e:
            click.echo(f"Warning: Could not update gitignore for state config: {e}")
        finally:
            os.chdir(old_cwd)
        
        click.echo(f"✅ DFT project '{project_name}' initialized successfully!")
        click.echo(f"📁 Created directory structure:")
        click.echo(f"   {project_name}/")
        click.echo(f"   ├── dft_project.yml")
        click.echo(f"   ├── {pipelines_dir}/")
        click.echo(f"   │   └── example_pipeline.yml")
        click.echo(f"   ├── tests/")
        click.echo(f"   ├── data/")
        click.echo(f"   ├── output/")
        click.echo(f"   ├── .dft/")
        click.echo(f"   ├── .env.example")
        click.echo(f"   └── .gitignore")
        click.echo()
        click.echo(f"Next steps:")
        click.echo(f"1. cd {project_name}")
        click.echo(f"2. cp .env.example .env  # and fill in your credentials")
        click.echo(f"3. dft run --select example_pipeline")
        
    except Exception as e:
        click.echo(f"Error creating project: {e}")
        # Cleanup on error
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)