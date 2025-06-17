#!/usr/bin/env python3
"""Basic test of DFT functionality without external dependencies"""

import sys
from pathlib import Path

# Add dft to path
sys.path.insert(0, str(Path(__file__).parent))

def test_pipeline_structure():
    """Test basic pipeline structure"""
    from dft.core.pipeline_simple import SimplePipeline, SimplePipelineStep
    
    # Create test steps
    step1 = SimplePipelineStep(
        id="extract",
        type="source",
        config={"source_type": "csv", "file_path": "test.csv"}
    )
    
    step2 = SimplePipelineStep(
        id="validate", 
        type="processor",
        config={"processor_type": "validator"},
        depends_on=["extract"]
    )
    
    step3 = SimplePipelineStep(
        id="save",
        type="endpoint", 
        config={"endpoint_type": "csv", "file_path": "output.csv"},
        depends_on=["validate"]
    )
    
    # Create pipeline
    pipeline = SimplePipeline(
        name="test_pipeline",
        steps=[step1, step2, step3],
        tags=["test"]
    )
    
    # Test basic functionality
    assert pipeline.name == "test_pipeline"
    assert len(pipeline.steps) == 3
    assert pipeline.has_tag("test")
    
    # Test step retrieval
    step = pipeline.get_step("extract")
    assert step is not None
    assert step.id == "extract"
    
    # Test dependency resolution
    deps = pipeline.get_dependencies("validate")
    assert len(deps) == 1
    assert deps[0].id == "extract"
    
    # Test execution order
    order = pipeline.get_execution_order()
    assert order == ["extract", "validate", "save"]
    
    print("✅ Pipeline structure tests passed")


def test_data_packet():
    """Test DataPacket without pyarrow"""
    from dft.core.data_packet_simple import SimpleDataPacket
    from datetime import datetime
    
    # Create simple test data packet without pyarrow
    packet = SimpleDataPacket(
        data=None,  # Skip pyarrow for now
        metadata={"test": "value"},
        timestamp=datetime.now(),
        source="test"
    )
    
    assert packet.source == "test"
    assert packet.metadata["test"] == "value"
    assert packet.row_count == 0  # None data should return 0
    
    # Test metadata functions
    packet.add_metadata("new_key", "new_value")
    assert packet.get_metadata("new_key") == "new_value"
    assert packet.get_metadata("missing", "default") == "default"
    
    print("✅ DataPacket tests passed")


def test_yaml_config():
    """Test YAML configuration loading"""
    import yaml
    from pathlib import Path
    
    # Test pipeline YAML structure
    yaml_content = """
pipeline_name: test_pipeline
tags: [test, example]
depends_on: []

steps:
  - id: extract_data
    type: source
    source_type: csv
    config:
      file_path: "data.csv"
  
  - id: process_data
    type: processor
    processor_type: validator
    depends_on: [extract_data]
    config:
      required_columns: [id, name]
"""
    
    config = yaml.safe_load(yaml_content)
    
    assert config["pipeline_name"] == "test_pipeline"
    assert "test" in config["tags"]
    assert len(config["steps"]) == 2
    assert config["steps"][0]["id"] == "extract_data"
    assert config["steps"][1]["depends_on"] == ["extract_data"]
    
    print("✅ YAML configuration tests passed")


def main():
    """Run all tests"""
    print("🧪 Running DFT basic tests...")
    print()
    
    try:
        test_pipeline_structure()
        test_data_packet()
        test_yaml_config()
        
        print()
        print("🎉 All basic tests passed!")
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Test full functionality with: python -m dft.cli.main init test_project")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()