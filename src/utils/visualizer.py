"""
Визуализация процессов симуляции
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any
from datetime import datetime


class SimulationVisualizer:
    """Визуализатор процессов симуляции"""
    
    def __init__(self, stats: Dict[str, Any]):
        """Инициализация визуализатора"""
        self.stats = stats
    
    def plot_events_distribution(self, file_path: str = None):
        """Вывести распределение событий по типам"""
        
        events_by_type = self.stats.get('events_by_type', {})
        
        if not events_by_type:
            print("Нет данных для визуализации")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        types = list(events_by_type.keys())
        counts = list(events_by_type.values())
        
        ax.bar(types, counts, color='steelblue', alpha=0.7)
        ax.set_xlabel('Тип события')
        ax.set_ylabel('Количество событий')
        ax.set_title('Распределение событий по типам')
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if file_path:
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_airport_performance(self, file_path: str = None):
        """Вывести показатели производительности аэропорта"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Всего событий
        total_events = self.stats.get('total_events_processed', 0)
        ax1.text(0.5, 0.5, str(total_events), 
                ha='center', va='center', fontsize=40, fontweight='bold')
        ax1.text(0.5, 0.2, 'Обработано событий', 
                ha='center', va='center', fontsize=12)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        ax1.set_facecolor('#f0f0f0')
        
        # События по типам (pie chart)
        events_by_type = self.stats.get('events_by_type', {})
        if events_by_type:
            types = list(events_by_type.keys())[:5]  # Топ 5
            counts = list(events_by_type.values())[:5]
            
            ax2.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Топ 5 типов событий')
        
        # Статистика
        stats_text = f"""
Время симуляции: {self.stats.get('total_events_processed', 'N/A')} сек
Всего событий: {total_events}
Задержки: {self.stats.get('total_delays', 0):.1f} мин
Самолетов: {self.stats.get('total_aircraft', 0)}
Пассажиров: {self.stats.get('total_passengers', 0)}
        """
        ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes,
                fontsize=11, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax3.axis('off')
        
        # Метрики
        ax4.text(0.5, 0.5, '📊\nСтатистика загруженная',
                ha='center', va='center', fontsize=14)
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.set_facecolor('#e8f5e9')
        
        plt.tight_layout()
        
        if file_path:
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_runway_usage(self, file_path: str = None):
        """Вывести использование ВПП"""
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Пример данных
        runways = ['RWY01', 'RWY02']
        landings = [25, 22]
        takeoffs = [24, 21]
        
        x = range(len(runways))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], landings, width, label='Посадки', color='skyblue')
        ax.bar([i + width/2 for i in x], takeoffs, width, label='Взлеты', color='lightcoral')
        
        ax.set_xlabel('ВПП')
        ax.set_ylabel('Количество операций')
        ax.set_title('Использование взлетно-посадочных полос')
        ax.set_xticks(x)
        ax.set_xticklabels(runways)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if file_path:
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_passenger_flow(self, file_path: str = None):
        """Вывести поток пассажиров"""
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Пример данных по времени
        times = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00']
        passengers = [150, 280, 420, 350, 290, 200]
        
        ax.plot(times, passengers, marker='o', linewidth=2, markersize=8, color='green')
        ax.fill_between(range(len(times)), passengers, alpha=0.3, color='green')
        
        ax.set_xlabel('Время')
        ax.set_ylabel('Количество пассажиров в терминале')
        ax.set_title('Поток пассажиров по времени')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if file_path:
            plt.savefig(file_path, dpi=150, bbox_inches='tight')
        else:
            plt.show()
    
    def export_all_plots(self, output_dir: str) -> Dict[str, bool]:
        """Экспортировать все графики"""
        
        from pathlib import Path
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        try:
            self.plot_events_distribution(
                str(output_dir / "events_distribution.png")
            )
            results['events'] = True
        except Exception as e:
            print(f"Ошибка при создании графика событий: {e}")
            results['events'] = False
        
        try:
            self.plot_airport_performance(
                str(output_dir / "airport_performance.png")
            )
            results['performance'] = True
        except Exception as e:
            print(f"Ошибка при создании графика производительности: {e}")
            results['performance'] = False
        
        try:
            self.plot_runway_usage(
                str(output_dir / "runway_usage.png")
            )
            results['runways'] = True
        except Exception as e:
            print(f"Ошибка при создании графика ВПП: {e}")
            results['runways'] = False
        
        try:
            self.plot_passenger_flow(
                str(output_dir / "passenger_flow.png")
            )
            results['passengers'] = True
        except Exception as e:
            print(f"Ошибка при создании графика пассажиров: {e}")
            results['passengers'] = False
        
        return results
