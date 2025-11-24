"""
REST API для AeroSim EDU
"""

from flask import Flask, jsonify, request
from functools import wraps
import json
from typing import Dict, Any


def create_api(simulator_class):
    """Создать REST API приложение"""
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # API версия
    API_VERSION = "v1"
    
    # Вспомогательные функции
    def require_json(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type должен быть application/json'}), 400
            return f(*args, **kwargs)
        return decorated_function
    
    # API Routes
    
    @app.route(f'/{API_VERSION}/info', methods=['GET'])
    def api_info():
        """Информация о API"""
        return jsonify({
            'name': 'AeroSim EDU REST API',
            'version': '1.0.0',
            'api_version': API_VERSION,
            'description': 'API для управления симулятором аэропорта',
        })
    
    @app.route(f'/{API_VERSION}/simulations', methods=['POST'])
    @require_json
    def create_simulation():
        """Создать новую симуляцию"""
        data = request.get_json()
        
        config = data.get('config', {})
        
        try:
            simulator = simulator_class(config)
            simulator.run()
            stats = simulator.get_statistics()
            
            return jsonify({
                'id': 1,  # В реальности - ID из БД
                'status': 'completed',
                'statistics': stats,
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route(f'/{API_VERSION}/simulations', methods=['GET'])
    def list_simulations():
        """Получить список симуляций"""
        return jsonify({
            'simulations': [
                {
                    'id': 1,
                    'timestamp': '2025-11-23T23:26:00',
                    'status': 'completed'
                }
            ]
        })
    
    @app.route(f'/{API_VERSION}/simulations/<int:sim_id>', methods=['GET'])
    def get_simulation(sim_id):
        """Получить симуляцию по ID"""
        return jsonify({
            'id': sim_id,
            'status': 'completed',
            'statistics': {}
        })
    
    @app.route(f'/{API_VERSION}/simulations/<int:sim_id>/results', methods=['GET'])
    def get_simulation_results(sim_id):
        """Получить результаты симуляции"""
        return jsonify({
            'id': sim_id,
            'results': {}
        })
    
    @app.route(f'/{API_VERSION}/export/csv', methods=['POST'])
    @require_json
    def export_csv():
        """Экспортировать в CSV"""
        return jsonify({'message': 'Экспорт в CSV'})
    
    @app.route(f'/{API_VERSION}/export/json', methods=['POST'])
    @require_json
    def export_json():
        """Экспортировать в JSON"""
        return jsonify({'message': 'Экспорт в JSON'})
    
    @app.route(f'/{API_VERSION}/export/pdf', methods=['POST'])
    @require_json
    def export_pdf():
        """Экспортировать в PDF"""
        return jsonify({'message': 'Экспорт в PDF'})
    
    @app.route(f'/{API_VERSION}/health', methods=['GET'])
    def health_check():
        """Проверка здоровья"""
        return jsonify({
            'status': 'ok',
            'service': 'AeroSim EDU',
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Не найдено',
            'code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Внутренняя ошибка сервера',
            'code': 500
        }), 500
    
    return app


class APIClient:
    """Клиент для работы с REST API"""
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API
        """
        self.base_url = base_url.rstrip('/')
        self.api_version = 'v1'
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Выполнить запрос"""
        try:
            import requests
            
            url = f"{self.base_url}/{self.api_version}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data or {})
            elif method == 'PUT':
                response = requests.put(url, json=data or {})
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                raise ValueError(f"Неизвестный метод: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except ImportError:
            print("Требуется установить requests: pip install requests")
            return {}
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return {'error': str(e)}
    
    def create_simulation(self, config: Dict) -> Dict:
        """Создать новую симуляцию"""
        return self._make_request('POST', '/simulations', {'config': config})
    
    def list_simulations(self) -> Dict:
        """Получить список симуляций"""
        return self._make_request('GET', '/simulations')
    
    def get_simulation(self, sim_id: int) -> Dict:
        """Получить симуляцию"""
        return self._make_request('GET', f'/simulations/{sim_id}')
    
    def get_results(self, sim_id: int) -> Dict:
        """Получить результаты"""
        return self._make_request('GET', f'/simulations/{sim_id}/results')
    
    def health_check(self) -> Dict:
        """Проверить здоровье"""
        return self._make_request('GET', '/health')
