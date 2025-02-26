import pandas as pd
import numpy as np
from settings.yandex_direct import HIGH_BOUNCE_RATE_THRESHOLD

COST_WARNING_THRESHOLD = 2500

def _group_data(df: pd.DataFrame, group_by: str) -> pd.DataFrame:
    agg_dict = {
        'Impressions': 'sum',
        'Clicks': 'sum', 
        'Cost': 'sum',
        'Conversions': 'sum',
        'Sessions': 'sum',
        'Bounces': 'sum'
    }
    return df.groupby(group_by).agg(agg_dict).reset_index()

def _calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df['CTR'] = np.where(df['Impressions'] > 0, (df['Clicks'] / df['Impressions'] * 100).round(2), 0)
    df['CPC'] = np.where(df['Clicks'] > 0, (df['Cost'] / df['Clicks']).round(2), 0)
    df['CR']  = np.where(df['Clicks'] > 0, (df['Conversions'] / df['Clicks'] * 100).round(2), 0)
    df['CPA'] = np.where(df['Conversions'] > 0, (df['Cost'] / df['Conversions']).round(2), 0)
    df['BounceRate'] = np.where(df['Sessions'] > 0, (df['Bounces'] / df['Sessions'] * 100).round(2), 0)
    return df

def _rename_columns_to_russian(df: pd.DataFrame) -> pd.DataFrame:
    russian_names = {
        'Impressions': 'Показы',
        'Clicks': 'Клики',
        'Cost': 'Расход',
        'Conversions': 'Конверсии',
        'Sessions': 'Сессии',
        'Bounces': 'Отказы',
        'BounceRate': 'Процент отказов',
        'CampaignName': 'Название кампании',
        'Age': 'Возраст',
        'Gender': 'Пол',
        'Device': 'Устройство',
        'Date': 'Дата'
    }
    return df.rename(columns=russian_names)

def _add_conditional_formatting(df: pd.DataFrame) -> pd.DataFrame:
    """Добавляет условное форматирование для строк с высоким расходом без конверсий и высоким процентом отказов"""
    # Форматирование для высокого расхода без конверсий
    mask = (df['Cost'] > COST_WARNING_THRESHOLD) & (df['Conversions'] == 0)
    df['Cost'] = df['Cost'].astype(str)
    df.loc[mask, 'Cost'] = df.loc[mask, 'Cost'].apply(lambda x: f'{x} ⚠️')
    
    # Форматирование для высокого процента отказов
    bounce_mask = df['BounceRate'] > HIGH_BOUNCE_RATE_THRESHOLD
    df['BounceRate'] = df['BounceRate'].astype(str)
    df.loc[bounce_mask, 'BounceRate'] = df.loc[bounce_mask, 'BounceRate'].apply(lambda x: f'{x} 🔴')
    
    return df

def proccess_data(data: list[dict], group_by: str = None) -> list[dict]:
    """
    Добавляет в DataFrame новые столбцы с вычислением производных метрик.
    Рассчитывает CTR, CPC, CR и CPA для каждой строки.
    Переименовывает поля на русский язык.
    Добавляет условное форматирование для проблемных показателей.
    
    Args:
        data: Список словарей с данными
        group_by: Поле для группировки. Если None - группировка не выполняется
    """
    df = pd.DataFrame(data)
    
    if group_by and group_by in df.columns:
        df = _group_data(df, group_by)
        
    df = _calculate_metrics(df)
    df = _add_conditional_formatting(df)
    df = _rename_columns_to_russian(df)
    return df.to_dict('records')