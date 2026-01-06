"""
Validador de schemas JSON para evaluaciones de traders.

Este módulo proporciona funcionalidades para validar archivos JSON
contra schemas definidos, asegurando la integridad de los datos.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class SchemaValidator:
    """Validador de schemas JSON."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Inicializa el validador de schemas.

        Args:
            schema_path: Ruta al archivo de schema JSON (opcional)
        """
        self.schema_path = schema_path
        self.schema: Optional[Dict[str, Any]] = None
        
        if schema_path and schema_path.exists():
            self.load_schema(schema_path)

    def load_schema(self, schema_path: Path) -> None:
        """
        Carga un schema desde un archivo JSON.

        Args:
            schema_path: Ruta al archivo de schema

        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el archivo no es JSON válido
        """
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.schema_path = schema_path

    def validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Valida el tipo de un valor.

        Args:
            value: Valor a validar
            expected_type: Tipo esperado (string, number, integer, boolean, array, object)

        Returns:
            True si el tipo es correcto, False en caso contrario
        """
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }

        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return False

        return isinstance(value, expected_python_type)

    def validate_required_fields(
        self, data: Dict[str, Any], required: List[str]
    ) -> List[str]:
        """
        Valida que todos los campos requeridos estén presentes.

        Args:
            data: Diccionario de datos a validar
            required: Lista de campos requeridos

        Returns:
            Lista de campos faltantes
        """
        missing = []
        for field in required:
            if field not in data:
                missing.append(field)
        return missing

    def validate_enum(self, value: Any, enum_values: List[Any]) -> bool:
        """
        Valida que un valor esté en una lista de valores permitidos.

        Args:
            value: Valor a validar
            enum_values: Lista de valores permitidos

        Returns:
            True si el valor es válido, False en caso contrario
        """
        return value in enum_values

    def validate_range(
        self,
        value: float,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
    ) -> bool:
        """
        Valida que un valor numérico esté dentro de un rango.

        Args:
            value: Valor a validar
            minimum: Valor mínimo permitido (opcional)
            maximum: Valor máximo permitido (opcional)

        Returns:
            True si el valor está en el rango, False en caso contrario
        """
        if minimum is not None and value < minimum:
            return False
        if maximum is not None and value > maximum:
            return False
        return True

    def validate_string_format(self, value: str, format_type: str) -> bool:
        """
        Valida el formato de una cadena.

        Args:
            value: Cadena a validar
            format_type: Tipo de formato (date-time, uri, email, etc.)

        Returns:
            True si el formato es válido, False en caso contrario
        """
        if format_type == "date-time":
            try:
                from datetime import datetime
                datetime.fromisoformat(value.replace("Z", "+00:00"))
                return True
            except (ValueError, AttributeError):
                return False

        elif format_type == "uri":
            return value.startswith(("http://", "https://"))

        elif format_type == "email":
            return "@" in value and "." in value.split("@")[1]

        return True

    def validate_array(
        self,
        value: List[Any],
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> bool:
        """
        Valida las restricciones de un array.

        Args:
            value: Array a validar
            min_items: Número mínimo de elementos (opcional)
            max_items: Número máximo de elementos (opcional)

        Returns:
            True si el array es válido, False en caso contrario
        """
        if not isinstance(value, list):
            return False

        if min_items is not None and len(value) < min_items:
            return False

        if max_items is not None and len(value) > max_items:
            return False

        return True

    def get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        """
        Obtiene una lista de errores de validación para los datos proporcionados.

        Args:
            data: Datos a validar

        Returns:
            Lista de mensajes de error
        """
        errors = []

        if self.schema is None:
            errors.append("No se ha cargado ningún schema")
            return errors

        # Validar campos requeridos
        if "required" in self.schema:
            missing = self.validate_required_fields(data, self.schema["required"])
            for field in missing:
                errors.append(f"Campo requerido faltante: {field}")

        # Validar propiedades
        if "properties" in self.schema:
            for prop_name, prop_schema in self.schema["properties"].items():
                if prop_name in data:
                    value = data[prop_name]
                    
                    # Validar tipo
                    if "type" in prop_schema:
                        if not self.validate_type(value, prop_schema["type"]):
                            errors.append(
                                f"Tipo inválido para '{prop_name}': "
                                f"esperado {prop_schema['type']}"
                            )

                    # Validar enum
                    if "enum" in prop_schema:
                        if not self.validate_enum(value, prop_schema["enum"]):
                            errors.append(
                                f"Valor inválido para '{prop_name}': "
                                f"debe ser uno de {prop_schema['enum']}"
                            )

                    # Validar rango numérico
                    if isinstance(value, (int, float)):
                        if not self.validate_range(
                            value,
                            prop_schema.get("minimum"),
                            prop_schema.get("maximum"),
                        ):
                            errors.append(
                                f"Valor fuera de rango para '{prop_name}'"
                            )

                    # Validar formato de string
                    if isinstance(value, str) and "format" in prop_schema:
                        if not self.validate_string_format(
                            value, prop_schema["format"]
                        ):
                            errors.append(
                                f"Formato inválido para '{prop_name}': "
                                f"esperado {prop_schema['format']}"
                            )

        return errors

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """
        Verifica si los datos son válidos según el schema.

        Args:
            data: Datos a validar

        Returns:
            True si los datos son válidos, False en caso contrario
        """
        errors = self.get_validation_errors(data)
        return len(errors) == 0

    @staticmethod
    def validate_json_file(filepath: Path) -> bool:
        """
        Valida que un archivo sea JSON válido.

        Args:
            filepath: Ruta al archivo

        Returns:
            True si el archivo es JSON válido, False en caso contrario
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def __repr__(self) -> str:
        """Representación en string del validador."""
        schema_info = f"schema={self.schema_path}" if self.schema_path else "no schema"
        return f"SchemaValidator({schema_info})"