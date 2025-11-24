"""
Web интерфейс для AeroSim EDU с Flask
"""

from flask import Flask, render_template, jsonify, request
from src.core.simulator import AirportSimulator
from src.utils.logger import get_logger
import json
from threading import Thread


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

logger = get_logger(__name__)

# Глобальные переменные
current_simulation = None
simulation_stats = None


@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'name': 'AeroSim EDU - Web API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'Информация о API',
            'GET /api/status': 'Статус текущей симуляции',
            'POST /api/simulate': 'Запустить новую симуляцию',
            'GET /api/results': 'Получить результаты последней симуляции',
            'GET /api/config': 'Получить конфигурацию по умолчанию',
        }
    })


@app.route('/api/status')
def get_status():
    """Получить статус симуляции"""
    global current_simulation
    
    if current_simulation is None:
        return jsonify({'status': 'idle', 'message': 'Нет активной симуляции'})
    
    return jsonify({
        'status': 'running' if current_simulation.is_running else 'completed',
        'current_time': current_simulation.current_time,
        'end_time': current_simulation.end_time,
        'progress': (current_simulation.current_time / current_simulation.end_time * 100) 
                   if current_simulation.end_time > 0 else 0,
    })


@app.route('/api/simulate', methods=['POST'])
def start_simulation():
    """Запустить симуляцию"""
    global current_simulation, simulation_stats
    
    data = request.get_json() or {}
    
    config = {
        "duration": data.get("duration", 3600),
        "airport": {
            "num_runways": data.get("num_runways", 2),
            "num_terminals": data.get("num_terminals", 3),
            "gates_per_terminal": data.get("gates_per_terminal", 20),
        },
        "aircraft": {
            "initial_aircraft": data.get("initial_aircraft", 5),
        }
    }
    
    try:
        current_simulation = AirportSimulator(config)
        simulation_stats = None
        
        # Запустить в отдельном потоке
        def run_sim():
            global simulation_stats
            current_simulation.run()
            simulation_stats = current_simulation.get_statistics()
        
        thread = Thread(target=run_sim, daemon=True)
        thread.start()
        
        return jsonify({
            'status': 'started',
            'message': f'Симуляция запущена на {config["duration"]} сек',
            'config': config
        }), 202
    
    except Exception as e:
        logger.error(f"Ошибка при запуске симуляции: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/results')
def get_results():
    """Получить результаты"""
    global simulation_stats
    
    if simulation_stats is None:
        return jsonify({'error': 'Нет результатов'}), 404
    
    return jsonify(simulation_stats)


@app.route('/api/config')
def get_config():
    """Получить конфигурацию по умолчанию"""
    from config.default import DEFAULT_CONFIG
    return jsonify(DEFAULT_CONFIG)


@app.route('/api/health')
def health_check():
    """Проверка здоровья"""
    return jsonify({'status': 'ok', 'message': 'Сервер работает'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Не найдено'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


def run_web_server(host='127.0.0.1', port=5000, debug=False):
    """Запустить Web сервер"""
    logger.info(f"Запуск Web сервера на http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_web_server(debug=True)
