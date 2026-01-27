#!/usr/bin/env python3
"""
Скрипт для загрузки данных рынка из JSON файла
"""
import sys
import os
import json

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.database import SessionLocal
from app.db.models import MarketReport, MarketReportValue, PropertyClass

def load_market_data(json_file_path: str):
    """Загрузка данных рынка из JSON файла"""
    db = SessionLocal()
    
    try:
        # Читаем JSON файл
        with open(json_file_path, 'r', encoding='utf-8') as f:
            reports_data = json.load(f)
        
        print(f"Найдено отчётов: {len(reports_data)}")
        
        for report_data in reports_data:
            # Создаём или получаем отчёт
            existing_report = db.query(MarketReport).filter(
                MarketReport.provider == report_data['provider'],
                MarketReport.period == report_data['period']
            ).first()
            
            if existing_report:
                print(f"Отчёт {report_data['provider']} {report_data['period']} уже существует, пропускаем...")
                report = existing_report
            else:
                report = MarketReport(
                    provider=report_data['provider'],
                    title=report_data['title'],
                    period=report_data['period'],
                    file_url=report_data.get('file_url'),
                    active=report_data.get('active', True)
                )
                db.add(report)
                db.commit()
                db.refresh(report)
                print(f"✓ Создан отчёт: {report.provider} {report.period} (ID: {report.id})")
            
            # Загружаем значения отчёта
            values_count = 0
            for value_data in report_data.get('values', []):
                # Проверяем, существует ли уже такое значение
                existing_value = db.query(MarketReportValue).filter(
                    MarketReportValue.report_id == report.id,
                    MarketReportValue.location_group_id == value_data['location_group_id'],
                    MarketReportValue.property_class == PropertyClass(value_data['property_class'])
                ).first()
                
                if existing_value:
                    # Обновляем существующее значение
                    existing_value.rent_start = value_data['rent_start']
                    existing_value.rent_growth_annual = value_data['rent_growth_annual']
                    existing_value.price_per_m2_start = value_data.get('price_per_m2_start')
                    existing_value.price_growth_annual = value_data['price_growth_annual']
                    existing_value.vacancy_rate = value_data.get('vacancy_rate')
                    print(f"  ↻ Обновлено значение: {value_data['location_group_id']} - {value_data['property_class']}")
                else:
                    # Создаём новое значение
                    value = MarketReportValue(
                        report_id=report.id,
                        location_group_id=value_data['location_group_id'],
                        property_class=PropertyClass(value_data['property_class']),
                        rent_start=value_data['rent_start'],
                        rent_growth_annual=value_data['rent_growth_annual'],
                        price_per_m2_start=value_data.get('price_per_m2_start'),
                        price_growth_annual=value_data['price_growth_annual'],
                        vacancy_rate=value_data.get('vacancy_rate')
                    )
                    db.add(value)
                    values_count += 1
                    print(f"  ✓ Добавлено значение: {value_data['location_group_id']} - {value_data['property_class']}")
            
            if values_count > 0:
                db.commit()
                print(f"  ✓ Загружено значений: {values_count}")
        
        print("\n✓ Загрузка данных завершена успешно!")
        
    except FileNotFoundError:
        print(f"✗ Файл не найден: {json_file_path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"✗ Ошибка парсинга JSON: {e}")
        return 1
    except Exception as e:
        print(f"✗ Ошибка при загрузке данных: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    # Путь к JSON файлу относительно корня проекта
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    json_file = os.path.join(project_root, "market_data_Q4_2025.json")
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"✗ Файл не найден: {json_file}")
        print(f"Использование: python {sys.argv[0]} [путь_к_json_файлу]")
        sys.exit(1)
    
    exit_code = load_market_data(json_file)
    sys.exit(exit_code)
