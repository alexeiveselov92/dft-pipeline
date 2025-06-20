# 🔌 Custom Components Development Guide

DFT supports a powerful plugin system that allows you to create custom sources, processors, and endpoints directly in your project. This guide provides comprehensive information for analysts and developers who want to extend DFT with custom functionality.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)  
- [Development Workflow](#development-workflow)
- [Sources API](#sources-api)
- [Processors API](#processors-api)
- [Endpoints API](#endpoints-api)
- [Data Packet Structure](#data-packet-structure)
- [Best Practices](#best-practices)
- [Testing Custom Components](#testing-custom-components)
- [Advanced Patterns](#advanced-patterns)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

The plugin system allows you to:
- **Create custom data sources** for any API, database, or file format
- **Build custom processors** for domain-specific transformations, ML models, or validation
- **Develop custom endpoints** for specialized output formats or destinations
- **Extend the component library** without modifying the core DFT codebase
- **Share components** across projects and teams

### Auto-Discovery System

Components are automatically discovered from your project's `dft/` directory:
- No registration required
- Snake case naming (`MyCustomSource` → `my_custom`)
- Available immediately after creation
- Integrates seamlessly with existing pipelines

## 📁 Project Structure

When you run `dft init`, the following structure is created:

```
my_project/
├── dft/                           # Custom components directory
│   ├── __init__.py               # Package initialization
│   ├── sources/                  # Custom data sources
│   │   ├── __init__.py
│   │   └── my_custom_source.py   # Example source
│   ├── processors/               # Custom data processors
│   │   ├── __init__.py
│   │   └── my_custom_processor.py # Example processor
│   └── endpoints/                # Custom data endpoints
│       ├── __init__.py
│       └── my_custom_endpoint.py  # Example endpoint
├── pipelines/
│   └── custom_example_pipeline.yml # Example using custom components
└── ...
```

## 🔧 Development Workflow

### 1. Create Component File

```bash
# Create a new source
touch dft/sources/api_source.py

# Create a new processor  
touch dft/processors/data_transformer.py

# Create a new endpoint
touch dft/endpoints/webhook_sender.py
```

### 2. Implement Component Class

Each component must inherit from the appropriate base class and implement required methods.

### 3. Use in Pipeline

Components are automatically available using snake_case naming:

```yaml
steps:
  - id: my_step
    type: source
    source_type: api  # Uses ApiSource class
```

### 4. Test and Iterate

```bash
# Test your component
dft run --select test_pipeline

# Validate configuration
dft validate
```

## 📥 Sources API

### Base Class: `DataSource`

All custom sources must inherit from `dft.core.base.DataSource`.

#### Required Methods

```python
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket
from typing import Any, Dict, Optional

class YourCustomSource(DataSource):
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data and return DataPacket
        
        Args:
            variables: Pipeline variables (optional)
            
        Returns:
            DataPacket: Container with data and metadata
        """
        pass
    
    def test_connection(self) -> bool:
        """Test if the source is accessible
        
        Returns:
            bool: True if connection successful
        """
        pass
```

#### Available Methods

```python
# Configuration access
value = self.get_config('key', default_value)
all_config = self.config

# Pipeline context
step_id = self.step_id
pipeline_name = self.pipeline_name
```

### Complete Source Example

```python
# dft/sources/rest_api_source.py
import requests
import pandas as pd
from typing import Any, Dict, Optional
from dft.core.base import DataSource
from dft.core.data_packet import DataPacket


class RestApiSource(DataSource):
    """REST API data source with authentication and pagination"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from REST API"""
        # Get configuration
        base_url = self.get_config('base_url')
        endpoint = self.get_config('endpoint')
        api_key = self.get_config('api_key')
        headers = self.get_config('headers', {})
        params = self.get_config('params', {})
        
        # Build request
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers.update({'Authorization': f'Bearer {api_key}'})
        
        # Add variables to params if provided
        if variables:
            params.update(variables)
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Process response
            data = response.json()
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
            
            return DataPacket(
                data=df,
                metadata={
                    'source': 'rest_api',
                    'url': url,
                    'status_code': response.status_code,
                    'row_count': len(df),
                    'columns': list(df.columns)
                }
            )
            
        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            base_url = self.get_config('base_url')
            api_key = self.get_config('api_key')
            
            # Test with a simple endpoint or health check
            health_endpoint = self.get_config('health_endpoint', '/health')
            url = f"{base_url.rstrip('/')}{health_endpoint}"
            
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            return response.status_code == 200
            
        except Exception:
            return False
```

### Usage in Pipeline

```yaml
steps:
  - id: fetch_api_data
    type: source
    source_type: rest_api  # Uses RestApiSource
    config:
      base_url: "https://api.example.com"
      endpoint: "/users"
      api_key: "{{ env_var('API_KEY') }}"
      headers:
        Content-Type: "application/json"
      params:
        limit: 1000
        active: true
```

## ⚙️ Processors API

### Base Class: `DataProcessor`

All custom processors must inherit from `dft.core.base.DataProcessor`.

#### Required Methods

```python
from dft.core.base import DataProcessor
from dft.core.data_packet import DataPacket
from typing import Any, Dict, Optional

class YourCustomProcessor(DataProcessor):
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Process data and return transformed DataPacket
        
        Args:
            packet: Input data packet
            variables: Pipeline variables (optional)
            
        Returns:
            DataPacket: Transformed data packet
        """
        pass
```

### Complete Processor Examples

#### Data Transformation Processor

```python
# dft/processors/data_enricher.py
import pandas as pd
from typing import Any, Dict, Optional
from dft.core.base import DataProcessor
from dft.core.data_packet import DataPacket


class DataEnricher(DataProcessor):
    """Enrich data with additional calculated fields"""
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Add calculated fields to the data"""
        df = packet.data.copy()
        
        # Get configuration
        calculations = self.get_config('calculations', {})
        date_column = self.get_config('date_column')
        
        # Add calculated columns
        for calc_name, calc_config in calculations.items():
            if calc_config['type'] == 'percentage':
                numerator = calc_config['numerator']
                denominator = calc_config['denominator']
                df[calc_name] = (df[numerator] / df[denominator] * 100).round(2)
                
            elif calc_config['type'] == 'date_diff':
                from_date = calc_config['from_date']
                to_date = calc_config.get('to_date', pd.Timestamp.now())
                df[calc_name] = (pd.to_datetime(to_date) - pd.to_datetime(df[from_date])).dt.days
        
        # Add time-based features if date column specified
        if date_column and date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            df['year'] = df[date_column].dt.year
            df['month'] = df[date_column].dt.month
            df['weekday'] = df[date_column].dt.day_name()
            df['is_weekend'] = df[date_column].dt.weekday >= 5
        
        return DataPacket(
            data=df,
            metadata={
                **packet.metadata,
                'processor': 'data_enricher',
                'added_columns': list(calculations.keys()),
                'processed_at': pd.Timestamp.now()
            }
        )
```

#### ML Model Processor

```python
# dft/processors/anomaly_detector.py
import pandas as pd
import numpy as np
from typing import Any, Dict, Optional
from dft.core.base import DataProcessor
from dft.core.data_packet import DataPacket


class AnomalyDetector(DataProcessor):
    """Detect anomalies using statistical methods"""
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Detect anomalies in specified columns"""
        df = packet.data.copy()
        
        # Configuration
        columns = self.get_config('columns', [])
        method = self.get_config('method', 'zscore')  # zscore, iqr, isolation_forest
        threshold = self.get_config('threshold', 3.0)
        
        anomaly_flags = []
        
        for column in columns:
            if column not in df.columns:
                continue
                
            if method == 'zscore':
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                anomalies = z_scores > threshold
                
            elif method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                anomalies = (df[column] < lower_bound) | (df[column] > upper_bound)
                
            elif method == 'isolation_forest':
                try:
                    from sklearn.ensemble import IsolationForest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    anomalies = iso_forest.fit_predict(df[[column]].values) == -1
                except ImportError:
                    # Fallback to z-score if sklearn not available
                    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                    anomalies = z_scores > threshold
            
            # Add anomaly flag column
            flag_column = f'{column}_anomaly'
            df[flag_column] = anomalies
            anomaly_flags.append(flag_column)
        
        # Add overall anomaly flag
        if anomaly_flags:
            df['has_anomaly'] = df[anomaly_flags].any(axis=1)
        
        return DataPacket(
            data=df,
            metadata={
                **packet.metadata,
                'processor': 'anomaly_detector',
                'method': method,
                'anomaly_columns': anomaly_flags,
                'anomaly_count': df.get('has_anomaly', pd.Series()).sum(),
                'total_rows': len(df)
            }
        )
```

### Usage in Pipeline

```yaml
steps:
  - id: enrich_data
    type: processor
    processor_type: data_enricher
    depends_on: [extract_data]
    config:
      date_column: "created_at"
      calculations:
        conversion_rate:
          type: percentage
          numerator: "conversions"
          denominator: "visits"
        days_since_signup:
          type: date_diff
          from_date: "signup_date"
          
  - id: detect_anomalies
    type: processor
    processor_type: anomaly_detector
    depends_on: [enrich_data]
    config:
      columns: ["revenue", "conversion_rate"]
      method: "zscore"
      threshold: 2.5
```

## 📤 Endpoints API

### Base Class: `DataEndpoint`

All custom endpoints must inherit from `dft.core.base.DataEndpoint`.

#### Required Methods

```python
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket
from typing import Any, Dict, Optional

class YourCustomEndpoint(DataEndpoint):
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to destination
        
        Args:
            packet: Data packet to load
            variables: Pipeline variables (optional)
            
        Returns:
            bool: True if load successful
        """
        pass
```

### Complete Endpoint Examples

#### API Webhook Endpoint

```python
# dft/endpoints/webhook_endpoint.py
import requests
import json
import pandas as pd
from typing import Any, Dict, Optional
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket


class WebhookEndpoint(DataEndpoint):
    """Send data to webhook endpoint"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Send data via webhook"""
        # Configuration
        webhook_url = self.get_config('webhook_url')
        headers = self.get_config('headers', {'Content-Type': 'application/json'})
        auth_token = self.get_config('auth_token')
        format_type = self.get_config('format', 'json')  # json, records, summary
        batch_size = self.get_config('batch_size', 100)
        
        # Add authentication
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        df = packet.data
        
        try:
            if format_type == 'summary':
                # Send summary statistics
                payload = {
                    'summary': {
                        'row_count': len(df),
                        'columns': list(df.columns),
                        'pipeline_metadata': packet.metadata
                    }
                }
                response = requests.post(webhook_url, json=payload, headers=headers)
                response.raise_for_status()
                
            elif format_type == 'records':
                # Send individual records in batches
                records = df.to_dict('records')
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    payload = {
                        'data': batch,
                        'batch_info': {
                            'batch_number': i // batch_size + 1,
                            'total_batches': (len(records) + batch_size - 1) // batch_size,
                            'records_in_batch': len(batch)
                        },
                        'metadata': packet.metadata
                    }
                    response = requests.post(webhook_url, json=payload, headers=headers)
                    response.raise_for_status()
                    
            else:  # json format
                payload = {
                    'data': df.to_dict('records'),
                    'metadata': packet.metadata
                }
                response = requests.post(webhook_url, json=payload, headers=headers)
                response.raise_for_status()
            
            print(f"Successfully sent {len(df)} rows to webhook")
            return True
            
        except requests.RequestException as e:
            print(f"Webhook request failed: {e}")
            return False
```

#### Custom File Format Endpoint

```python
# dft/endpoints/excel_endpoint.py
import pandas as pd
from pathlib import Path
from typing import Any, Dict, Optional
from dft.core.base import DataEndpoint
from dft.core.data_packet import DataPacket


class ExcelEndpoint(DataEndpoint):
    """Export data to Excel with multiple sheets and formatting"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Export to Excel file"""
        # Configuration
        file_path = self.get_config('file_path')
        sheet_name = self.get_config('sheet_name', 'Data')
        mode = self.get_config('mode', 'replace')  # replace, append_sheet
        include_metadata = self.get_config('include_metadata', True)
        formatting = self.get_config('formatting', {})
        
        df = packet.data
        
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare Excel writer
            if mode == 'append_sheet' and Path(file_path).exists():
                with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='replace') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Add metadata sheet if requested
                    if include_metadata:
                        metadata_df = pd.DataFrame([
                            {'key': k, 'value': str(v)} 
                            for k, v in packet.metadata.items()
                        ])
                        metadata_df.to_excel(writer, sheet_name=f'{sheet_name}_metadata', index=False)
            else:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Apply formatting if specified
                    if formatting:
                        worksheet = writer.sheets[sheet_name]
                        
                        # Auto-adjust column widths
                        if formatting.get('auto_width', True):
                            for column in worksheet.columns:
                                max_length = 0
                                column_letter = column[0].column_letter
                                for cell in column:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                adjusted_width = min(max_length + 2, 50)
                                worksheet.column_dimensions[column_letter].width = adjusted_width
                        
                        # Add filters to header row
                        if formatting.get('add_filters', True):
                            worksheet.auto_filter.ref = worksheet.dimensions
                    
                    # Add metadata sheet
                    if include_metadata:
                        metadata_df = pd.DataFrame([
                            {'key': k, 'value': str(v)} 
                            for k, v in packet.metadata.items()
                        ])
                        metadata_df.to_excel(writer, sheet_name='metadata', index=False)
            
            print(f"Successfully exported {len(df)} rows to {file_path}")
            return True
            
        except Exception as e:
            print(f"Excel export failed: {e}")
            return False
```

### Usage in Pipeline

```yaml
steps:
  - id: send_webhook
    type: endpoint
    endpoint_type: webhook
    depends_on: [process_data]
    config:
      webhook_url: "https://hooks.slack.com/services/..."
      auth_token: "{{ env_var('SLACK_TOKEN') }}"
      format: "summary"
      
  - id: export_excel
    type: endpoint
    endpoint_type: excel
    depends_on: [process_data]
    config:
      file_path: "output/analysis_{{ today() }}.xlsx"
      sheet_name: "Analysis"
      include_metadata: true
      formatting:
        auto_width: true
        add_filters: true
```

## 📦 Data Packet Structure

### DataPacket Class

The `DataPacket` is the container that flows between components:

```python
from dft.core.data_packet import DataPacket

packet = DataPacket(
    data=your_dataframe,  # pandas DataFrame or compatible data structure
    metadata={            # Dictionary with component metadata
        'source': 'component_name',
        'row_count': len(data),
        'processed_at': timestamp,
        'custom_field': 'value'
    }
)
```

### Data Formats

Components should handle multiple data formats:

```python
def process(self, packet: DataPacket, variables=None) -> DataPacket:
    data = packet.data
    
    # Handle pandas DataFrame (preferred)
    if hasattr(data, 'columns'):  # pandas DataFrame
        processed_data = data.copy()
        # ... pandas operations
    
    # Handle list of dictionaries (fallback)
    elif isinstance(data, list):
        processed_data = []
        for item in data:
            # ... process each item
            processed_data.append(processed_item)
    
    # Handle other formats
    else:
        processed_data = data  # or convert to preferred format
    
    return DataPacket(data=processed_data, metadata=packet.metadata)
```

### Metadata Best Practices

```python
# Good metadata practices
metadata = {
    # Component identification
    'source': 'your_component_name',
    'processor': 'transformation_type',
    
    # Data characteristics
    'row_count': len(data),
    'column_count': len(data.columns),
    'columns': list(data.columns),
    
    # Processing information
    'processed_at': pd.Timestamp.now(),
    'processing_time': elapsed_time,
    'success': True,
    
    # Domain-specific information
    'api_response_code': 200,
    'anomaly_count': 5,
    'validation_errors': []
}
```

## ✅ Best Practices

### 1. Error Handling

```python
def extract(self, variables=None) -> DataPacket:
    try:
        # Main logic
        data = self._fetch_data()
        return DataPacket(data=data, metadata={'status': 'success'})
        
    except ConnectionError as e:
        # Log specific error types
        print(f"Connection failed: {e}")
        raise RuntimeError(f"Could not connect to data source: {e}")
        
    except ValueError as e:
        # Handle data validation errors
        print(f"Data validation failed: {e}")
        raise ValueError(f"Invalid data format: {e}")
        
    except Exception as e:
        # Generic error handling
        print(f"Unexpected error: {e}")
        raise RuntimeError(f"Component failed: {e}")
```

### 2. Configuration Validation

```python
def __init__(self, config: Dict[str, Any], step_id: str, pipeline_name: str):
    super().__init__(config, step_id, pipeline_name)
    
    # Validate required configuration
    required_fields = ['api_url', 'api_key']
    for field in required_fields:
        if not self.get_config(field):
            raise ValueError(f"Missing required configuration: {field}")
    
    # Validate configuration values
    api_url = self.get_config('api_url')
    if not api_url.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid API URL format: {api_url}")
```

### 3. Logging and Monitoring

```python
import logging

def process(self, packet: DataPacket, variables=None) -> DataPacket:
    logger = logging.getLogger(__name__)
    
    start_time = pd.Timestamp.now()
    input_rows = len(packet.data)
    
    logger.info(f"Processing {input_rows} rows with {self.__class__.__name__}")
    
    try:
        # Processing logic
        processed_data = self._transform_data(packet.data)
        
        output_rows = len(processed_data)
        processing_time = (pd.Timestamp.now() - start_time).total_seconds()
        
        logger.info(f"Processed {input_rows} → {output_rows} rows in {processing_time:.2f}s")
        
        return DataPacket(
            data=processed_data,
            metadata={
                **packet.metadata,
                'input_rows': input_rows,
                'output_rows': output_rows,
                'processing_time': processing_time
            }
        )
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

### 4. Environment Variable Usage

```python
import os

class MySource(DataSource):
    def extract(self, variables=None) -> DataPacket:
        # Use environment variables for sensitive data
        api_key = self.get_config('api_key') or os.getenv('MY_API_KEY')
        if not api_key:
            raise ValueError("API key not found in config or environment")
        
        # Support both config and environment
        database_url = (
            self.get_config('database_url') or 
            os.getenv('DATABASE_URL') or
            'sqlite:///default.db'
        )
```

### 5. Testing Support

```python
def test_connection(self) -> bool:
    """Implement meaningful connection tests"""
    try:
        # Test actual connectivity
        api_url = self.get_config('api_url')
        api_key = self.get_config('api_key')
        
        response = requests.get(
            f"{api_url}/health", 
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
```

## 🧪 Testing Custom Components

### Unit Testing

```python
# tests/test_custom_components.py
import unittest
from dft.core.data_packet import DataPacket
from dft.sources.rest_api_source import RestApiSource

class TestRestApiSource(unittest.TestCase):
    def setUp(self):
        self.config = {
            'base_url': 'https://jsonplaceholder.typicode.com',
            'endpoint': '/users',
            'api_key': 'test_key'
        }
        self.source = RestApiSource(self.config, 'test_step', 'test_pipeline')
    
    def test_extract_returns_datapacket(self):
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [{'id': 1, 'name': 'Test'}]
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = self.source.extract()
            
            self.assertIsInstance(result, DataPacket)
            self.assertEqual(len(result.data), 1)
            self.assertEqual(result.data.iloc[0]['name'], 'Test')
    
    def test_connection_test(self):
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = self.source.test_connection()
            self.assertTrue(result)
```

### Integration Testing

```bash
# Create test pipeline
# pipelines/test_custom_components.yml
pipeline_name: test_custom_components

steps:
  - id: test_source
    type: source
    source_type: rest_api
    config:
      base_url: "https://jsonplaceholder.typicode.com"
      endpoint: "/users"
      api_key: "test"
      
  - id: test_processor
    type: processor
    processor_type: data_enricher
    depends_on: [test_source]
    config:
      date_column: "created_at"
      
  - id: test_endpoint
    type: endpoint
    endpoint_type: webhook
    depends_on: [test_processor]
    config:
      webhook_url: "https://httpbin.org/post"
      format: "summary"
```

```bash
# Run test
dft run --select test_custom_components
```

## 🎯 Advanced Patterns

### 1. Stateful Components

```python
class StatefulProcessor(DataProcessor):
    def __init__(self, config, step_id, pipeline_name):
        super().__init__(config, step_id, pipeline_name)
        self.state_file = f".dft/state/{step_id}_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_state(self, state: dict):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def process(self, packet: DataPacket, variables=None) -> DataPacket:
        # Use state for incremental processing
        last_processed_id = self.state.get('last_processed_id', 0)
        
        df = packet.data
        new_data = df[df['id'] > last_processed_id]
        
        # Update state
        if not new_data.empty:
            self.state['last_processed_id'] = new_data['id'].max()
            self.state['last_processed_at'] = pd.Timestamp.now().isoformat()
            self._save_state(self.state)
        
        return DataPacket(data=new_data, metadata=packet.metadata)
```

### 2. Multi-Output Components

```python
class MultiOutputProcessor(DataProcessor):
    def process(self, packet: DataPacket, variables=None) -> DataPacket:
        df = packet.data
        
        # Split data into multiple outputs
        valid_data = df[df['status'] == 'valid']
        invalid_data = df[df['status'] == 'invalid']
        
        # Save additional outputs
        output_dir = self.get_config('output_dir', 'output')
        valid_data.to_csv(f'{output_dir}/valid_data.csv', index=False)
        invalid_data.to_csv(f'{output_dir}/invalid_data.csv', index=False)
        
        # Return main output
        return DataPacket(
            data=valid_data,
            metadata={
                **packet.metadata,
                'valid_rows': len(valid_data),
                'invalid_rows': len(invalid_data),
                'additional_outputs': ['valid_data.csv', 'invalid_data.csv']
            }
        )
```

### 3. Configuration Templates

```python
# dft/sources/database_source.py
class DatabaseSource(DataSource):
    DEFAULT_CONFIG = {
        'timeout': 30,
        'batch_size': 1000,
        'retry_attempts': 3,
        'connection_pool_size': 5
    }
    
    def __init__(self, config, step_id, pipeline_name):
        # Merge with defaults
        full_config = {**self.DEFAULT_CONFIG, **config}
        super().__init__(full_config, step_id, pipeline_name)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Component Not Found

```
Error: Unknown source_type 'my_component'
```

**Solutions:**
- Check file naming: `MyComponentSource` class in `my_component_source.py`
- Verify file location: `dft/sources/my_component_source.py`
- Ensure `__init__.py` exists in the directory
- Check for syntax errors in the component file

#### 2. Import Errors

```
ModuleNotFoundError: No module named 'some_library'
```

**Solutions:**
- Install required dependencies: `pip install some_library`
- Add fallback logic for optional dependencies
- Document dependencies in your project README

#### 3. Configuration Errors

```
ValueError: Missing required configuration: api_key
```

**Solutions:**
- Validate configuration in `__init__` method
- Provide clear error messages
- Document required configuration parameters

#### 4. Data Type Issues

```
AttributeError: 'list' object has no attribute 'columns'
```

**Solutions:**
- Handle multiple data formats in your component
- Convert data to pandas DataFrame when needed
- Check data type before operations

### Debugging Tips

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

def extract(self, variables=None) -> DataPacket:
    logger = logging.getLogger(__name__)
    logger.debug(f"Component config: {self.config}")
    logger.debug(f"Variables: {variables}")
    
    # Your logic here
    
    logger.debug(f"Extracted {len(data)} rows")
    return DataPacket(data=data, metadata=metadata)
```

### Performance Optimization

```python
# Use efficient data operations
def process(self, packet: DataPacket, variables=None) -> DataPacket:
    df = packet.data
    
    # Use vectorized operations instead of loops
    df['calculated'] = df['a'] * df['b']  # Good
    # df['calculated'] = df.apply(lambda row: row['a'] * row['b'], axis=1)  # Slower
    
    # Use efficient filtering
    filtered_df = df[df['status'].isin(['active', 'pending'])]  # Good
    # filtered_df = df[df['status'] == 'active' or df['status'] == 'pending']  # Wrong
    
    return DataPacket(data=filtered_df, metadata=packet.metadata)
```

## 📚 Additional Resources

- [Base Classes Documentation](dft/core/base.py)
- [Example Components](example_project/dft/)
- [Pipeline Configuration Guide](README.md#pipeline-configuration)
- [Environment Variables Guide](DATABASE_INTEGRATION.md#secret-management)

---

**Ready to build custom components?** Start with the examples in your project's `dft/` directory and refer to this guide as you develop more sophisticated components!