# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 23:51:23 2022
@author: liraeng
Simple ZigZag calculation as a function.
Includes a hyperparameters optimization for the best calculation.
Created based on the ZigZag classical definition with depth and deviation.
Use for free, just give the credits. MIT License.
"""
import pandas as pd
from scipy.signal import find_peaks
def Zigzag2(_ohlc_df: pd.DataFrame, _depth: int, _deviation: float) -> (list, list):
     
    # dataset split into lists
    _high_data = _ohlc_df['high']
    _high_data_list = _high_data.tolist()
    _low_data = _ohlc_df['low']
    _low_data_list = _low_data.tolist()
    
    # converting the deviation from percent to decimal
    _deviation = _deviation / 100
    
    # looking for high indexes through peak analysis
    _high_indices, _ = find_peaks(_high_data.tolist(), distance=_depth)
    
    # looking for low indexes through peak analysis
    _low_indices, _ = find_peaks([_vl * -1 for _vl in _low_data.tolist()], distance=_depth)
    
    # loop variable controls
    filtered_pivot_indexes = []
    filtered_pivot_values = []
    
    # appeding pivots and sorting (time index)
    _all_indexes = _high_indices.tolist() + _low_indices.tolist()
    _all_indexes = sorted(_all_indexes)
    
    # filtering by consecutives peaks and valleys order
    _last_was_a_peak = False  # to control the kind of the last added point
    for _index in _all_indexes:
        
        # case for the first to be added
        if not filtered_pivot_indexes:  
            
            # appending first point
            filtered_pivot_indexes.append(_index)
            
            # first point being a peak
            if _high_indices[0] < _low_indices[0]:
                _last_was_a_peak = True
                filtered_pivot_values.append(_high_data_list[_index])
            
            # first point being a valley
            else:
                filtered_pivot_values.append(_low_data_list[_index])
            
            # skipping for the next loop
            continue
        
        # trigger control
        _t1 = _index in _high_indices
        _t2 = _index in _low_indices
        _t3 = _t1 and _last_was_a_peak
        _t4 = _t2 and not _last_was_a_peak
        
        # suppresing consecutive peaks
        if _t3 or _t4:
            
            # analysis for consecutive valleys
            if _last_was_a_peak:
                _last_added_point_value = filtered_pivot_values[-1]
                _current_point_value = _high_data_list[_index]
                
                # suppressing the last added valley for a lower valley level
                if _current_point_value >= _last_added_point_value:
                    
                    # removing the last added points
                    del filtered_pivot_indexes[-1]
                    del filtered_pivot_values[-1]
                    
                    # updating the new one
                    filtered_pivot_indexes.append(_index)
                    filtered_pivot_values.append(_high_data_list[_index])        
                else:
                    continue
            
            # analysis for consecutive peaks
            else:
                _last_added_point_value = filtered_pivot_values[-1]
                _current_point_value = _low_data_list[_index]
                
                # suppressing the last added valley for a lower valley level
                if _current_point_value <= _last_added_point_value:
                    
                    # removing the last added points
                    del filtered_pivot_indexes[-1]
                    del filtered_pivot_values[-1]
                    
                    # updating the new one
                    filtered_pivot_indexes.append(_index)
                    filtered_pivot_values.append(_low_data_list[_index])        
                else:
                    continue

        # case for the last point added was a peak
        elif _t2 and _last_was_a_peak:
            _last_was_a_peak = False
            filtered_pivot_indexes.append(_index)
            filtered_pivot_values.append(_low_data_list[_index])
        
        # case for the last point added was a valley
        elif _t1 and not _last_was_a_peak:
            _last_was_a_peak = True
            filtered_pivot_indexes.append(_index)
            filtered_pivot_values.append(_high_data_list[_index])
    
    # deviation filtering
    _total_deviation = (max(_high_data_list) - min(_low_data_list)) / min(_low_data_list)
    _minimal_deviation = abs(_total_deviation * _deviation)
    
    
    # filtering by the minimal deviation criteria
    for _index in range(len(filtered_pivot_values) - 1, 1, -1):
        try:
            _first_value = filtered_pivot_values[_index]
            _second_value = filtered_pivot_values[_index - 1]
            _variation = abs((_first_value - _second_value) / _first_value)
        
        # case for the remove of the last two points
        except IndexError:
            continue
        
        # case for not reaching the minimal deviation
        if _variation < _minimal_deviation:
            del filtered_pivot_values[_index]
            del filtered_pivot_indexes[_index]
            
            # alteration to keep the last pivot point
            if _index != len(filtered_pivot_values) - 1:
                del filtered_pivot_values[_index - 1]
                del filtered_pivot_indexes[_index - 1]
    
    return filtered_pivot_indexes, filtered_pivot_values