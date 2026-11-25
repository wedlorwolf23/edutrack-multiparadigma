from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Evaluacion:
    """Entidad inmutable que representa una evaluación ponderada (POO + base para funcional)."""
    nombre: str
    calificacion: float  # Escala 0.0 a 10.0
    peso: float          # Porcentaje 1.0 a 100.0

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValueError("El nombre de la evaluación no puede estar vacío.")
        if not (0.0 <= self.calificacion <= 10.0):
            raise ValueError("La calificación debe estar entre 0.0 y 10.0.")
        if not (0.0 < self.peso <= 100.0):
            raise ValueError("El peso porcentual debe ser mayor a 0 y menor o igual a 100.")

    def to_dict(self) -> Dict[str, object]:
        return {
            "nombre": self.nombre,
            "calificacion": self.calificacion,
            "peso": self.peso,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Evaluacion":
        return cls(
            nombre=str(data["nombre"]),
            calificacion=float(data["calificacion"]),
            peso=float(data["peso"]),
        )


@dataclass
class Materia:
    """Agrupa evaluaciones y controla la integridad de sus porcentajes."""
    nombre: str
    profesor: str = ""
    evaluaciones: List[Evaluacion] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()
        self.profesor = self.profesor.strip()
        if not self.nombre:
            raise ValueError("El nombre de la materia no puede estar vacío.")

    @property
    def peso_total(self) -> float:
        return sum(e.peso for e in self.evaluaciones)

    def agregar_evaluacion(self, evaluacion: Evaluacion) -> None:
        if self.peso_total + evaluacion.peso > 100.0 + 1e-6:
            disponible = max(0.0, 100.0 - self.peso_total)
            raise ValueError(
                f"El peso excede el 100%. Solo queda {disponible:.1f}% disponible en {self.nombre}."
            )
        self.evaluaciones.append(evaluacion)

    def eliminar_evaluacion(self, indice: int) -> None:
        if 0 <= indice < len(self.evaluaciones):
            self.evaluaciones.pop(indice)

    def to_dict(self) -> Dict[str, object]:
        return {
            "nombre": self.nombre,
            "profesor": self.profesor,
            "evaluaciones": [e.to_dict() for e in self.evaluaciones],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Materia":
        return cls(
            nombre=str(data["nombre"]),
            profesor=str(data.get("profesor", "")),
            evaluaciones=[Evaluacion.from_dict(e) for e in data.get("evaluaciones", [])],
        )


@dataclass
class Pendiente:
    """Representa una tarea, examen o sesión de tutoría con fecha límite."""
    titulo: str
    materia: str
    fecha_limite: str  # Formato YYYY-MM-DD
    importancia: int   # 1 (baja) a 5 (crítica)
    completado: bool = False

    def __post_init__(self) -> None:
        self.titulo = self.titulo.strip()
        self.materia = self.materia.strip() or "General"
        if not self.titulo:
            raise ValueError("El título del pendiente no puede estar vacío.")
        try:
            datetime.strptime(self.fecha_limite, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("La fecha límite debe tener el formato AAAA-MM-DD (ej. 2026-11-30).") from exc
        if not (1 <= int(self.importancia) <= 5):
            raise ValueError("La importancia debe estar entre 1 y 5.")
        self.importancia = int(self.importancia)

    def alternar_estado(self) -> None:
        self.completado = not self.completado

    def to_dict(self) -> Dict[str, object]:
        return {
            "titulo": self.titulo,
            "materia": self.materia,
            "fecha_limite": self.fecha_limite,
            "importancia": self.importancia,
            "completado": self.completado,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Pendiente":
        return cls(
            titulo=str(data["titulo"]),
            materia=str(data.get("materia", "General")),
            fecha_limite=str(data["fecha_limite"]),
            importancia=int(data.get("importancia", 3)),
            completado=bool(data.get("completado", False)),
        )


class GestorAcademico:
    """Contenedor principal que coordina materias y pendientes."""

    def __init__(
        self,
        materias: Optional[List[Materia]] = None,
        pendientes: Optional[List[Pendiente]] = None,
    ) -> None:
        self.materias: List[Materia] = materias or []
        self.pendientes: List[Pendiente] = pendientes or []

    def obtener_materia(self, nombre: str) -> Optional[Materia]:
        for materia in self.materias:
            if materia.nombre.lower() == nombre.strip().lower():
                return materia
        return None

    def agregar_materia(self, materia: Materia) -> None:
        if self.obtener_materia(materia.nombre) is not None:
            raise ValueError(f"Ya existe una materia llamada '{materia.nombre}'.")
        self.materias.append(materia)

    def eliminar_materia(self, nombre: str) -> None:
        self.materias = [m for m in self.materias if m.nombre.lower() != nombre.strip().lower()]

    def agregar_pendiente(self, pendiente: Pendiente) -> None:
        self.pendientes.append(pendiente)

    def eliminar_pendiente(self, pendiente: Pendiente) -> None:
        if pendiente in self.pendientes:
            self.pendientes.remove(pendiente)

    def to_dict(self) -> Dict[str, object]:
        return {
            "materias": [m.to_dict() for m in self.materias],
            "pendientes": [p.to_dict() for p in self.pendientes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "GestorAcademico":
        materias = [Materia.from_dict(m) for m in data.get("materias", [])]
        pendientes = [Pendiente.from_dict(p) for p in data.get("pendientes", [])]
        return cls(materias=materias, pendientes=pendientes)