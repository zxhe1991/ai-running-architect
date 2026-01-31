"""
TCX File Analyzer
Parse and analyze Garmin TCX (Training Center XML) files.
"""
import xml.etree.ElementTree as ET
from lxml import etree
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def parse_tcx(file_path: str) -> Dict[str, Any]:
    """
    Parse TCX file and extract trackpoint data.
    
    Args:
        file_path: Path to the TCX file
        
    Returns:
        Dictionary containing parsed trackpoint data
    """
    # TCX namespace
    namespaces = {
        'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
    }
    
    try:
        # Parse XML with lxml for better namespace handling
        tree = etree.parse(file_path)
        root = tree.getroot()
        
        # Find all trackpoints
        trackpoints = root.findall('.//ns:Trackpoint', namespaces)
        
        if not trackpoints:
            # Try alternative namespace
            namespaces_alt = {
                '': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
            }
            trackpoints = root.findall('.//Trackpoint', namespaces_alt)
        
        data = {
            'times': [],
            'distances': [],
            'heart_rates': [],
            'speeds': [],
            'latitudes': [],
            'longitudes': [],
            'altitudes': [],
            'cadences': [],  # Steps per minute
            'vertical_oscillations': [],  # Vertical oscillation (cm)
            'stride_lengths': [],  # Stride length (m)
            'ground_contact_times': [],  # Ground contact time (ms)
            'ground_contact_balance': []  # Left/right balance (%)
        }
        
        total_distance = 0.0
        
        for tp in trackpoints:
            # Extract time
            time_elem = tp.find('ns:Time', namespaces)
            if time_elem is None:
                time_elem = tp.find('Time')
            
            if time_elem is not None:
                time_str = time_elem.text
                try:
                    # Parse ISO format time
                    time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    data['times'].append(time_obj)
                except:
                    pass
            
            # Extract distance
            distance_elem = tp.find('ns:DistanceMeters', namespaces)
            if distance_elem is None:
                distance_elem = tp.find('DistanceMeters')
            
            if distance_elem is not None:
                distance = float(distance_elem.text)
                data['distances'].append(distance)
                total_distance = distance  # Last distance is total
            
            # Extract heart rate
            hr_elem = tp.find('ns:HeartRateBpm/ns:Value', namespaces)
            if hr_elem is None:
                hr_elem = tp.find('HeartRateBpm/Value')
            
            if hr_elem is not None:
                hr = int(hr_elem.text)
                data['heart_rates'].append(hr)
            else:
                data['heart_rates'].append(None)
            
            # Extract position (lat/lon)
            pos_elem = tp.find('ns:Position', namespaces)
            if pos_elem is None:
                pos_elem = tp.find('Position')
            
            if pos_elem is not None:
                lat_elem = pos_elem.find('ns:LatitudeDegrees', namespaces)
                lon_elem = pos_elem.find('ns:LongitudeDegrees', namespaces)
                
                if lat_elem is None:
                    lat_elem = pos_elem.find('LatitudeDegrees')
                if lon_elem is None:
                    lon_elem = pos_elem.find('LongitudeDegrees')
                
                if lat_elem is not None and lon_elem is not None:
                    data['latitudes'].append(float(lat_elem.text))
                    data['longitudes'].append(float(lon_elem.text))
            
            # Extract altitude
            alt_elem = tp.find('ns:AltitudeMeters', namespaces)
            if alt_elem is None:
                alt_elem = tp.find('AltitudeMeters')
            
            if alt_elem is not None:
                data['altitudes'].append(float(alt_elem.text))
        
        # Calculate speeds from distances and times
        if len(data['distances']) > 1 and len(data['times']) > 1:
            speeds = []
            for i in range(1, len(data['distances'])):
                if i < len(data['times']):
                    time_diff = (data['times'][i] - data['times'][i-1]).total_seconds()
                    if time_diff > 0:
                        distance_diff = data['distances'][i] - data['distances'][i-1]
                        speed_ms = distance_diff / time_diff  # meters per second
                        speed_kmh = speed_ms * 3.6  # km/h
                        speeds.append(speed_kmh)
                    else:
                        speeds.append(0)
                else:
                    speeds.append(0)
            
            # Add first speed point (use second point's speed)
            if speeds:
                data['speeds'] = [speeds[0]] + speeds
            else:
                data['speeds'] = [0]
        else:
            data['speeds'] = [0]
        
        # Ensure all arrays have the same length
        min_length = min(len(data['times']), len(data['distances']), 
                        len(data['heart_rates']), len(data['speeds']))
        
        for key in data:
            if len(data[key]) < min_length:
                # Pad with None if shorter
                data[key].extend([None] * (min_length - len(data[key])))
            else:
                data[key] = data[key][:min_length]
        
        return {
            'trackpoints': data,
            'total_distance_meters': total_distance
        }
        
    except Exception as e:
        raise ValueError(f"Error parsing TCX file: {str(e)}")


def calculate_cardiac_drift(heart_rates: List[Optional[int]], 
                            speeds: List[float]) -> Dict[str, Any]:
    """
    Calculate cardiac drift (efficiency drop) between first and second half.
    
    Args:
        heart_rates: List of heart rate values
        speeds: List of speed values (km/h)
        
    Returns:
        Dictionary with cardiac drift metrics
    """
    # Filter out None values and ensure we have valid data
    valid_indices = [i for i, hr in enumerate(heart_rates) 
                    if hr is not None and i < len(speeds) and speeds[i] > 0]
    
    if len(valid_indices) < 4:
        return {
            'first_half_efficiency': None,
            'second_half_efficiency': None,
            'drift_percentage': None,
            'error': 'Insufficient data points'
        }
    
    # Split into first and second half
    mid_point = len(valid_indices) // 2
    first_half_indices = valid_indices[:mid_point]
    second_half_indices = valid_indices[mid_point:]
    
    # Calculate efficiency (Speed / HR) for each half
    first_half_efficiencies = []
    for idx in first_half_indices:
        if heart_rates[idx] is not None and heart_rates[idx] > 0:
            efficiency = speeds[idx] / heart_rates[idx]
            first_half_efficiencies.append(efficiency)
    
    second_half_efficiencies = []
    for idx in second_half_indices:
        if heart_rates[idx] is not None and heart_rates[idx] > 0:
            efficiency = speeds[idx] / heart_rates[idx]
            second_half_efficiencies.append(efficiency)
    
    if not first_half_efficiencies or not second_half_efficiencies:
        return {
            'first_half_efficiency': None,
            'second_half_efficiency': None,
            'drift_percentage': None,
            'error': 'Could not calculate efficiency'
        }
    
    avg_first = np.mean(first_half_efficiencies)
    avg_second = np.mean(second_half_efficiencies)
    
    # Calculate drift percentage (negative means efficiency dropped)
    if avg_first > 0:
        drift_pct = ((avg_second - avg_first) / avg_first) * 100
    else:
        drift_pct = None
    
    return {
        'first_half_efficiency': float(avg_first),
        'second_half_efficiency': float(avg_second),
        'drift_percentage': float(drift_pct) if drift_pct is not None else None,
        'first_half_avg_hr': float(np.mean([heart_rates[i] for i in first_half_indices if heart_rates[i] is not None])),
        'second_half_avg_hr': float(np.mean([heart_rates[i] for i in second_half_indices if heart_rates[i] is not None])),
        'first_half_avg_speed': float(np.mean([speeds[i] for i in first_half_indices])),
        'second_half_avg_speed': float(np.mean([speeds[i] for i in second_half_indices]))
    }


def calculate_pacing_variance(speeds: List[float]) -> Dict[str, Any]:
    """
    Calculate pacing variance to determine run type.
    
    Args:
        speeds: List of speed values (km/h)
        
    Returns:
        Dictionary with pacing variance metrics
    """
    if not speeds or len(speeds) < 2:
        return {
            'speed_std': None,
            'speed_mean': None,
            'coefficient_of_variation': None,
            'run_type': 'Unknown',
            'error': 'Insufficient data'
        }
    
    # Filter out zero speeds (pauses/stops)
    valid_speeds = [s for s in speeds if s > 0]
    
    if len(valid_speeds) < 2:
        return {
            'speed_std': None,
            'speed_mean': None,
            'coefficient_of_variation': None,
            'run_type': 'Unknown',
            'error': 'Insufficient valid speed data'
        }
    
    speed_array = np.array(valid_speeds)
    speed_mean = float(np.mean(speed_array))
    speed_std = float(np.std(speed_array))
    
    # Coefficient of variation (CV) = std / mean
    if speed_mean > 0:
        cv = speed_std / speed_mean
    else:
        cv = None
    
    # Classify run type based on CV
    # Low CV (< 0.1 or 10%) = Steady Run
    # High CV (> 0.2 or 20%) = Intervals/Erratic
    # Medium CV (0.1-0.2) = Moderate variation
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
        'speed_min': float(np.min(speed_array)),
        'speed_max': float(np.max(speed_array))
    }


def analyze_tcx(file_path: str) -> Dict[str, Any]:
    """
    Analyze TCX file and return comprehensive metrics.
    
    Args:
        file_path: Path to the TCX file
        
    Returns:
        Dictionary containing:
        - Basic stats: Total Distance, Total Duration, Avg HR
        - Cardiac Drift: Efficiency metrics for first/second half
        - Pacing Variance: Speed variance and run type classification
    """
    # Parse TCX file
    parsed_data = parse_tcx(file_path)
    trackpoints = parsed_data['trackpoints']
    
    # Extract arrays
    times = trackpoints['times']
    distances = trackpoints['distances']
    heart_rates = trackpoints['heart_rates']
    speeds = trackpoints['speeds']
    
    # Basic Stats
    total_distance_meters = parsed_data['total_distance_meters']
    total_distance_km = total_distance_meters / 1000.0
    
    if len(times) > 1:
        total_duration = times[-1] - times[0]
        total_duration_seconds = total_duration.total_seconds()
        total_duration_minutes = total_duration_seconds / 60.0
    else:
        total_duration_seconds = 0
        total_duration_minutes = 0
    
    # Calculate average heart rate (filter None values)
    valid_hrs = [hr for hr in heart_rates if hr is not None]
    avg_hr = float(np.mean(valid_hrs)) if valid_hrs else None
    
    # Calculate average speed
    valid_speeds = [s for s in speeds if s > 0]
    avg_speed = float(np.mean(valid_speeds)) if valid_speeds else None
    
    # Calculate average pace (minutes per km)
    if avg_speed and avg_speed > 0:
        pace_seconds_per_km = 3600 / avg_speed
        pace_minutes = int(pace_seconds_per_km // 60)
        pace_seconds = int(pace_seconds_per_km % 60)
        avg_pace = f"{pace_minutes}:{pace_seconds:02d}"
    else:
        avg_pace = None
    
    # Calculate cadence metrics
    valid_cadences = [c for c in trackpoints['cadences'] if c is not None]
    avg_cadence = float(np.mean(valid_cadences)) if valid_cadences else None
    max_cadence = float(np.max(valid_cadences)) if valid_cadences else None
    min_cadence = float(np.min(valid_cadences)) if valid_cadences else None
    
    # Calculate vertical oscillation metrics
    valid_vos = [vo for vo in trackpoints['vertical_oscillations'] if vo is not None]
    avg_vertical_oscillation = float(np.mean(valid_vos)) if valid_vos else None
    max_vertical_oscillation = float(np.max(valid_vos)) if valid_vos else None
    
    # Calculate stride length metrics
    valid_strides = [s for s in trackpoints['stride_lengths'] if s is not None]
    avg_stride_length = float(np.mean(valid_strides)) if valid_strides else None
    
    # Calculate ground contact time metrics
    valid_gcts = [gct for gct in trackpoints['ground_contact_times'] if gct is not None]
    avg_gct = float(np.mean(valid_gcts)) if valid_gcts else None
    
    # Calculate ground contact balance
    valid_gcbs = [gcb for gcb in trackpoints['ground_contact_balance'] if gcb is not None]
    avg_gcb = float(np.mean(valid_gcbs)) if valid_gcbs else None
    
    # Analyze cadence consistency
    if valid_cadences:
        cadence_std = float(np.std(valid_cadences))
        cadence_cv = cadence_std / avg_cadence if avg_cadence > 0 else None
        if cadence_cv:
            if cadence_cv < 0.05:
                cadence_consistency = "Very Consistent"
            elif cadence_cv < 0.10:
                cadence_consistency = "Consistent"
            else:
                cadence_consistency = "Variable"
        else:
            cadence_consistency = "Unknown"
    else:
        cadence_std = None
        cadence_cv = None
        cadence_consistency = "No Data"
    
    # Analyze vertical oscillation (lower is better for efficiency)
    if valid_vos:
        vo_std = float(np.std(valid_vos))
        if avg_vertical_oscillation:
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
        vo_std = None
        vo_assessment = "No Data"
    
    # Advanced Metrics - Cardiac Drift
    cardiac_drift = calculate_cardiac_drift(heart_rates, speeds)
    
    # Advanced Metrics - Pacing Variance
    pacing_variance = calculate_pacing_variance(speeds)
    
    # Build result dictionary
    result = {
        'basic_stats': {
            'total_distance_meters': total_distance_meters,
            'total_distance_km': round(total_distance_km, 2),
            'total_duration_seconds': total_duration_seconds,
            'total_duration_minutes': round(total_duration_minutes, 2),
            'total_duration_formatted': str(total_duration) if len(times) > 1 else "0:00:00",
            'avg_heart_rate': round(avg_hr, 1) if avg_hr else None,
            'avg_speed_kmh': round(avg_speed, 2) if avg_speed else None,
            'avg_pace': avg_pace,
            'num_trackpoints': len(times)
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
        'vertical_oscillation': {
            'avg_vertical_oscillation_cm': round(avg_vertical_oscillation, 2) if avg_vertical_oscillation else None,
            'max_vertical_oscillation_cm': round(max_vertical_oscillation, 2) if max_vertical_oscillation else None,
            'vertical_oscillation_std': round(vo_std, 2) if vo_std else None,
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
    # Test the analyzer
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "Runing_Today.tcx"
    
    try:
        print(f"Analyzing TCX file: {file_path}")
        print("=" * 60)
        
        result = analyze_tcx(file_path)
        
        print("\nBasic Stats:")
        print(f"  Total Distance: {result['basic_stats']['total_distance_km']} km")
        print(f"  Total Duration: {result['basic_stats']['total_duration_formatted']}")
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
            print(f"  Max Cadence: {cadence['max_cadence']} spm")
            print(f"  Min Cadence: {cadence['min_cadence']} spm")
            print(f"  Consistency: {cadence['cadence_consistency']}")
        else:
            print(f"  No cadence data available")
        
        print("\nVertical Oscillation:")
        vo = result['vertical_oscillation']
        if vo['avg_vertical_oscillation_cm']:
            print(f"  Average: {vo['avg_vertical_oscillation_cm']} cm")
            print(f"  Max: {vo['max_vertical_oscillation_cm']} cm")
            print(f"  Assessment: {vo['assessment']}")
        else:
            print(f"  No vertical oscillation data available")
        
        print("\nStride Metrics:")
        stride = result['stride_metrics']
        if stride['avg_stride_length_m']:
            print(f"  Average Stride Length: {stride['avg_stride_length_m']} m")
        else:
            print(f"  No stride length data available")
        
        print("\nGround Contact:")
        gct = result['ground_contact']
        if gct['avg_ground_contact_time_ms']:
            print(f"  Average GCT: {gct['avg_ground_contact_time_ms']} ms")
            print(f"  Balance: {gct['avg_ground_contact_balance']}%")
        else:
            print(f"  No ground contact data available")
        
        print("\n" + "=" * 60)
        
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
