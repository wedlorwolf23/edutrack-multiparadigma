import csv
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Union

from analytics import proyectar_nota_necesaria
from models import Evaluacion, GestorAcademico, Materia, Pendiente

RUTA_DATOS_DEFAULT = Path(__file__).resolve().parent / "datos_academicos.json"


def guardar_datos(gestor: GestorAcademico, ruta: Union[Path, str] = RUTA_DATOS_DEFAULT) -> None:
    """Guarda el estado completo del gestor en un archivo JSON."""
    destino = Path(ruta)
    with destino.open("w", encoding="utf-8") as archivo:
        json.dump(gestor.to_dict(), archivo, ensure_ascii=False, indent=2)


def cargar_datos(ruta: Union[Path, str] = RUTA_DATOS_DEFAULT) -> GestorAcademico:
    """Carga el gestor desde JSON; si no existe o falla, devuelve uno vacío."""
    origen = Path(ruta)
    if not origen.exists():
        return GestorAcademico()
    try:
        with origen.open("r", encoding="utf-8") as archivo:
            contenido = json.load(archivo)
        return GestorAcademico.from_dict(contenido)
    except (OSError, json.JSONDecodeError, ValueError, KeyError):
        return GestorAcademico()


def exportar_reporte_csv(
    gestor: GestorAcademico,
    meta: float,
    ruta_csv: Union[Path, str],
) -> None:
    """Exporta un resumen estructurado de materias y metas a CSV (UTF-8 con BOM para Excel)."""
    destino = Path(ruta_csv)
    with destino.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            "Materia",
            "Profesor / Grupo",
            "Evaluado (%)",
            "Promedio Actual",
            "Puntos Acumulados",
            f"Necesario para {meta:.1f}",
            "Estado",
        ])
        for materia in gestor.materias:
            proy = proyectar_nota_necesaria(materia.evaluaciones, meta)
            nota_nec = proy["nota_necesaria"]
            nota_texto = "-" if nota_nec is None else f"{nota_nec:.2f}"
            escritor.writerow([
                materia.nombre,
                materia.profesor or "-",
                f"{proy['peso_evaluado']:.1f}%",
                f"{proy['promedio_actual']:.2f}",
                f"{proy['puntos_acumulados']:.2f}",
                nota_texto,
                proy["estado"],
            ])


def crear_datos_ejemplo() -> GestorAcademico:
    """Genera un conjunto realista de materias y tareas para demostración inmediata."""
    hoy = date.today()
    materias = [
        Materia(
            nombre="Programación Multiparadigma",
            profesor="Proyecto Final",
            evaluaciones=[
                Evaluacion("Parcial 1", 9.0, 25),
                Evaluacion("Parcial 2", 8.5, 25),
                Evaluacion("Prácticas", 9.5, 20),
            ],
        ),
        Materia(
            nombre="Microcontroladores y Sensores",
            profesor="Laboratorio",
            evaluaciones=[
                Evaluacion("Parcial 1", 7.2, 30),
                Evaluacion("Práctica ESP32", 8.8, 30),
            ],
        ),
        Materia(
            nombre="Control Analógico",
            profesor="Teoría",
            evaluaciones=[
                Evaluacion("Parcial 1", 5.8, 35),
                Evaluacion("Parcial 2", 6.4, 35),
            ],
        ),
    ]
    pendientes = [
        Pendiente(
            titulo="Subir repositorio y portafolio a GitHub",
            materia="Programación Multiparadigma",
            fecha_limite=(hoy + timedelta(days=1)).strftime("%Y-%m-%d"),
            importancia=5,
        ),
        Pendiente(
            titulo="Repasar diagramas de Bode para examen final",
            materia="Control Analógico",
            fecha_limite=(hoy + timedelta(days=3)).strftime("%Y-%m-%d"),
            importancia=5,
        ),
        Pendiente(
            titulo="Preparar ejercicios de factorización (tutoría)",
            materia="Tutorías Matemáticas",
            fecha_limite=(hoy + timedelta(days=5)).strftime("%Y-%m-%d"),
            importancia=3,
        ),
    ]
    return GestorAcademico(materias=materias, pendientes=pendientes)