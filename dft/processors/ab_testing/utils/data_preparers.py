import numpy as np
import pyarrow as pa
from typing import List, Optional, Union

from ..models.sample import Sample
from ..models.ab_test_config import ABTestConfig


class DataPreparer:
    """Utility class for preparing data for A/B testing"""
    
    @staticmethod
    def prepare_samples(data: pa.Table, config: ABTestConfig) -> List[Sample]:
        """Prepare Sample objects from PyArrow Table for all test types"""
        if config.test_type in ["ttest", "cuped_ttest", "bootstrap"]:
            return DataPreparer._prepare_samples_for_continuous_tests(data, config)
        elif config.test_type == "ztest":
            return DataPreparer._prepare_samples_for_ztest(data, config)
        else:
            raise ValueError(f"Unsupported test type: {config.test_type}")
    
    
    @staticmethod
    def _prepare_samples_for_continuous_tests(data: pa.Table, config: ABTestConfig) -> List[Sample]:
        """Prepare samples for t-test, CUPED t-test, and bootstrap test"""
        required_columns = [config.group_column, config.metric_column]
        
        # Check required columns
        for col in required_columns:
            if col not in data.column_names:
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Check for CUPED covariate column
        if config.test_type == "cuped_ttest":
            if not config.covariate_column:
                raise ValueError("covariate_column is required for CUPED tests")
            if config.covariate_column not in data.column_names:
                raise ValueError(f"Covariate column '{config.covariate_column}' not found in data")
        
        samples = []
        groups = [config.control_group, config.treatment_group]
        
        # Convert columns to numpy arrays for filtering
        group_array = data[config.group_column].to_numpy()
        metric_array = data[config.metric_column].to_numpy()
        
        # Get covariate array if needed
        cov_array_full = None
        if config.test_type == "cuped_ttest":
            cov_array_full = data[config.covariate_column].to_numpy()
        
        for group in groups:
            # Filter by group
            group_mask = group_array == group
            
            if not np.any(group_mask):
                raise ValueError(f"No data found for group '{group}'")
            
            metric_values = metric_array[group_mask]
            
            # Remove NaN values
            valid_mask = ~np.isnan(metric_values)
            metric_values = metric_values[valid_mask]
            
            if len(metric_values) == 0:
                raise ValueError(f"No valid metric values found for group '{group}'")
            
            # Prepare covariate data for CUPED
            cov_array = None
            if config.test_type == "cuped_ttest":
                cov_values = cov_array_full[group_mask][valid_mask]
                if len(cov_values) != len(metric_values):
                    raise ValueError(f"Metric and covariate arrays have different lengths for group '{group}'")
                cov_array = cov_values
            
            sample = Sample(
                array=metric_values,
                cov_array=cov_array,
                name=group
            )
            samples.append(sample)
        
        return samples
    
    @staticmethod 
    def _prepare_samples_for_ztest(data: pa.Table, config: ABTestConfig) -> List[Sample]:
        """Prepare samples for z-test (binary metrics)"""
        required_columns = [config.group_column, config.metric_column]
        
        # Check required columns
        for col in required_columns:
            if col not in data.column_names:
                raise ValueError(f"Required column '{col}' not found in data")
        
        samples = []
        groups = [config.control_group, config.treatment_group]
        
        # Convert columns to numpy arrays for filtering
        group_array = data[config.group_column].to_numpy()
        metric_array = data[config.metric_column].to_numpy()
        
        for group in groups:
            # Filter by group
            group_mask = group_array == group
            
            if not np.any(group_mask):
                raise ValueError(f"No data found for group '{group}'")
            
            metric_values = metric_array[group_mask]
            
            # Remove NaN values
            valid_mask = ~np.isnan(metric_values.astype(float))
            metric_values = metric_values[valid_mask]
            
            if len(metric_values) == 0:
                raise ValueError(f"No valid metric values found for group '{group}'")
            
            # Check if values are binary (0/1)
            unique_values = np.unique(metric_values)
            if not np.all(np.isin(unique_values, [0, 1])):
                raise ValueError(f"Z-test requires binary metric values (0/1) for group '{group}'. "
                               f"Found values: {unique_values}")
            
            # Convert to binary array for Sample object
            binary_array = metric_values.astype(int)
            
            sample = Sample(
                array=binary_array,
                cov_array=None,
                name=group
            )
            samples.append(sample)
        
        return samples


def prepare_samples(data: pa.Table, config: ABTestConfig) -> List[Sample]:
    """Convenience function for preparing samples"""
    return DataPreparer.prepare_samples(data, config)