from datetime import datetime

def format_timestamp(timestamp):
    """Convierte un timestamp UNIX a un formato de fecha legible"""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M')
    return "Fecha desconocida"
