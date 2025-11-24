"""
Виджет для анализа и вывода рекомендаций по оптимизации процессов
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QScrollArea
from PyQt5.QtGui import QFont, QColor, QTextDocument, QTextCursor
from PyQt5.QtCore import Qt


class RecommendationsWidget(QWidget):
    """Виджет для отображения рекомендаций по оптимизации"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализировать интерфейс"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("💡 АНАЛИЗ И РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976D2; padding: 10px;")
        layout.addWidget(title)
        
        # Основной текст рекомендаций
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setFont(QFont("Courier", 10))
        self.recommendations_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                color: #1a1a1a;
                border: 1px solid #ddd;
                padding: 10px;
            }
        """)
        layout.addWidget(self.recommendations_text)
        
        self.setLayout(layout)
    
    def generate_recommendations(self, stats: dict):
        """Генерировать рекомендации на основе статистики"""
        recommendations = []
        
        # Анализ задержек
        total_delays = stats.get('total_delays', 0)
        if total_delays > 500:
            recommendations.append(
                "⚠️ ВЫСОКИЙ УРОВЕНЬ ЗАДЕРЖЕК\n"
                f"   • Текущие задержки: {total_delays:.0f} минут\n"
                "   • Рекомендация: Увеличить количество ВПП или оптимизировать расписание\n"
                "   • Альтернатива: Усилить работу диспетчеров для лучшего планирования\n"
            )
        elif total_delays > 200:
            recommendations.append(
                "⚡ УМЕРЕННЫЙ УРОВЕНЬ ЗАДЕРЖЕК\n"
                f"   • Текущие задержки: {total_delays:.0f} минут\n"
                "   • Рекомендация: Рассмотреть добавление дополнительных гейтов\n"
                "   • Альтернатива: Оптимизировать время обслуживания самолётов\n"
            )
        else:
            recommendations.append(
                "✓ ПРИЕМЛЕМЫЙ УРОВЕНЬ ЗАДЕРЖЕК\n"
                f"   • Текущие задержки: {total_delays:.0f} минут\n"
                "   • Статус: Система работает эффективно\n"
            )
        
        # Анализ утилизации ВПП
        runway_util = stats.get('runway_utilization', 0)
        if runway_util > 90:
            recommendations.append(
                "⚠️ ПЕРЕГРУЖЕННОСТЬ ВПП\n"
                f"   • Утилизация ВПП: {runway_util:.1f}%\n"
                "   • Проблема: ВПП работают практически на максимум\n"
                "   • Рекомендация: СРОЧНО увеличить количество ВПП\n"
                "   • Альтернатива: Перераспределить рейсы по времени\n"
            )
        elif runway_util > 70:
            recommendations.append(
                "⚡ ВЫСОКАЯ УТИЛИЗАЦИЯ ВПП\n"
                f"   • Утилизация ВПП: {runway_util:.1f}%\n"
                "   • Рекомендация: Добавить 1 ВПП для резерва\n"
                "   • Альтернатива: Оптимизировать время на взлёт/посадку\n"
            )
        else:
            recommendations.append(
                "✓ ОПТИМАЛЬНАЯ УТИЛИЗАЦИЯ ВПП\n"
                f"   • Утилизация ВПП: {runway_util:.1f}%\n"
                "   • Статус: ВПП работают эффективно\n"
            )
        
        # Анализ утилизации гейтов
        gate_util = stats.get('gate_utilization', 0)
        if gate_util > 95:
            recommendations.append(
                "⚠️ КРИТИЧЕСКАЯ УТИЛИЗАЦИЯ ГЕЙТОВ\n"
                f"   • Утилизация гейтов: {gate_util:.1f}%\n"
                "   • Проблема: Острая нехватка гейтов\n"
                "   • Рекомендация: СРОЧНО увеличить количество гейтов\n"
                "   • Альтернатива: Внедрить удалённые позиции для стоянки\n"
            )
        elif gate_util > 80:
            recommendations.append(
                "⚠️ ВЫСОКАЯ УТИЛИЗАЦИЯ ГЕЙТОВ\n"
                f"   • Утилизация гейтов: {gate_util:.1f}%\n"
                "   • Рекомендация: Добавить 2-3 гейта\n"
                "   • Альтернатива: Ускорить процесс проверки/посадки пассажиров\n"
            )
        else:
            recommendations.append(
                "✓ ОПТИМАЛЬНАЯ УТИЛИЗАЦИЯ ГЕЙТОВ\n"
                f"   • Утилизация гейтов: {gate_util:.1f}%\n"
                "   • Статус: Гейты используются эффективно\n"
            )
        
        # Анализ количества пассажиров и процесса
        total_passengers = stats.get('total_passengers', 0)
        checkin_queue = stats.get('checkin_queue_length', 0)
        security_queue = stats.get('security_queue_length', 0)
        boarding_queue = stats.get('boarding_queue_length', 0)
        
        if checkin_queue > 100:
            recommendations.append(
                "⚠️ ОЧЕРЕДЬ В CHECK-IN\n"
                f"   • Длина очереди: {checkin_queue:.0f} пассажиров\n"
                "   • Рекомендация: Добавить стойки регистрации\n"
                "   • Альтернатива: Внедрить самообслуживание (CUSS) терминалы\n"
            )
        
        if security_queue > 50:
            recommendations.append(
                "⚠️ ОЧЕРЕДЬ В ПАСПОРТНОМ КОНТРОЛЕ\n"
                f"   • Длина очереди: {security_queue:.0f} пассажиров\n"
                "   • Рекомендация: Увеличить количество агентов\n"
                "   • Альтернатива: Внедрить автоматические проверки\n"
            )
        
        if boarding_queue > 80:
            recommendations.append(
                "⚠️ ОЧЕРЕДЬ В ПОСАДКЕ\n"
                f"   • Длина очереди: {boarding_queue:.0f} пассажиров\n"
                "   • Рекомендация: Ускорить процесс посадки\n"
                "   • Альтернатива: Использовать дополнительные выходы/мосты\n"
            )
        
        # Анализ средней утилизации
        avg_util = stats.get('average_utilization', 0)
        if avg_util > 85:
            recommendations.append(
                "📊 ОБЩАЯ РЕКОМЕНДАЦИЯ: МАСШТАБИРОВАНИЕ\n"
                f"   • Средняя утилизация: {avg_util:.1f}%\n"
                "   • Вывод: Аэропорт работает близко к максимальной мощности\n"
                "   • Действия:\n"
                "     - Рассмотреть расширение инфраструктуры\n"
                "     - Внедрить систему управления перегрузками\n"
                "     - Оптимизировать интервалы между рейсами\n"
            )
        elif avg_util > 70:
            recommendations.append(
                "📊 ОБЩАЯ РЕКОМЕНДАЦИЯ: ОПТИМИЗАЦИЯ\n"
                f"   • Средняя утилизация: {avg_util:.1f}%\n"
                "   • Вывод: Нужна локальная оптимизация\n"
                "   • Действия:\n"
                "     - Пересмотреть расписание пиковых часов\n"
                "     - Балансировать нагрузку по терминалам\n"
            )
        else:
            recommendations.append(
                "✓ ОБЩАЯ РЕКОМЕНДАЦИЯ: СИСТЕМА РАБОТАЕТ ЭФФЕКТИВНО\n"
                f"   • Средняя утилизация: {avg_util:.1f}%\n"
            )
        
        # Анализ доходов и экономики
        econ_stats = stats.get('airport_economics', {})
        profit = econ_stats.get('total_profit', 0)
        roi = econ_stats.get('roi_percentage', 0)
        
        if roi < 100:
            recommendations.append(
                "💰 ЭКОНОМИЧЕСКАЯ ПРОБЛЕМА\n"
                f"   • ROI: {roi:.1f}%\n"
                f"   • Прибыль: ${profit:.0f}\n"
                "   • Рекомендация: Пересмотреть тарифы и операционные расходы\n"
            )
        elif roi > 400:
            recommendations.append(
                "💰 ОТЛИЧНАЯ РЕНТАБЕЛЬНОСТЬ\n"
                f"   • ROI: {roi:.1f}%\n"
                f"   • Прибыль: ${profit:.0f}\n"
                "   • Статус: Экономически успешный сценарий\n"
            )
        else:
            recommendations.append(
                "💰 ЗДОРОВАЯ РЕНТАБЕЛЬНОСТЬ\n"
                f"   • ROI: {roi:.1f}%\n"
                f"   • Прибыль: ${profit:.0f}\n"
                "   • Статус: Нормальные экономические показатели\n"
            )
        
        # Сформировать итоговый текст
        recommendations_text = "═" * 70 + "\n\n"
        recommendations_text += "ИТОГОВЫЙ АНАЛИЗ СИМУЛЯЦИИ\n"
        recommendations_text += "═" * 70 + "\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            recommendations_text += rec + "\n"
        
        recommendations_text += "\n" + "═" * 70 + "\n"
        recommendations_text += "ПРИОРИТЕТ ДЕЙСТВИЙ:\n"
        recommendations_text += "1️⃣  Критические проблемы (отмечены ⚠️ ВЫСОКИЙ/КРИТИЧЕСКИЙ)\n"
        recommendations_text += "2️⃣  Важные проблемы (отмечены ⚡)\n"
        recommendations_text += "3️⃣  Долгосрочные улучшения (📊 ОБЩАЯ РЕКОМЕНДАЦИЯ)\n"
        recommendations_text += "═" * 70 + "\n"
        
        # Вывести результаты
        self.recommendations_text.setText(recommendations_text)
