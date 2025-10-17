from .parto import bp as partos_bp
from .mortalidad_general import bp as mortalidad_bp
from .dashboard import bp as dashboard_bp

# Para los módulos que aún no tienes, comenta temporalmente
# from .destetes import bp as destetes_bp
# from .galpones import bp as galpones_bp  
# from .gastos import bp as gastos_bp
# from .ventas import bp as ventas_bp
# from .inventario import bp as inventario_bp
# from .balance import bp as balance_bp
# from .predicciones import bp as predicciones_bp

__all__ = [
    'partos_bp',
    'mortalidad_bp',
    'dashboard_bp',
    # 'destetes_bp',
    # 'galpones_bp',
    # 'gastos_bp', 
    # 'ventas_bp',
    # 'inventario_bp',
    # 'balance_bp',
    # 'predicciones_bp'
]