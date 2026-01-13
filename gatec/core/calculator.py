def calculate_generation(efficiency, total_output):
    """
    Calculate generation value based on efficiency and total output.
    Returns the generation value as a float, or 0.0 if calculation fails.
    """
    try:
        efficiency = float(efficiency)
        total_output = float(total_output)
        
        if total_output > 0 and efficiency > 0:
            generation_value = total_output / (efficiency / 100)
            return round(generation_value, 2)
        else:
            return 0.0
    except (ValueError, TypeError):
        return 0.0

def calculate_results(input_data):
    """
    Perform all calculations based on input data.
    Returns a dictionary with results.
    """
    try:
        results = {}
        
        # Initialize default values
        defaults = {
            'total_output': 0,
            'extraction': 0,
            'processing': 0,
            'transportation': 0,
            'generation': 0,
            'plant_efficiency': 0,
            'ccs_capture': 0,
            'ccs_compression': 0,
            'ccs_transportation': 0,
            'ccs_storage': 0,
            'emissions_value': 0,
            'ccs': False,
            'include_emissions': False
        }
        
        # Safely get all input values with defaults
        try:
            total_output = float(input_data.get('total_output', defaults['total_output']))
            extraction = float(input_data.get('extraction', defaults['extraction']))
            processing = float(input_data.get('processing', defaults['processing']))
            transportation = float(input_data.get('transportation', defaults['transportation']))
            generation = float(input_data.get('generation', defaults['generation']))
            plant_efficiency = float(input_data.get('plant_efficiency', defaults['plant_efficiency']))
            ccs_enabled = bool(input_data.get('ccs', defaults['ccs']))
            include_emissions = bool(input_data.get('include_emissions', defaults['include_emissions']))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid input values: {str(e)}")

        # 1. Calculate total energy contributions
        try:
            ccs_energy = 0
            if ccs_enabled:
                ccs_energy = (
                    float(input_data.get('ccs_capture', defaults['ccs_capture'])) +
                    float(input_data.get('ccs_compression', defaults['ccs_compression'])) +
                    float(input_data.get('ccs_transportation', defaults['ccs_transportation'])) +
                    float(input_data.get('ccs_storage', defaults['ccs_storage']))
                )
            
            total_energy = extraction + processing + transportation + generation + ccs_energy
        except Exception as e:
            raise ValueError(f"Error calculating total energy: {str(e)}")

        # 2. Calculate total efficiency
        try:
            if total_energy > 0:
                results['total_efficiency'] = (total_output / total_energy) * 100
            else:
                results['total_efficiency'] = 0.0
        except Exception as e:
            raise ValueError(f"Error calculating total efficiency: {str(e)}")

        # 3. Calculate efficiency drop
        try:
            results['efficiency_drop'] = max(0.0, plant_efficiency - results['total_efficiency'])
        except Exception as e:
            raise ValueError(f"Error calculating efficiency drop: {str(e)}")

        # 4. Calculate emissions (if enabled)
        try:
            if include_emissions:
                emissions_value = float(input_data.get('emissions_value', defaults['emissions_value']))
                results['total_emissions'] = emissions_value * (1 - results['total_efficiency']/100)
            else:
                results['total_emissions'] = 0.0
        except Exception as e:
            raise ValueError(f"Error calculating emissions: {str(e)}")

        # 5. Energy contributions by stage
        try:
            results['energy_contributions'] = {
                'extraction': extraction,
                'processing': processing,
                'transportation': transportation,
                'generation': generation,
                'ccs': ccs_energy if ccs_enabled else 0.0
            }
        except Exception as e:
            raise ValueError(f"Error preparing energy contributions: {str(e)}")

        # 6. CCS sensitivity analysis
        try:
            results['ccs_sensitivity'] = []
            results['ccs_sensitivity_percentages'] = []
            if ccs_enabled:
                ccs_interval = float(input_data.get('ccs_sensitivity_value', 5))
                if ccs_interval <= 0: ccs_interval = 5
                
                # Range: 100-2*i, 100-i, 100, 100+i, 100+2*i
                percentages = [100 + (i * ccs_interval) for i in range(-2, 3)]
                results['ccs_sensitivity_percentages'] = percentages
                
                for percentage in percentages:
                    adjusted_ccs = ccs_energy * (percentage/100)
                    adjusted_total = extraction + processing + transportation + generation + adjusted_ccs
                    eff = (total_output / adjusted_total) * 100 if adjusted_total > 0 else 0
                    results['ccs_sensitivity'].append(eff)
            else:
                results['ccs_sensitivity'] = [results['total_efficiency']] * 5
                results['ccs_sensitivity_percentages'] = [100] * 5
        except Exception as e:
            raise ValueError(f"Error in CCS sensitivity analysis: {str(e)}")

        # 7. General Sensitivity Analysis
        try:
            interval = float(input_data.get('sensitivity_value', 5))
            if interval <= 0: interval = 5
            
            # Range: 100-2*i, 100-i, 100, 100+i, 100+2*i
            percentages = [100 + (i * interval) for i in range(-2, 3)]
            
            results['general_sensitivity'] = {'percentages': percentages, 'efficiencies': []}
            
            for p in percentages:
                factor = p / 100.0
                
                # Apply factor to all non-generation components
                adj_extraction = extraction * factor
                adj_processing = processing * factor
                adj_transportation = transportation * factor
                adj_ccs = ccs_energy * factor
                
                adj_total_energy = adj_extraction + adj_processing + adj_transportation + generation + adj_ccs
                
                eff = (total_output / adj_total_energy) * 100 if adj_total_energy > 0 else 0
                results['general_sensitivity']['efficiencies'].append(eff)
                
        except Exception as e:
             raise ValueError(f"Error in General sensitivity analysis: {str(e)}")

        return results

    except Exception as e:
        # Return a results dictionary with error information
        return {
            'error': str(e),
            'total_efficiency': 0.0,
            'efficiency_drop': 0.0,
            'total_emissions': 0.0,
            'energy_contributions': {
                'extraction': 0.0,
                'processing': 0.0,
                'transportation': 0.0,
                'generation': 0.0,
                'ccs': 0.0
            },
            'ccs_sensitivity': [0.0] * 5,
            'general_sensitivity': {'percentages': [], 'efficiencies': []}
        }
