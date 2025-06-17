"""Run pipelines command"""

import click
from pathlib import Path
from typing import Optional


def run_pipelines(
    select: Optional[str], 
    exclude: Optional[str], 
    vars: Optional[str], 
    full_refresh: bool
) -> None:
    """Run DFT pipelines with automatic dependency resolution.
    
    Pipelines are automatically executed in dependency order.
    
    Selection syntax:
    - pipeline_name: Run specific pipeline
    - tag:tagname: Run pipelines with tag
    - +pipeline_name: Run upstream dependencies of pipeline
    - pipeline_name+: Run downstream dependencies of pipeline  
    - +pipeline_name+: Run pipeline with all dependencies
    - Multiple selectors can be combined with commas
    """
    
    # Check if we're in a DFT project
    if not Path("dft_project.yml").exists():
        click.echo("Error: Not in a DFT project directory. Run 'dft init' first.")
        return
    
    try:
        from ...core.runner import PipelineRunner
        
        # Parse variables from command line
        variables = {}
        if vars:
            for var_pair in vars.split(","):
                if "=" in var_pair:
                    key, value = var_pair.split("=", 1)
                    variables[key.strip()] = value.strip()
        
        # Create and run pipeline runner
        runner = PipelineRunner()
        success = runner.run(
            select=select,
            exclude=exclude,
            variables=variables,
            full_refresh=full_refresh
        )
        
        if success:
            click.echo("✅ All pipelines completed successfully!")
        else:
            click.echo("❌ Some pipelines failed. Check logs for details.")
            exit(1)
            
    except Exception as e:
        click.echo(f"Error running pipelines: {e}")
        exit(1)