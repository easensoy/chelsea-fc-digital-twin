import requests
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import base64
from urllib.parse import urlencode

logger = logging.getLogger('core.exports')

class PowerBIConnector:
    
    def __init__(self):
        self.logger = logging.getLogger('core.exports')
        self.config = settings.POWERBI_CONFIG
        self.client_id = self.config.get('CLIENT_ID')
        self.client_secret = self.config.get('CLIENT_SECRET')
        self.tenant_id = self.config.get('TENANT_ID')
        self.workspace_id = self.config.get('WORKSPACE_ID')
        self.base_url = 'https://api.powerbi.com/v1.0/myorg'
        self.auth_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        
    def upload_data(self, export_data):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain Power BI access token'}
            
            upload_results = {}
            
            for data_source_name, data_source in export_data['data_sources'].items():
                if not data_source['data']:
                    continue
                
                dataset_result = self._create_or_update_dataset(
                    access_token, 
                    data_source_name, 
                    data_source
                )
                
                if dataset_result['success']:
                    rows_result = self._upload_rows(
                        access_token,
                        dataset_result['dataset_id'],
                        data_source_name,
                        data_source['data']
                    )
                    upload_results[data_source_name] = rows_result
                else:
                    upload_results[data_source_name] = dataset_result
            
            overall_success = all(result.get('success', False) for result in upload_results.values())
            
            return {
                'success': overall_success,
                'upload_timestamp': timezone.now().isoformat(),
                'results': upload_results,
                'total_datasets': len(upload_results),
                'successful_uploads': sum(1 for r in upload_results.values() if r.get('success', False))
            }
            
        except Exception as e:
            self.logger.error(f"Power BI upload failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_access_token(self):
        cache_key = 'powerbi_access_token'
        token = cache.get(cache_key)
        
        if token:
            return token
        
        try:
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'https://analysis.windows.net/powerbi/api/.default'
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                self.auth_url, 
                data=urlencode(auth_data), 
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                
                cache.set(cache_key, access_token, expires_in - 300)
                
                self.logger.info("Power BI access token obtained successfully")
                return access_token
            else:
                self.logger.error(f"Failed to get Power BI access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error obtaining Power BI access token: {str(e)}")
            return None
    
    def _create_or_update_dataset(self, access_token, table_name, data_source):
        dataset_name = f"Chelsea FC {table_name.replace('_', ' ').title()}"
        
        existing_dataset_id = self._find_existing_dataset(access_token, dataset_name)
        
        if existing_dataset_id:
            return {
                'success': True,
                'dataset_id': existing_dataset_id,
                'action': 'found_existing'
            }
        
        try:
            dataset_schema = self._create_dataset_schema(dataset_name, table_name, data_source)
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets'
            
            response = requests.post(
                url,
                json=dataset_schema,
                headers=headers,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                dataset_data = response.json()
                dataset_id = dataset_data['id']
                
                self.logger.info(f"Power BI dataset created: {dataset_name} (ID: {dataset_id})")
                
                return {
                    'success': True,
                    'dataset_id': dataset_id,
                    'action': 'created'
                }
            else:
                self.logger.error(f"Failed to create Power BI dataset: {response.status_code} - {response.text}")
                return {'success': False, 'error': f"Dataset creation failed: {response.text}"}
                
        except Exception as e:
            self.logger.error(f"Error creating Power BI dataset: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _find_existing_dataset(self, access_token, dataset_name):
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                datasets = response.json().get('value', [])
                
                for dataset in datasets:
                    if dataset['name'] == dataset_name:
                        return dataset['id']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding existing dataset: {str(e)}")
            return None
    
    def _create_dataset_schema(self, dataset_name, table_name, data_source):
        columns = []
        
        if not data_source['data']:
            return {
                'name': dataset_name,
                'tables': [
                    {
                        'name': table_name,
                        'columns': [
                            {'name': 'placeholder', 'dataType': 'string'}
                        ]
                    }
                ]
            }
        
        sample_record = data_source['data'][0]
        
        for column_name, value in sample_record.items():
            column_type = self._determine_powerbi_data_type(value, column_name)
            
            columns.append({
                'name': column_name,
                'dataType': column_type
            })
        
        return {
            'name': dataset_name,
            'tables': [
                {
                    'name': table_name,
                    'columns': columns
                }
            ]
        }
    
    def _determine_powerbi_data_type(self, value, column_name):
        if value is None:
            return 'string'
        
        if isinstance(value, bool):
            return 'bool'
        
        if isinstance(value, int):
            return 'int64'
        
        if isinstance(value, float):
            return 'double'
        
        if isinstance(value, str):
            if 'date' in column_name.lower() and self._is_date_string(value):
                return 'dateTime'
            elif column_name.lower().endswith('_id') or column_name.lower() == 'id':
                return 'string'
            elif column_name.lower().endswith('_pct') or 'percentage' in column_name.lower():
                return 'double'
            else:
                return 'string'
        
        return 'string'
    
    def _is_date_string(self, value):
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    def _upload_rows(self, access_token, dataset_id, table_name, rows_data):
        try:
            if not rows_data:
                return {'success': True, 'rows_uploaded': 0, 'message': 'No data to upload'}
            
            self._clear_table_rows(access_token, dataset_id, table_name)
            
            batch_size = 1000
            total_rows = len(rows_data)
            uploaded_rows = 0
            
            for i in range(0, total_rows, batch_size):
                batch = rows_data[i:i + batch_size]
                
                batch_result = self._upload_batch(access_token, dataset_id, table_name, batch)
                
                if batch_result['success']:
                    uploaded_rows += len(batch)
                    self.logger.info(f"Uploaded batch {i//batch_size + 1}: {len(batch)} rows to {table_name}")
                else:
                    self.logger.error(f"Failed to upload batch {i//batch_size + 1} to {table_name}")
                    return batch_result
            
            return {
                'success': True,
                'rows_uploaded': uploaded_rows,
                'total_batches': (total_rows + batch_size - 1) // batch_size
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading rows to Power BI: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _clear_table_rows(self, access_token, dataset_id, table_name):
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows'
            
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 204]:
                self.logger.info(f"Cleared existing rows from table: {table_name}")
            else:
                self.logger.warning(f"Failed to clear table rows: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error clearing table rows: {str(e)}")
    
    def _upload_batch(self, access_token, dataset_id, table_name, batch_data):
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}/tables/{table_name}/rows'
            
            payload = {'rows': batch_data}
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code in [200, 201]:
                return {'success': True}
            else:
                error_message = f"Batch upload failed: {response.status_code} - {response.text}"
                return {'success': False, 'error': error_message}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def refresh_dataset(self, dataset_name):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain access token'}
            
            dataset_id = self._find_existing_dataset(access_token, dataset_name)
            if not dataset_id:
                return {'success': False, 'error': f'Dataset {dataset_name} not found'}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}/refreshes'
            
            response = requests.post(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 202]:
                self.logger.info(f"Dataset refresh initiated: {dataset_name}")
                return {'success': True, 'message': 'Dataset refresh initiated'}
            else:
                error_message = f"Dataset refresh failed: {response.status_code} - {response.text}"
                return {'success': False, 'error': error_message}
                
        except Exception as e:
            self.logger.error(f"Error refreshing dataset: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_dataset_info(self, dataset_name):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain access token'}
            
            dataset_id = self._find_existing_dataset(access_token, dataset_name)
            if not dataset_id:
                return {'success': False, 'error': f'Dataset {dataset_name} not found'}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                dataset_info = response.json()
                
                refreshes_url = f'{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}/refreshes'
                refreshes_response = requests.get(refreshes_url, headers=headers, timeout=30)
                
                refresh_history = []
                if refreshes_response.status_code == 200:
                    refresh_history = refreshes_response.json().get('value', [])
                
                return {
                    'success': True,
                    'dataset_info': {
                        'id': dataset_info['id'],
                        'name': dataset_info['name'],
                        'configured_by': dataset_info.get('configuredBy', 'Unknown'),
                        'created_date': dataset_info.get('createdDate'),
                        'last_refresh': refresh_history[0].get('endTime') if refresh_history else None,
                        'refresh_status': refresh_history[0].get('status') if refresh_history else None,
                        'tables_count': len(dataset_info.get('tables', [])),
                        'refresh_history_count': len(refresh_history)
                    }
                }
            else:
                return {'success': False, 'error': f'Failed to get dataset info: {response.text}'}
                
        except Exception as e:
            self.logger.error(f"Error getting dataset info: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def test_connection(self):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain access token'}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                workspace_info = response.json()
                return {
                    'success': True,
                    'connection_status': 'Connected',
                    'workspace_name': workspace_info.get('name', 'Unknown'),
                    'workspace_id': workspace_info.get('id'),
                    'test_timestamp': timezone.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Connection test failed: {response.status_code} - {response.text}'
                }
                
        except Exception as e:
            self.logger.error(f"Power BI connection test failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_dashboard_report(self, report_config):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain access token'}
            
            report_definition = {
                'name': report_config.get('name', 'Chelsea FC Analytics Report'),
                'datasetId': report_config.get('dataset_id'),
                'pages': self._create_report_pages(report_config.get('report_type', 'overview'))
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/reports'
            
            response = requests.post(
                url,
                json=report_definition,
                headers=headers,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                report_data = response.json()
                return {
                    'success': True,
                    'report_id': report_data['id'],
                    'report_name': report_data['name'],
                    'web_url': report_data.get('webUrl')
                }
            else:
                return {'success': False, 'error': f'Report creation failed: {response.text}'}
                
        except Exception as e:
            self.logger.error(f"Error creating dashboard report: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_report_pages(self, report_type):
        if report_type == 'player_performance':
            return [
                {
                    'name': 'Player Overview',
                    'visualizations': [
                        {'type': 'table', 'title': 'Player Statistics'},
                        {'type': 'bar_chart', 'title': 'Goals and Assists'},
                        {'type': 'line_chart', 'title': 'Performance Trends'}
                    ]
                }
            ]
        elif report_type == 'tactical_analysis':
            return [
                {
                    'name': 'Formation Analysis',
                    'visualizations': [
                        {'type': 'pie_chart', 'title': 'Formation Usage'},
                        {'type': 'scatter_plot', 'title': 'Formation Effectiveness'},
                        {'type': 'heat_map', 'title': 'Tactical Heat Map'}
                    ]
                }
            ]
        else:
            return [
                {
                    'name': 'Overview',
                    'visualizations': [
                        {'type': 'scorecard', 'title': 'Key Metrics'},
                        {'type': 'line_chart', 'title': 'Performance Trends'},
                        {'type': 'table', 'title': 'Recent Matches'}
                    ]
                }
            ]
    
    def get_workspace_datasets(self):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain access token'}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets'
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                datasets = response.json().get('value', [])
                
                chelsea_datasets = []
                for dataset in datasets:
                    if 'chelsea' in dataset['name'].lower():
                        chelsea_datasets.append({
                            'id': dataset['id'],
                            'name': dataset['name'],
                            'configured_by': dataset.get('configuredBy', 'Unknown'),
                            'created_date': dataset.get('createdDate'),
                            'is_refreshable': dataset.get('isRefreshable', False)
                        })
                
                return {
                    'success': True,
                    'total_datasets': len(datasets),
                    'chelsea_datasets': chelsea_datasets,
                    'chelsea_datasets_count': len(chelsea_datasets)
                }
            else:
                return {'success': False, 'error': f'Failed to get datasets: {response.text}'}
                
        except Exception as e:
            self.logger.error(f"Error getting workspace datasets: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_dataset(self, dataset_name):
        try:
            access_token = self._get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to obtain access token'}
            
            dataset_id = self._find_existing_dataset(access_token, dataset_name)
            if not dataset_id:
                return {'success': False, 'error': f'Dataset {dataset_name} not found'}
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f'{self.base_url}/groups/{self.workspace_id}/datasets/{dataset_id}'
            
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code in [200, 204]:
                self.logger.info(f"Dataset deleted: {dataset_name}")
                return {'success': True, 'message': f'Dataset {dataset_name} deleted successfully'}
            else:
                return {'success': False, 'error': f'Dataset deletion failed: {response.text}'}
                
        except Exception as e:
            self.logger.error(f"Error deleting dataset: {str(e)}")
            return {'success': False, 'error': str(e)}