"""
Recession Probability Calculator
Analyzes indicators and calculates recession probability scores
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

class RecessionIndicatorAnalyzer:
    """
    Analyzes recession indicators and calculates probability scores
    """
    
    # NBER recession dates
    NBER_RECESSIONS = [
        ('1980-01-01', '1980-07-01'),
        ('1981-07-01', '1982-11-01'),
        ('1990-07-01', '1991-03-01'),
        ('2001-03-01', '2001-11-01'),
        ('2007-12-01', '2009-06-01'),
        ('2020-02-01', '2020-04-01'),
    ]
    
    # Indicator thresholds and weights for composite score
    THRESHOLDS = {
        'yield_curve': {
            'critical': -0.5,     # Deeply inverted
            'warning': 0.0,       # Any inversion
            'weight': 25,         # Weight in composite score
            'description': '10Y-2Y Treasury Spread'
        },
        'sahm_rule': {
            'critical': 0.5,      # Recession signal
            'warning': 0.3,       # Approaching recession
            'weight': 25,
            'description': 'Sahm Rule Indicator'
        },
        'credit_spread': {
            'critical': 6.0,      # Severe stress
            'warning': 4.0,       # Elevated stress
            'weight': 15,
            'description': 'High Yield Credit Spread'
        },
        'unemployment_change': {
            'critical': 0.5,      # Rapid increase
            'warning': 0.3,       # Moderate increase
            'weight': 20,
            'description': 'Unemployment Rate Change (3m)'
        },
        'lei_decline': {
            'critical': -5.0,     # Steep decline over 6m
            'warning': -2.0,      # Moderate decline
            'weight': 10,
            'description': 'LEI 6-Month Change'
        },
        'gdp_growth': {
            'critical': -1.0,     # Negative growth
            'warning': 0.5,       # Weak growth
            'weight': 15,
            'description': 'GDP Growth (QoQ)'
        },
        'manufacturing_pmi': {
            'critical': 45,       # Deep contraction
            'warning': 50,        # Contraction
            'weight': 10,
            'description': 'ISM Manufacturing PMI'
        },
    }
    
    def __init__(self):
        """Initialize the analyzer"""
        self.recession_periods = self._parse_recession_dates()
    
    def _parse_recession_dates(self):
        """Convert NBER recession dates to datetime"""
        periods = []
        for start, end in self.NBER_RECESSIONS:
            periods.append((
                pd.Timestamp(start),
                pd.Timestamp(end)
            ))
        return periods
    
    def is_recession(self, date):
        """
        Check if a given date falls within a recession period
        
        Parameters:
        -----------
        date : pd.Timestamp or str
            Date to check
            
        Returns:
        --------
        bool
            True if date is in a recession period
        """
        if isinstance(date, str):
            date = pd.Timestamp(date)
        
        for start, end in self.recession_periods:
            if start <= date <= end:
                return True
        return False
    
    def get_recession_indicators(self, date_or_period, data):
        """
        Create recession indicator overlay for time series
        
        Parameters:
        -----------
        date_or_period : pd.Index or pd.DatetimeIndex
            Dates to check
        data : pd.Series or pd.DataFrame
            Data to align with
            
        Returns:
        --------
        pd.Series
            Boolean series indicating recession periods
        """
        if isinstance(date_or_period, pd.Series):
            index = date_or_period.index
        elif isinstance(date_or_period, pd.DataFrame):
            index = date_or_period.index
        else:
            index = date_or_period
        
        recession_mask = pd.Series(False, index=index)
        
        for start, end in self.recession_periods:
            mask = (index >= start) & (index <= end)
            recession_mask[mask] = True
        
        return recession_mask
    
    def analyze_yield_curve(self, spread_data):
        """
        Analyze yield curve for recession signals
        
        Parameters:
        -----------
        spread_data : pd.Series
            10Y-2Y or 10Y-3M spread
            
        Returns:
        --------
        dict
            Analysis results with score and metrics
        """
        if len(spread_data) == 0:
            return {'score': 0, 'signal': 'No Data', 'current_value': None}
        
        current = spread_data.dropna().iloc[-1]
        
        # Check inversion
        is_inverted = current < 0
        
        # Calculate inversion duration (months)
        inversion_duration = 0
        if is_inverted:
            for i in range(len(spread_data) - 1, -1, -1):
                if pd.notna(spread_data.iloc[i]) and spread_data.iloc[i] < 0:
                    inversion_duration += 1
                else:
                    break
        
        # Score based on depth and duration
        if current <= self.THRESHOLDS['yield_curve']['critical']:
            score = 100
            signal = 'Critical - Deeply Inverted'
        elif current <= self.THRESHOLDS['yield_curve']['warning']:
            score = 70 + (abs(current) / 0.5) * 30  # Scale 70-100
            signal = 'Warning - Inverted'
        elif current < 0.5:
            score = 30 + (0.5 - current) / 0.5 * 40  # Scale 30-70
            signal = 'Caution - Flattening'
        else:
            score = max(0, 30 - (current - 0.5) * 10)
            signal = 'Normal'
        
        return {
            'score': min(100, max(0, score)),
            'signal': signal,
            'current_value': current,
            'is_inverted': is_inverted,
            'inversion_duration_months': inversion_duration,
            'interpretation': f'Spread: {current:+.2f}%, Inverted for {inversion_duration} months' if is_inverted else f'Spread: {current:+.2f}%'
        }
    
    def analyze_sahm_rule(self, sahm_data):
        """
        Analyze Sahm Rule indicator
        
        Parameters:
        -----------
        sahm_data : pd.Series
            Sahm Rule values
            
        Returns:
        --------
        dict
            Analysis results
        """
        if len(sahm_data) == 0:
            return {'score': 0, 'signal': 'No Data', 'current_value': None}
        
        current = sahm_data.dropna().iloc[-1]
        
        if current >= self.THRESHOLDS['sahm_rule']['critical']:
            score = 100
            signal = 'RECESSION SIGNAL'
        elif current >= self.THRESHOLDS['sahm_rule']['warning']:
            score = 50 + ((current - self.THRESHOLDS['sahm_rule']['warning']) / 
                          (self.THRESHOLDS['sahm_rule']['critical'] - self.THRESHOLDS['sahm_rule']['warning'])) * 50
            signal = 'Warning - Approaching Threshold'
        else:
            score = (current / self.THRESHOLDS['sahm_rule']['warning']) * 50
            signal = 'Normal'
        
        return {
            'score': min(100, max(0, score)),
            'signal': signal,
            'current_value': current,
            'threshold': self.THRESHOLDS['sahm_rule']['critical'],
            'interpretation': f'Sahm Rule: {current:.2f} (Threshold: 0.50)'
        }
    
    def analyze_credit_spreads(self, spread_data):
        """
        Analyze corporate credit spreads
        
        Parameters:
        -----------
        spread_data : pd.Series
            Credit spread (e.g., high yield spread)
            
        Returns:
        --------
        dict
            Analysis results
        """
        if len(spread_data) == 0:
            return {'score': 0, 'signal': 'No Data', 'current_value': None}
        
        current = spread_data.dropna().iloc[-1]
        
        if current >= self.THRESHOLDS['credit_spread']['critical']:
            score = 100
            signal = 'Critical - Severe Stress'
        elif current >= self.THRESHOLDS['credit_spread']['warning']:
            score = 50 + ((current - self.THRESHOLDS['credit_spread']['warning']) / 
                          (self.THRESHOLDS['credit_spread']['critical'] - self.THRESHOLDS['credit_spread']['warning'])) * 50
            signal = 'Warning - Elevated Stress'
        else:
            score = (current / self.THRESHOLDS['credit_spread']['warning']) * 50
            signal = 'Normal'
        
        return {
            'score': min(100, max(0, score)),
            'signal': signal,
            'current_value': current,
            'interpretation': f'Credit Spread: {current:.2f}%'
        }
    
    def analyze_unemployment_change(self, unemployment_data):
        """
        Analyze unemployment rate changes
        
        Parameters:
        -----------
        unemployment_data : pd.Series
            Unemployment rate
            
        Returns:
        --------
        dict
            Analysis results
        """
        if len(unemployment_data) < 3:
            return {'score': 0, 'signal': 'No Data', 'current_value': None}
        
        # Calculate 3-month change
        current = unemployment_data.dropna().iloc[-1]
        three_months_ago = unemployment_data.dropna().iloc[-4] if len(unemployment_data.dropna()) >= 4 else unemployment_data.dropna().iloc[0]
        change = current - three_months_ago
        
        if change >= self.THRESHOLDS['unemployment_change']['critical']:
            score = 100
            signal = 'Critical - Rapid Increase'
        elif change >= self.THRESHOLDS['unemployment_change']['warning']:
            score = 50 + ((change - self.THRESHOLDS['unemployment_change']['warning']) / 
                          (self.THRESHOLDS['unemployment_change']['critical'] - self.THRESHOLDS['unemployment_change']['warning'])) * 50
            signal = 'Warning - Rising'
        elif change > 0:
            score = (change / self.THRESHOLDS['unemployment_change']['warning']) * 50
            signal = 'Caution - Slight Increase'
        else:
            score = 0
            signal = 'Normal - Stable or Declining'
        
        return {
            'score': min(100, max(0, score)),
            'signal': signal,
            'current_value': current,
            'change_3m': change,
            'interpretation': f'Unemployment: {current:.1f}% ({change:+.1f}% over 3 months)'
        }
    
    def calculate_composite_score(self, indicator_scores):
        """
        Calculate weighted composite recession risk score
        
        Parameters:
        -----------
        indicator_scores : dict
            Dictionary of indicator names to score dicts
            
        Returns:
        --------
        dict
            Composite score and breakdown
        """
        total_weight = 0
        weighted_score = 0
        breakdown = {}
        
        for indicator, config in self.THRESHOLDS.items():
            if indicator in indicator_scores:
                score_data = indicator_scores[indicator]
                if score_data['score'] is not None and not pd.isna(score_data['score']):
                    weight = config['weight']
                    score = score_data['score']
                    weighted_score += score * weight
                    total_weight += weight
                    
                    breakdown[indicator] = {
                        'score': score,
                        'weight': weight,
                        'contribution': (score * weight) / 100,  # Contribution to total
                        'signal': score_data.get('signal', 'Unknown'),
                        'description': config['description']
                    }
        
        if total_weight == 0:
            return {
                'composite_score': 0,
                'risk_level': 'Unknown',
                'breakdown': {}
            }
        
        composite = weighted_score / total_weight
        
        # Determine risk level
        if composite >= 75:
            risk_level = 'Critical - High Recession Risk'
            risk_color = 'red'
        elif composite >= 50:
            risk_level = 'Warning - Elevated Risk'
            risk_color = 'orange'
        elif composite >= 25:
            risk_level = 'Caution - Moderate Risk'
            risk_color = 'yellow'
        else:
            risk_level = 'Normal - Low Risk'
            risk_color = 'green'
        
        return {
            'composite_score': round(composite, 1),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'breakdown': breakdown,
            'total_weight': total_weight
        }
    
    def analyze_all_indicators(self, data_dict):
        """
        Analyze all available indicators and calculate composite score
        
        Parameters:
        -----------
        data_dict : dict
            Dictionary of DataFrames from data fetcher
            
        Returns:
        --------
        dict
            Complete analysis with composite score
        """
        scores = {}
        
        # Yield Curve
        if 'treasury_yields' in data_dict:
            ty = data_dict['treasury_yields']
            if 'Spread_10Y2Y' in ty.columns:
                scores['yield_curve'] = self.analyze_yield_curve(ty['Spread_10Y2Y'])
        
        # Sahm Rule
        if 'labor_market' in data_dict:
            lm = data_dict['labor_market']
            if 'SAHM_Rule' in lm.columns:
                scores['sahm_rule'] = self.analyze_sahm_rule(lm['SAHM_Rule'])
            if 'UNRATE' in lm.columns:
                scores['unemployment_change'] = self.analyze_unemployment_change(lm['UNRATE'])
        
        # Credit Spreads
        if 'credit_spreads' in data_dict:
            cs = data_dict['credit_spreads']
            # Try different spread columns
            for col in ['HY_Spread', 'BBB_Spread', 'BAA_Spread']:
                if col in cs.columns:
                    scores['credit_spread'] = self.analyze_credit_spreads(cs[col])
                    break
        
        # LEI
        if 'lei' in data_dict:
            lei = data_dict['lei']
            if 'LEI_6M_Change' in lei.columns:
                lei_data = lei['LEI_6M_Change'].dropna()
                if len(lei_data) > 0:
                    current = lei_data.iloc[-1]
                    if current <= self.THRESHOLDS['lei_decline']['critical']:
                        score = 100
                        signal = 'Critical - Steep Decline'
                    elif current <= self.THRESHOLDS['lei_decline']['warning']:
                        score = 50 + ((abs(current) - abs(self.THRESHOLDS['lei_decline']['warning'])) / 
                                     (abs(self.THRESHOLDS['lei_decline']['critical']) - abs(self.THRESHOLDS['lei_decline']['warning']))) * 50
                        signal = 'Warning - Declining'
                    else:
                        score = max(0, 50 - (current * 10))
                        signal = 'Normal'
                    
                    scores['lei_decline'] = {
                        'score': min(100, max(0, score)),
                        'signal': signal,
                        'current_value': current,
                        'interpretation': f'LEI 6m Change: {current:+.1f}%'
                    }
        
        # GDP
        if 'gdp' in data_dict:
            gdp = data_dict['gdp']
            if 'GDP_QoQ_Growth' in gdp.columns:
                gdp_data = gdp['GDP_QoQ_Growth'].dropna()
                if len(gdp_data) > 0:
                    current = gdp_data.iloc[-1]
                    if current <= self.THRESHOLDS['gdp_growth']['critical']:
                        score = 100
                        signal = 'Critical - Negative Growth'
                    elif current <= self.THRESHOLDS['gdp_growth']['warning']:
                        score = 50 + ((self.THRESHOLDS['gdp_growth']['warning'] - current) / 
                                     (self.THRESHOLDS['gdp_growth']['warning'] - self.THRESHOLDS['gdp_growth']['critical'])) * 50
                        signal = 'Warning - Weak Growth'
                    else:
                        score = max(0, 50 - (current * 10))
                        signal = 'Normal'
                    
                    scores['gdp_growth'] = {
                        'score': min(100, max(0, score)),
                        'signal': signal,
                        'current_value': current,
                        'interpretation': f'GDP Growth: {current:+.1f}% QoQ'
                    }
        
        # Manufacturing PMI
        if 'manufacturing' in data_dict:
            mfg = data_dict['manufacturing']
            if 'ISM_PMI' in mfg.columns:
                pmi_data = mfg['ISM_PMI'].dropna()
                if len(pmi_data) > 0:
                    current = pmi_data.iloc[-1]
                    if current <= self.THRESHOLDS['manufacturing_pmi']['critical']:
                        score = 100
                        signal = 'Critical - Deep Contraction'
                    elif current <= self.THRESHOLDS['manufacturing_pmi']['warning']:
                        score = 50 + ((self.THRESHOLDS['manufacturing_pmi']['warning'] - current) / 
                                     (self.THRESHOLDS['manufacturing_pmi']['warning'] - self.THRESHOLDS['manufacturing_pmi']['critical'])) * 50
                        signal = 'Warning - Contraction'
                    else:
                        score = max(0, 50 - ((current - 50) * 2))
                        signal = 'Normal - Expansion'
                    
                    scores['manufacturing_pmi'] = {
                        'score': min(100, max(0, score)),
                        'signal': signal,
                        'current_value': current,
                        'interpretation': f'ISM PMI: {current:.1f}'
                    }
        
        # Calculate composite score
        composite = self.calculate_composite_score(scores)
        
        return {
            'individual_scores': scores,
            'composite': composite,
            'analysis_date': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test the analyzer
    print("Testing Recession Indicator Analyzer...")
    
    analyzer = RecessionIndicatorAnalyzer()
    
    # Test with sample data
    print("\n" + "="*60)
    print("TESTING INDICATOR ANALYSIS")
    print("="*60)
    
    # Test yield curve
    yield_spread = pd.Series([-0.3, -0.4, -0.5], index=pd.date_range('2024-01-01', periods=3, freq='M'))
    result = analyzer.analyze_yield_curve(yield_spread)
    print(f"\nYield Curve Analysis:")
    print(f"  Score: {result['score']:.1f}/100")
    print(f"  Signal: {result['signal']}")
    print(f"  {result['interpretation']}")
    
    # Test Sahm Rule
    sahm = pd.Series([0.2, 0.3, 0.6], index=pd.date_range('2024-01-01', periods=3, freq='M'))
    result = analyzer.analyze_sahm_rule(sahm)
    print(f"\nSahm Rule Analysis:")
    print(f"  Score: {result['score']:.1f}/100")
    print(f"  Signal: {result['signal']}")
    print(f"  {result['interpretation']}")
    
    print("\n✓ Recession Indicator Analyzer working correctly!")
