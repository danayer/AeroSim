"""
Многопоточная обработка для симулятора
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any, Dict
import queue
import time
from src.utils.logger import get_logger


class ThreadPoolSimulator:
    """Многопоточный симулятор"""
    
    def __init__(self, max_workers: int = 4):
        """
        Инициализация
        
        Args:
            max_workers: Максимальное количество рабочих потоков
        """
        self.logger = get_logger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
    
    def process_batch(self, tasks: List[Callable]) -> List[Any]:
        """
        Обработать пакет задач параллельно
        
        Args:
            tasks: Список callable объектов для выполнения
            
        Returns:
            Список результатов
        """
        futures = []
        results = []
        
        for task in tasks:
            future = self.executor.submit(task)
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Ошибка в потоке: {e}")
                results.append(None)
        
        return results
    
    def shutdown(self):
        """Завершить работу пула потоков"""
        self.executor.shutdown(wait=True)


class EventProcessorThread(threading.Thread):
    """Поток обработки событий"""
    
    def __init__(self, event_queue_in: queue.Queue, event_queue_out: queue.Queue):
        """
        Инициализация
        
        Args:
            event_queue_in: Входящая очередь событий
            event_queue_out: Исходящая очередь событий
        """
        super().__init__(daemon=True)
        self.logger = get_logger(__name__)
        self.event_queue_in = event_queue_in
        self.event_queue_out = event_queue_out
        self.running = False
    
    def run(self):
        """Основной цикл потока"""
        self.running = True
        self.logger.info(f"[{self.name}] Запущен")
        
        while self.running:
            try:
                # Получить событие с таймаутом
                event = self.event_queue_in.get(timeout=1.0)
                
                if event is None:  # Сигнал завершения
                    break
                
                # Обработать событие
                result = self._process_event(event)
                self.event_queue_out.put(result)
                
                self.event_queue_in.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"[{self.name}] Ошибка: {e}")
        
        self.logger.info(f"[{self.name}] Завершен")
    
    def _process_event(self, event: Dict) -> Dict:
        """Обработать отдельное событие"""
        # Имитация обработки
        time.sleep(0.01)
        return {**event, 'processed': True}
    
    def stop(self):
        """Остановить поток"""
        self.running = False


class ParallelEventProcessor:
    """Параллельный обработчик событий"""
    
    def __init__(self, num_threads: int = 4):
        """
        Инициализация
        
        Args:
            num_threads: Количество рабочих потоков
        """
        self.logger = get_logger(__name__)
        self.num_threads = num_threads
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.threads: List[EventProcessorThread] = []
        self._initialize_threads()
    
    def _initialize_threads(self):
        """Инициализировать рабочие потоки"""
        for i in range(self.num_threads):
            thread = EventProcessorThread(self.input_queue, self.output_queue)
            thread.name = f"EventProcessor-{i+1}"
            thread.start()
            self.threads.append(thread)
        
        self.logger.info(f"Инициализировано {self.num_threads} рабочих потоков")
    
    def submit_event(self, event: Dict):
        """Отправить событие на обработку"""
        self.input_queue.put(event)
    
    def submit_batch(self, events: List[Dict]):
        """Отправить пакет событий"""
        for event in events:
            self.input_queue.put(event)
    
    def get_results(self, timeout: float = None) -> List[Dict]:
        """Получить обработанные события"""
        results = []
        try:
            while True:
                result = self.output_queue.get_nowait()
                results.append(result)
        except queue.Empty:
            pass
        
        return results
    
    def shutdown(self):
        """Завершить работу"""
        # Отправить сигнал завершения
        for _ in range(self.num_threads):
            self.input_queue.put(None)
        
        # Ожидать завершения всех потоков
        for thread in self.threads:
            thread.stop()
            thread.join(timeout=5)
        
        self.logger.info("Параллельный обработчик завершен")


class ThreadSafeStatistics:
    """Потокобезопасная статистика"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.stats: Dict[str, Any] = {}
    
    def update(self, key: str, value: Any):
        """Обновить значение"""
        with self.lock:
            if key not in self.stats:
                self.stats[key] = value
            else:
                # Для чисел - сложить
                if isinstance(self.stats[key], (int, float)) and isinstance(value, (int, float)):
                    self.stats[key] += value
                else:
                    self.stats[key] = value
    
    def get(self, key: str, default=None) -> Any:
        """Получить значение"""
        with self.lock:
            return self.stats.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Получить все значения"""
        with self.lock:
            return self.stats.copy()
    
    def increment(self, key: str, amount: int = 1):
        """Увеличить значение"""
        with self.lock:
            if key not in self.stats:
                self.stats[key] = amount
            else:
                self.stats[key] += amount
