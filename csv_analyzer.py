"""
CSV Running Data Analyzer
Parse and analyze running data from CSV files (similar to Garmin CSV format).
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


def parse_pace_to_seconds(pace_str):
    """
    Convert pace string (e.g., "8:15") to seconds per mile (float).
    
    Args:
        pace_str: Pace string in format "MM:SS" or "H:MM:SS"
        
    Returns:
        Seconds per mile as float, or None if invalid
    """
    if pd.isna(pace_str) or pace_str == '':
        return None
    
    try:
        pace_str = str(pace_str).strip()
        parts = pace_str.split(':')
        
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        else:
            return None
    except:
        return None


def calculate_cardiac_drift_from_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate cardiac drift from running data.
    
    Args:
        df: DataFrame with running data
        
    Returns:
        Dictionary with cardiac drift metrics
    """
    # Find column names (handle different formats)
    hr_col = None
    pace_col = None
    distance_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'hr' in col_lower and ('avg' in col_lower or 'average' in col_lower):
            hr_col = col
        if 'pace' in col_lower and ('avg' in col_lower or 'average' in col_lower):
            pace_col = col
        if 'distance' in col_lower:
            distance_col = col
    
    if not hr_col or not pace_col:
        return {
            'first_half_efficiency': None,
            'second_half_efficiency': None,
            'drift_percentage': None,
            'error': 'Missing required columns (HR or Pace)'
        }
    
    # Filter valid data
    valid_data = df[df[hr_col].notna() & df[pace_col].notna()].copy()
    
    if len(valid_data) < 2:
        return {
            'first_half_efficiency': None,
            'second_half_efficiency': None,
            'drift_percentage': None,
            'error': 'Insufficient data points'
        }
    
    # Convert pace to speed (km/h)
    # Note: CSV pace might be in min/mi, need to convert to km/h
    valid_data['pace_seconds'] = valid_data[pace_col].apply(parse_pace_to_seconds)
    
    # If distance column exists and is in miles, convert pace accordingly
    if distance_col and 'mi' in distance_col.lower():
        # Pace is min/mi, convert to km/h: 1 mile = 1.60934 km
        valid_data['speed_kmh'] = valid_data['pace_seconds'].apply(
            lambda x: (1.60934 * 3600) / x if x and x > 0 else None
        )
    else:
        # Assume pace is min/km
        valid_data['speed_kmh'] = valid_data['pace_seconds'].apply(
            lambda x: 3600 / x if x and x > 0 else None
        )
    
    # Split into first and second half
    mid_point = len(valid_data) // 2
    first_half = valid_data.iloc[:mid_point]
    second_half = valid_data.iloc[mid_point:]
    
    # Calculate efficiency (Speed / HR)
    first_half['efficiency'] = first_half['speed_kmh'] / first_half[hr_col]
    second_half['efficiency'] = second_half['speed_kmh'] / second_half[hr_col]
    
    avg_first = first_half['efficiency'].mean()
    avg_second = second_half['efficiency'].mean()
    
    if pd.isna(avg_first) or pd.isna(avg_second) or avg_first == 0:
        return {
            'first_half_efficiency': None,
            'second_half_efficiency': None,
            'drift_percentage': None,
            'error': 'Could not calculate efficiency'
        }
    
    drift_pct = ((avg_second - avg_first) / avg_first) * 100
    
    return {
        'first_half_efficiency': float(avg_first),
        'second_half_efficiency': float(avg_second),
        'drift_percentage': float(drift_pct),
        'first_half_avg_hr': float(first_half[hr_col].mean()),
        'second_half_avg_hr': float(second_half[hr_col].mean()),
        'first_half_avg_speed': float(first_half['speed_kmh'].mean()),
        'second_half_avg_speed': float(second_half['speed_kmh'].mean())
    }


def calculate_pacing_variance_from_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate pacing variance from running data.
    
    Args:
        df: DataFrame with running data
        
    Returns:
        Dictionary with pacing variance metrics
    """
    # Find pace column
    pace_col = None
    distance_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'pace' in col_lower and ('avg' in col_lower or 'average' in col_lower):
            pace_col = col
        if 'distance' in col_lower:
            distance_col = col
    
    if not pace_col:
        return {
            'speed_std': None,
            'speed_mean': None,
            'coefficient_of_variation': None,
            'run_type': 'Unknown',
            'error': 'Missing pace column'
        }
    
    # Convert pace to speed
    df_copy = df.copy()
    df_copy['pace_seconds'] = df_copy[pace_col].apply(parse_pace_to_seconds)
    
    # Handle miles vs kilometers
    if distance_col and 'mi' in distance_col.lower():
        df_copy['speed_kmh'] = df_copy['pace_seconds'].apply(
            lambda x: (1.60934 * 3600) / x if x and x > 0 else None
        )
    else:
        df_copy['speed_kmh'] = df_copy['pace_seconds'].apply(
            lambda x: 3600 / x if x and x > 0 else None
        )
    
    valid_speeds = df_copy['speed_kmh'].dropna()
    
    if len(valid_speeds) < 2:
        return {
            'speed_std': None,
            'speed_mean': None,
            'coefficient_of_variation': None,
            'run_type': 'Unknown',
            'error': 'Insufficient valid speed data'
        }
    
    speed_mean_val = valid_speeds.mean()
    speed_std_val = valid_speeds.std()
    speed_min_val = valid_speeds.min()
    speed_max_val = valid_speeds.max()
    
    speed_mean = float(speed_mean_val) if not pd.isna(speed_mean_val) else None
    speed_std = float(speed_std_val) if not pd.isna(speed_std_val) else None
    
    cv = speed_std / speed_mean if speed_mean and speed_mean > 0 else None
    
    if cv is not None:
        if cv < 0.1:
            run_type = "Steady Run"
        elif cv > 0.2:
            run_type = "Intervals/Erratic"
        else:
            run_type = "Moderate Variation"
    else:
        run_type = "Unknown"
    
    return {
        'speed_std': speed_std,
        'speed_mean': speed_mean,
        'coefficient_of_variation': float(cv) if cv is not None else None,
        'run_type': run_type,
        'speed_min': float(speed_min_val) if not pd.isna(speed_min_val) else None,
        'speed_max': float(speed_max_val) if not pd.isna(speed_max_val) else None
    }


def analyze_csv(file_path: str) -> Dict[str, Any]:
    """
    Analyze CSV running data file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary containing comprehensive analysis
    """
    # Load CSV with error handling
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {str(e)}")
    
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Clean data
    # Convert Date to datetime
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Clean numeric columns - find columns that might contain numbers
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to clean numeric strings
            df[col] = df[col].astype(str).str.replace(',', '').replace('--', np.nan)
            df[col] = pd.to_numeric(df[col], errors='ignore')
    
    # Find key columns
    distance_col = None
    hr_col = None
    max_hr_col = None
    pace_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'distance' in col_lower:
            distance_col = col
        if 'hr' in col_lower and ('avg' in col_lower or 'average' in col_lower):
            hr_col = col
        if 'hr' in col_lower and 'max' in col_lower:
            max_hr_col = col
        if 'pace' in col_lower and ('avg' in col_lower or 'average' in col_lower):
            pace_col = col
    
    # Calculate basic stats
    total_distance = None
    if distance_col:
        total_distance = df[distance_col].sum()
        # Convert miles to km if needed
        if 'mi' in distance_col.lower():
            total_distance = total_distance * 1.60934
        # Convert to Python native type
        total_distance = float(total_distance) if total_distance is not None and not pd.isna(total_distance) else None
    
    avg_hr = float(df[hr_col].mean()) if hr_col and not df[hr_col].isna().all() else None
    if avg_hr is not None and pd.isna(avg_hr):
        avg_hr = None
    else:
        avg_hr = float(avg_hr) if avg_hr is not None else None
    
    max_hr = float(df[max_hr_col].max()) if max_hr_col and not df[max_hr_col].isna().all() else None
    if max_hr is not None and pd.isna(max_hr):
        max_hr = None
    else:
        max_hr = float(max_hr) if max_hr is not None else None
    
    # Calculate total duration (if Time column exists)
    if 'Time' in df.columns:
        # Parse time strings (e.g., "45:21")
        def parse_time(time_str):
            try:
                parts = str(time_str).split(':')
                if len(parts) == 2:
                    return int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except:
                return None
            return None
        
        total_duration_seconds = df['Time'].apply(parse_time).sum()
        if total_duration_seconds is not None and not pd.isna(total_duration_seconds):
            total_duration_seconds = float(total_duration_seconds)
            total_duration_minutes = float(total_duration_seconds / 60.0)
        else:
            total_duration_seconds = None
            total_duration_minutes = None
    else:
        total_duration_seconds = None
        total_duration_minutes = None
    
    # Calculate average pace
    avg_pace = None
    if pace_col:
        pace_seconds = df[pace_col].apply(parse_pace_to_seconds)
        avg_pace_seconds = pace_seconds.mean()
        if avg_pace_seconds and avg_pace_seconds > 0:
            # Convert to min/km if pace was in min/mi
            if distance_col and 'mi' in distance_col.lower():
                # Convert min/mi to min/km
                avg_pace_seconds = avg_pace_seconds / 1.60934
            
            pace_minutes = int(avg_pace_seconds // 60)
            pace_secs = int(avg_pace_seconds % 60)
            avg_pace = f"{pace_minutes}:{pace_secs:02d}"
    
    # Calculate cadence metrics
    cadence_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'cadence' in col_lower and ('run' in col_lower or 'avg' in col_lower or 'average' in col_lower):
            cadence_col = col
            break
    
    if cadence_col:
        valid_cadences = df[cadence_col].dropna()
        avg_cadence = float(valid_cadences.mean()) if len(valid_cadences) > 0 else None
        max_cadence = float(valid_cadences.max()) if len(valid_cadences) > 0 else None
        min_cadence = float(valid_cadences.min()) if len(valid_cadences) > 0 else None
        cadence_std = float(valid_cadences.std()) if len(valid_cadences) > 0 else None
        
        if cadence_std and avg_cadence and avg_cadence > 0:
            cadence_cv = cadence_std / avg_cadence
            if cadence_cv < 0.05:
                cadence_consistency = "Very Consistent"
            elif cadence_cv < 0.10:
                cadence_consistency = "Consistent"
            else:
                cadence_consistency = "Variable"
        else:
            cadence_consistency = "Unknown"
    else:
        avg_cadence = None
        max_cadence = None
        min_cadence = None
        cadence_std = None
        cadence_consistency = "No Data"
    
    # Calculate vertical oscillation metrics
    vo_col = None
    for col in df.columns:
        col_lower = col.lower().strip()
        # Match various formats: "Avg Vertical Oscillationcm", "Vertical Oscillation", etc.
        if ('vertical' in col_lower and 'oscillation' in col_lower) or ('vertical' in col_lower and 'osc' in col_lower):
            vo_col = col
            break
    
    if vo_col:
        # Clean vertical oscillation column specifically
        # Handle string values like '--' or other non-numeric values
        df[vo_col] = df[vo_col].astype(str).str.replace('--', '', regex=False).str.strip()
        df[vo_col] = pd.to_numeric(df[vo_col], errors='coerce')
        
        valid_vos = df[vo_col].dropna()
        if len(valid_vos) > 0:
            avg_vo_val = valid_vos.mean()
            max_vo_val = valid_vos.max()
            vo_std_val = valid_vos.std()
            
            avg_vertical_oscillation = float(avg_vo_val) if not pd.isna(avg_vo_val) else None
            max_vertical_oscillation = float(max_vo_val) if not pd.isna(max_vo_val) else None
            vo_std = float(vo_std_val) if not pd.isna(vo_std_val) else None
        else:
            avg_vertical_oscillation = None
            max_vertical_oscillation = None
            vo_std = None
        
        if avg_vertical_oscillation is not None:
            if avg_vertical_oscillation < 6.0:
                vo_assessment = "Excellent (Very Efficient)"
            elif avg_vertical_oscillation < 8.0:
                vo_assessment = "Good (Efficient)"
            elif avg_vertical_oscillation < 10.0:
                vo_assessment = "Moderate"
            else:
                vo_assessment = "High (Less Efficient)"
        else:
            vo_assessment = "Unknown"
    else:
        avg_vertical_oscillation = None
        max_vertical_oscillation = None
        vo_std = None
        vo_assessment = "No Data"
    
    # Calculate stride length
    stride_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'stride' in col_lower and 'length' in col_lower:
            stride_col = col
            break
    
    if stride_col:
        valid_strides = df[stride_col].dropna()
        if len(valid_strides) > 0:
            stride_mean = valid_strides.mean()
            avg_stride_length = float(stride_mean) if not pd.isna(stride_mean) else None
        else:
            avg_stride_length = None
    else:
        avg_stride_length = None
    
    # Calculate ground contact time
    gct_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'ground' in col_lower and 'contact' in col_lower and 'time' in col_lower:
            gct_col = col
            break
    
    if gct_col:
        valid_gcts = df[gct_col].dropna()
        if len(valid_gcts) > 0:
            gct_mean = valid_gcts.mean()
            avg_gct = float(gct_mean) if not pd.isna(gct_mean) else None
        else:
            avg_gct = None
    else:
        avg_gct = None
    
    # Calculate ground contact balance
    gcb_col = None
    for col in df.columns:
        col_lower = col.lower()
        if ('gct' in col_lower or 'ground' in col_lower) and 'balance' in col_lower:
            gcb_col = col
            break
    
    if gcb_col:
        # Convert to numeric, handling '--' and other non-numeric values
        df[gcb_col] = pd.to_numeric(df[gcb_col], errors='coerce')
        valid_gcbs = df[gcb_col].dropna()
        if len(valid_gcbs) > 0:
            gcb_mean = valid_gcbs.mean()
            avg_gcb = float(gcb_mean) if not pd.isna(gcb_mean) else None
        else:
            avg_gcb = None
    else:
        avg_gcb = None
    
    # Advanced Metrics
    cardiac_drift = calculate_cardiac_drift_from_data(df)
    pacing_variance = calculate_pacing_variance_from_data(df)
    
    # Build result dictionary
    result = {
        'basic_stats': {
            'total_distance_km': round(total_distance, 2) if total_distance else None,
            'total_duration_minutes': round(total_duration_minutes, 2) if total_duration_minutes else None,
            'total_duration_seconds': total_duration_seconds,
            'avg_heart_rate': round(avg_hr, 1) if avg_hr else None,
            'max_heart_rate': round(max_hr, 1) if max_hr else None,
            'avg_pace': avg_pace,
            'num_records': len(df)
        },
        'cardiac_drift': cardiac_drift,
        'pacing_variance': pacing_variance,
        'cadence_metrics': {
            'avg_cadence': round(avg_cadence, 1) if avg_cadence else None,
            'max_cadence': round(max_cadence, 1) if max_cadence else None,
            'min_cadence': round(min_cadence, 1) if min_cadence else None,
            'cadence_std': round(cadence_std, 2) if cadence_std else None,
            'cadence_consistency': cadence_consistency
        },
        'vertical_oscillation_metrics': {
            'avg_vertical_oscillation_cm': round(avg_vertical_oscillation, 2) if avg_vertical_oscillation is not None else None,
            'max_vertical_oscillation_cm': round(max_vertical_oscillation, 2) if max_vertical_oscillation is not None else None,
            'vertical_oscillation_std': round(vo_std, 2) if vo_std is not None else None,
            'assessment': vo_assessment
        },
        'stride_metrics': {
            'avg_stride_length_m': round(avg_stride_length, 3) if avg_stride_length else None
        },
        'ground_contact': {
            'avg_ground_contact_time_ms': round(avg_gct, 1) if avg_gct else None,
            'avg_ground_contact_balance': round(avg_gcb, 1) if avg_gcb else None
        }
    }
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "Running_Today.csv"
    
    try:
        print(f"Analyzing CSV file: {file_path}")
        print("=" * 60)
        
        result = analyze_csv(file_path)
        
        print("\nBasic Stats:")
        print(f"  Total Distance: {result['basic_stats']['total_distance_km']} km")
        print(f"  Total Duration: {result['basic_stats']['total_duration_minutes']} minutes")
        print(f"  Average HR: {result['basic_stats']['avg_heart_rate']} bpm")
        print(f"  Average Pace: {result['basic_stats']['avg_pace']} min/km")
        
        print("\nCardiac Drift:")
        if result['cardiac_drift'].get('error'):
            print(f"  Error: {result['cardiac_drift']['error']}")
        else:
            print(f"  First Half Efficiency: {result['cardiac_drift']['first_half_efficiency']:.4f}")
            print(f"  Second Half Efficiency: {result['cardiac_drift']['second_half_efficiency']:.4f}")
            print(f"  Drift Percentage: {result['cardiac_drift']['drift_percentage']:.2f}%")
        
        print("\nPacing Variance:")
        if result['pacing_variance'].get('error'):
            print(f"  Error: {result['pacing_variance']['error']}")
        else:
            print(f"  Speed Std Dev: {result['pacing_variance']['speed_std']:.2f} km/h")
            print(f"  Coefficient of Variation: {result['pacing_variance']['coefficient_of_variation']:.3f}")
            print(f"  Run Type: {result['pacing_variance']['run_type']}")
        
        print("\nCadence Metrics:")
        cadence = result['cadence_metrics']
        if cadence['avg_cadence']:
            print(f"  Average Cadence: {cadence['avg_cadence']} spm")
            print(f"  Consistency: {cadence['cadence_consistency']}")
        else:
            print(f"  No cadence data available")
        
        print("\nVertical Oscillation:")
        vo = result['vertical_oscillation']
        if vo['avg_vertical_oscillation_cm']:
            print(f"  Average: {vo['avg_vertical_oscillation_cm']} cm")
            print(f"  Assessment: {vo['assessment']}")
        else:
            print(f"  No vertical oscillation data available")
        
        print("\n" + "=" * 60)
        
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
