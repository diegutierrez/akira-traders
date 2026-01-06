"""
Módulo de utilidades para el sistema de evaluación de traders.

Este paquete contiene utilidades compartidas para validación, cálculo de métricas,
generación de reportes y otras funcionalidades comunes.
"""

__version__ = "1.0.0"
__author__ = "Akira Traders"

from .schema_validator import SchemaValidator
from .metrics_calculator import MetricsCalculator

__all__ = [
    "SchemaValidator",
    "MetricsCalculator",
]