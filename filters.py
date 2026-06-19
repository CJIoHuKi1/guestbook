# filters.py
def format_date_russian(date_str):
    """Преобразует дату из формата YYYY-MM-DD в русский формат"""
    months = {
        '01': 'января', '02': 'февраля', '03': 'марта',
        '04': 'апреля', '05': 'мая', '06': 'июня',
        '07': 'июля', '08': 'августа', '09': 'сентября',
        '10': 'октября', '11': 'ноября', '12': 'декабря'
    }
    
    if not date_str:
        return ''
    
    year, month, day = date_str.split('-')
    return f"{int(day)} {months[month]} {year}"