"""
Экспорт результатов симуляции в различные форматы
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ResultsExporter:
    """Экспортер результатов симуляции"""
    
    def __init__(self, stats: Dict[str, Any]):
        """
        Инициализация экспортера
        
        Args:
            stats: Словарь со статистикой
        """
        self.stats = stats
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_json(self, file_path: str) -> bool:
        """
        Экспортировать в JSON
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если успешно
        """
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "statistics": self.stats,
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Ошибка при экспорте JSON: {e}")
            return False
    
    def export_csv(self, file_path: str) -> bool:
        """
        Экспортировать в CSV
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если успешно
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Заголовки
                writer.writerow(['Показатель', 'Значение'])
                
                # Данные
                for key, value in self.stats.items():
                    if isinstance(value, dict):
                        # Развернуть вложенные словари
                        for sub_key, sub_value in value.items():
                            writer.writerow([f"{key}.{sub_key}", sub_value])
                    else:
                        writer.writerow([key, value])
            
            return True
        except Exception as e:
            print(f"Ошибка при экспорте CSV: {e}")
            return False
    
    def export_pdf(self, file_path: str) -> bool:
        """
        Экспортировать в PDF
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если успешно
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Заголовок
            title = Paragraph("<b>Отчет о симуляции AeroSim EDU</b>", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.3 * inch))
            
            # Информация
            info = Paragraph(f"<b>Дата/время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            story.append(info)
            story.append(Spacer(1, 0.2 * inch))
            
            # Таблица со статистикой
            data = [['Показатель', 'Значение']]
            for key, value in self.stats.items():
                if not isinstance(value, dict):
                    data.append([str(key), str(value)])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            doc.build(story)
            
            return True
        except ImportError:
            print("Для экспорта PDF требуется reportlab: pip install reportlab")
            return False
        except Exception as e:
            print(f"Ошибка при экспорте PDF: {e}")
            return False
    
    def export_all(self, output_dir: str) -> Dict[str, bool]:
        """
        Экспортировать во все форматы
        
        Args:
            output_dir: Директория для выходных файлов
            
        Returns:
            Словарь с результатами по форматам
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'json': self.export_json(str(output_dir / f"results_{self.timestamp}.json")),
            'csv': self.export_csv(str(output_dir / f"results_{self.timestamp}.csv")),
            'pdf': self.export_pdf(str(output_dir / f"results_{self.timestamp}.pdf")),
        }
        
        return results
