"""
Data Ingestion Service Lambda Function

This Lambda function handles data ingestion from NSW Government air quality APIs including:
- Fetching air quality data from NSW Government APIs
- Processing and normalizing data
- Storing data in DynamoDB
- Scheduled data updates via EventBridge
"""

import json
import os
import boto3
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
air_quality_table = dynamodb.Table(os.getenv('AIR_QUALITY_TABLE_NAME', 'asthma-guardian-air-quality'))

# NSW Government API endpoints
NSW_AIR_QUALITY_API_URL = os.getenv('NSW_AIR_QUALITY_API_URL', 'https://api.airquality.nsw.gov.au')
BOM_API_URL = os.getenv('BOM_API_URL', 'https://api.bom.gov.au')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for data ingestion service.
    
    Args:
        event: EventBridge or manual invocation event
        context: Lambda context
        
    Returns:
        Processing result
    """
    try:
        # Parse event type
        event_source = event.get('source', 'manual')
        
        if event_source == 'aws.events':
            # Scheduled ingestion
            return handle_scheduled_ingestion(event)
        else:
            # Manual ingestion
            return handle_manual_ingestion(event)
            
    except Exception as e:
        logger.error(f"Error in data ingestion: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Data ingestion failed',
                'message': str(e)
            })
        }

def handle_scheduled_ingestion(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle scheduled data ingestion from EventBridge.
    
    Args:
        event: EventBridge event
        
    Returns:
        Processing result
    """
    try:
        logger.info("Starting scheduled air quality data ingestion")
        
        # Ingest data for all NSW postcodes
        result = ingest_air_quality_data()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Scheduled ingestion completed',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled ingestion: {str(e)}")
        raise

def handle_manual_ingestion(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle manual data ingestion.
    
    Args:
        event: Manual invocation event
        
    Returns:
        Processing result
    """
    try:
        # Get postcodes from event or use default
        postcodes = event.get('postcodes', get_nsw_postcodes())
        
        logger.info(f"Starting manual air quality data ingestion for {len(postcodes)} postcodes")
        
        result = ingest_air_quality_data(postcodes)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Manual ingestion completed',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error in manual ingestion: {str(e)}")
        raise

def ingest_air_quality_data(postcodes: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Ingest air quality data for specified postcodes.
    
    Args:
        postcodes: List of postcodes to ingest data for
        
    Returns:
        Ingestion result
    """
    try:
        if not postcodes:
            postcodes = get_nsw_postcodes()
        
        results = {
            'total_postcodes': len(postcodes),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for postcode in postcodes:
            try:
                # Fetch air quality data for postcode
                air_quality_data = fetch_air_quality_data(postcode)
                
                if air_quality_data:
                    # Store data in DynamoDB
                    store_air_quality_data(postcode, air_quality_data)
                    results['successful'] += 1
                    logger.info(f"Successfully ingested data for postcode {postcode}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"No data available for postcode {postcode}")
                    
            except Exception as e:
                results['failed'] += 1
                error_msg = f"Error ingesting data for postcode {postcode}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in air quality data ingestion: {str(e)}")
        raise

def fetch_air_quality_data(postcode: str) -> Optional[Dict[str, Any]]:
    """
    Fetch air quality data from NSW Government API for a postcode.
    
    Args:
        postcode: NSW postcode
        
    Returns:
        Air quality data or None if not available
    """
    try:
        # Try NSW Government API first
        nsw_data = fetch_nsw_air_quality_data(postcode)
        if nsw_data:
            return nsw_data
        
        # Fallback to BOM API
        bom_data = fetch_bom_air_quality_data(postcode)
        if bom_data:
            return bom_data
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching air quality data for postcode {postcode}: {str(e)}")
        return None

def fetch_nsw_air_quality_data(postcode: str) -> Optional[Dict[str, Any]]:
    """
    Fetch air quality data from NSW Government API.
    
    Args:
        postcode: NSW postcode
        
    Returns:
        Air quality data or None if not available
    """
    try:
        # NSW Government air quality API endpoint
        url = f"{NSW_AIR_QUALITY_API_URL}/v1/air-quality/current"
        params = {
            'postcode': postcode,
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or 'data' not in data:
            return None
        
        # Process NSW Government data format
        return process_nsw_air_quality_data(data['data'], postcode)
        
    except Exception as e:
        logger.error(f"Error fetching NSW air quality data: {str(e)}")
        return None

def fetch_bom_air_quality_data(postcode: str) -> Optional[Dict[str, Any]]:
    """
    Fetch air quality data from BOM API as fallback.
    
    Args:
        postcode: NSW postcode
        
    Returns:
        Air quality data or None if not available
    """
    try:
        # BOM air quality API endpoint
        url = f"{BOM_API_URL}/v1/air-quality/current"
        params = {
            'postcode': postcode,
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or 'observations' not in data:
            return None
        
        # Process BOM data format
        return process_bom_air_quality_data(data['observations'], postcode)
        
    except Exception as e:
        logger.error(f"Error fetching BOM air quality data: {str(e)}")
        return None

def process_nsw_air_quality_data(data: Dict[str, Any], postcode: str) -> Dict[str, Any]:
    """
    Process NSW Government air quality data into standard format.
    
    Args:
        data: Raw NSW Government data
        postcode: NSW postcode
        
    Returns:
        Processed air quality data
    """
    try:
        # Extract location information
        location = data.get('location', {})
        latitude = location.get('latitude', 0.0)
        longitude = location.get('longitude', 0.0)
        
        # Extract air quality measurements
        measurements = data.get('measurements', {})
        
        # Calculate AQI (simplified calculation)
        aqi = calculate_aqi(measurements)
        quality_rating = get_quality_rating(aqi)
        
        return {
            'postcode': postcode,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'aqi': aqi,
            'quality_rating': quality_rating,
            'pm25': measurements.get('pm25', 0.0),
            'pm10': measurements.get('pm10', 0.0),
            'ozone': measurements.get('ozone', 0.0),
            'no2': measurements.get('no2', 0.0),
            'so2': measurements.get('so2', 0.0),
            'source': 'nsw_government'
        }
        
    except Exception as e:
        logger.error(f"Error processing NSW air quality data: {str(e)}")
        return None

def process_bom_air_quality_data(data: Dict[str, Any], postcode: str) -> Dict[str, Any]:
    """
    Process BOM air quality data into standard format.
    
    Args:
        data: Raw BOM data
        postcode: NSW postcode
        
    Returns:
        Processed air quality data
    """
    try:
        # Extract location information
        location = data.get('location', {})
        latitude = location.get('lat', 0.0)
        longitude = location.get('lon', 0.0)
        
        # Extract air quality measurements
        measurements = data.get('air_quality', {})
        
        # Calculate AQI (simplified calculation)
        aqi = calculate_aqi(measurements)
        quality_rating = get_quality_rating(aqi)
        
        return {
            'postcode': postcode,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'aqi': aqi,
            'quality_rating': quality_rating,
            'pm25': measurements.get('pm25', 0.0),
            'pm10': measurements.get('pm10', 0.0),
            'ozone': measurements.get('ozone', 0.0),
            'no2': measurements.get('no2', 0.0),
            'so2': measurements.get('so2', 0.0),
            'source': 'bom'
        }
        
    except Exception as e:
        logger.error(f"Error processing BOM air quality data: {str(e)}")
        return None

def calculate_aqi(measurements: Dict[str, float]) -> int:
    """
    Calculate Air Quality Index from pollutant measurements.
    
    Args:
        measurements: Pollutant measurements
        
    Returns:
        Calculated AQI value
    """
    try:
        # Simplified AQI calculation based on PM2.5 and PM10
        pm25 = measurements.get('pm25', 0.0)
        pm10 = measurements.get('pm10', 0.0)
        
        # Use the higher of PM2.5 and PM10 AQI
        pm25_aqi = calculate_pm25_aqi(pm25)
        pm10_aqi = calculate_pm10_aqi(pm10)
        
        return max(pm25_aqi, pm10_aqi)
        
    except Exception as e:
        logger.error(f"Error calculating AQI: {str(e)}")
        return 0

def calculate_pm25_aqi(pm25: float) -> int:
    """Calculate AQI for PM2.5."""
    if pm25 <= 12.0:
        return int((pm25 / 12.0) * 50)
    elif pm25 <= 35.4:
        return int(((pm25 - 12.1) / (35.4 - 12.1)) * (100 - 51) + 51)
    elif pm25 <= 55.4:
        return int(((pm25 - 35.5) / (55.4 - 35.5)) * (150 - 101) + 101)
    elif pm25 <= 150.4:
        return int(((pm25 - 55.5) / (150.4 - 55.5)) * (200 - 151) + 151)
    else:
        return 201

def calculate_pm10_aqi(pm10: float) -> int:
    """Calculate AQI for PM10."""
    if pm10 <= 54:
        return int((pm10 / 54) * 50)
    elif pm10 <= 154:
        return int(((pm10 - 55) / (154 - 55)) * (100 - 51) + 51)
    elif pm10 <= 254:
        return int(((pm10 - 155) / (254 - 155)) * (150 - 101) + 101)
    elif pm10 <= 354:
        return int(((pm10 - 255) / (354 - 255)) * (200 - 151) + 151)
    else:
        return 201

def get_quality_rating(aqi: int) -> str:
    """
    Get air quality rating based on AQI.
    
    Args:
        aqi: Air Quality Index value
        
    Returns:
        Quality rating string
    """
    if aqi <= 50:
        return "good"
    elif aqi <= 100:
        return "moderate"
    elif aqi <= 150:
        return "unhealthy_for_sensitive_groups"
    elif aqi <= 200:
        return "unhealthy"
    elif aqi <= 300:
        return "very_unhealthy"
    else:
        return "hazardous"

def store_air_quality_data(postcode: str, air_quality_data: Dict[str, Any]) -> None:
    """
    Store air quality data in DynamoDB.
    
    Args:
        postcode: NSW postcode
        air_quality_data: Air quality data to store
    """
    try:
        item = {
            'PK': f'LOCATION#{postcode}',
            'SK': f'TIMESTAMP#{air_quality_data["timestamp"]}',
            'GSI1PK': f'DATE#{air_quality_data["timestamp"][:10]}',
            'GSI1SK': f'LOCATION#{postcode}',
            'postcode': postcode,
            'latitude': air_quality_data['latitude'],
            'longitude': air_quality_data['longitude'],
            'timestamp': air_quality_data['timestamp'],
            'aqi': air_quality_data['aqi'],
            'quality_rating': air_quality_data['quality_rating'],
            'pm25': air_quality_data['pm25'],
            'pm10': air_quality_data['pm10'],
            'ozone': air_quality_data['ozone'],
            'no2': air_quality_data['no2'],
            'so2': air_quality_data['so2'],
            'source': air_quality_data['source'],
            'ttl': int((datetime.utcnow() + timedelta(days=7)).timestamp())
        }
        
        air_quality_table.put_item(Item=item)
        
    except Exception as e:
        logger.error(f"Error storing air quality data: {str(e)}")
        raise

def get_nsw_postcodes() -> List[str]:
    """
    Get list of NSW postcodes to ingest data for.
    
    Returns:
        List of NSW postcodes
    """
    # This would typically be stored in a configuration file or database
    # For now, return a sample of major NSW postcodes
    return [
        '2000',  # Sydney CBD
        '2001',  # Sydney
        '2010',  # Surry Hills
        '2011',  # Darlinghurst
        '2020',  # Mascot
        '2030',  # Bondi
        '2040',  # Leichhardt
        '2050',  # Newtown
        '2060',  # North Sydney
        '2070',  # Chatswood
        '2088',  # Mosman
        '2090',  # Cremorne
        '2100',  # Manly
        '2110',  # Ryde
        '2120',  # Parramatta
        '2130',  # Auburn
        '2140',  # Bankstown
        '2150',  # Castle Hill
        '2160',  # Liverpool
        '2170',  # Fairfield
        '2200',  # Canterbury
        '2210',  # Kogarah
        '2220',  # Hurstville
        '2230',  # Sutherland
        '2250',  # Gosford
        '2300',  # Newcastle
        '2320',  # Maitland
        '2325',  # Cessnock
        '2330',  # Singleton
        '2340',  # Tamworth
        '2350',  # Armidale
        '2400',  # Grafton
        '2450',  # Coffs Harbour
        '2500',  # Wollongong
        '2520',  # Port Kembla
        '2530',  # Dapto
        '2540',  # Nowra
        '2550',  # Ulladulla
        '2560',  # Campbelltown
        '2570',  # Camden
        '2580',  # Goulburn
        '2590',  # Yass
        '2600',  # Canberra
        '2610',  # Canberra
        '2620',  # Queanbeyan
        '2640',  # Albury
        '2650',  # Wagga Wagga
        '2700',  # Griffith
        '2710',  # Hay
        '2720',  # Leeton
        '2730',  # Deniliquin
        '2740',  # Dubbo
        '2750',  # Penrith
        '2760',  # St Marys
        '2770',  # Mount Druitt
        '2780',  # Katoomba
        '2790',  # Bathurst
        '2800',  # Orange
        '2810',  # Parkes
        '2820',  # Forbes
        '2830',  # Condobolin
        '2840',  # Cowra
        '2850',  # Mudgee
        '2860',  # Wellington
        '2870',  # Dubbo
        '2880',  # Broken Hill
        '2890',  # Wilcannia
        '2900',  # Tumbarumba
        '2910',  # Tumut
        '2920',  # Gundagai
        '2930',  # Cootamundra
        '2940',  # Young
        '2950',  # Boorowa
        '2960',  # Harden
        '2970',  # Murrumburrah
        '2980',  # Cootamundra
        '2990',  # Temora
        '3000',  # Melbourne (for reference)
    ]
