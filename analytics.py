from datetime import date, datetime
from functools import reduce
from typing import Dict, Iterable, List, Optional, Tuple

from models import Evaluacion, Materia, Pendiente


def calcular_peso_evaluado(evaluaciones: Iterable[Evaluacion]) -> float:
    """Suma los pesos evaluados usando reduce (función pura)."""
    return reduce(lambda acc, ev: acc + ev.peso, evaluaciones, 0.0)


def calcular_puntos_acumulados(evaluaciones: Iterable[Evaluacion]) -> float:
    """Calcula la calificación acumulada sobre la escala total (0 a 10)."""
    aportes = map(lambda ev: ev.calificacion * (ev.peso / 100.0), evaluaciones)
    return reduce(lambda acc, x: acc + x, aportes, 0.0)


def calcular_promedio_actual(evaluaciones: Iterable[Evaluacion]) -> float:
    """Promedio ponderado real considerando únicamente lo evaluado hasta ahora."""
    lista = tuple(evaluaciones)
    peso = calcular_peso_evaluado(lista)
    if peso <= 0.0:
        return 0.0
    puntos = calcular_puntos_acumulados(lista)
    return round(puntos / (peso / 100.0), 2)


def proyectar_nota_necesaria(
    evaluaciones: Iterable[Evaluacion],
    meta: float = 7.0,
) -> Dict[str, object]:
    """
    Calcula exactamente qué calificación se requiere en el porcentaje restante
    para alcanzar la meta deseada.
    """
    lista = tuple(evaluaciones)
    peso_evaluado = calcular_peso_evaluado(lista)
    peso_restante = max(0.0, round(100.0 - peso_evaluado, 2))
    puntos = round(calcular_puntos_acumulados(lista), 2)
    promedio = calcular_promedio_actual(lista)

    if peso_evaluado == 0.0:
        return {
            "peso_evaluado": 0.0,
            "peso_restante": 100.0,
            "puntos_acumulados": 0.0,
            "promedio_actual": 0.0,
            "nota_necesaria": round(meta, 2),
            "estado": "Sin evaluar",
            "nivel": "neutro",
            "mensaje": f"Aún sin calificaciones. Necesitas promediar {meta:.2f} para tu meta.",
        }

    if peso_restante <= 0.0:
        alcanzada = puntos >= meta - 1e-6
        return {
            "peso_evaluado": round(peso_evaluado, 2),
            "peso_restante": 0.0,
            "puntos_acumulados": puntos,
            "promedio_actual": promedio,
            "nota_necesaria": None,
            "estado": "Meta alcanzada" if alcanzada else "Meta no alcanzada",
            "nivel": "ok" if alcanzada else "riesgo",
            "mensaje": (
                f"Curso cerrado al 100% con {puntos:.2f}. ¡Cumpliste tu meta de {meta:.1f}!"
                if alcanzada
                else f"Curso cerrado al 100% con {puntos:.2f} (meta: {meta:.1f})."
            ),
        }

    nota_necesaria = (meta - puntos) / (peso_restante / 100.0)
    nota_redondeada = round(nota_necesaria, 2)

    if nota_necesaria <= 0.0:
        estado, nivel = "Meta asegurada", "ok"
        mensaje = (
            f"¡Ya aseguraste tu meta de {meta:.1f}! Acumulas {puntos:.2f} pts "
            f"y aún resta {peso_restante:.0f}% del curso."
        )
        nota_salida: Optional[float] = 0.0
    elif nota_necesaria > 10.0:
        estado, nivel = "Meta inalcanzable", "riesgo"
        mensaje = (
            f"Requerirías {nota_redondeada:.2f} en el {peso_restante:.0f}% restante "
            f"(máximo posible: {puntos + peso_restante / 10.0:.2f})."
        )
        nota_salida = nota_redondeada
    elif nota_necesaria >= 8.5:
        estado, nivel = "En riesgo", "alerta"
        mensaje = (
            f"Necesitas al menos {nota_redondeada:.2f} en el {peso_restante:.0f}% restante "
            f"para cerrar en {meta:.1f}."
        )
        nota_salida = nota_redondeada
    else:
        estado, nivel = "Buen camino", "ok"
        mensaje = (
            f"Necesitas {nota_redondeada:.2f} en el {peso_restante:.0f}% restante "
            f"para alcanzar {meta:.1f}."
        )
        nota_salida = nota_redondeada

    return {
        "peso_evaluado": round(peso_evaluado, 2),
        "peso_restante": peso_restante,
        "puntos_acumulados": puntos,
        "promedio_actual": promedio,
        "nota_necesaria": nota_salida,
        "estado": estado,
        "nivel": nivel,
        "mensaje": mensaje,
    }


def resumen_global(materias: Iterable[Materia], meta: float = 7.0) -> Dict[str, object]:
    """Pipeline funcional que resume el desempeño general de todas las materias."""
    proyecciones = list(map(lambda m: (m.nombre, proyectar_nota_necesaria(m.evaluaciones, meta)), materias))
    evaluadas = list(filter(lambda item: item[1]["peso_evaluado"] > 0, proyecciones))

    promedio_general = (
        round(
            reduce(lambda acc, item: acc + float(item[1]["promedio_actual"]), evaluadas, 0.0)
            / len(evaluadas),
            2,
        )
        if evaluadas
        else 0.0
    )

    en_riesgo = list(
        filter(lambda item: item[1]["nivel"] in ("riesgo", "alerta"), proyecciones)
    )

    return {
        "total_materias": len(proyecciones),
        "promedio_general": promedio_general,
        "materias_en_riesgo": len(en_riesgo),
    }


def calcular_puntaje_urgencia(pendiente: Pendiente, hoy: Optional[date] = None) -> Tuple[int, str]:
    """Asigna puntaje de prioridad y etiqueta temporal a un pendiente (función pura)."""
    referencia = hoy or date.today()
    fecha_obj = datetime.strptime(pendiente.fecha_limite, "%Y-%m-%d").date()
    dias = (fecha_obj - referencia).days

    if dias < 0:
        base = 100 + abs(dias) * 5
        etiqueta = f"Vencido ({abs(dias)}d)"
    elif dias == 0:
        base = 90
        etiqueta = "Hoy"
    elif dias == 1:
        base = 75
        etiqueta = "Mañana"
    else:
        base = max(10, 65 - dias * 4)
        etiqueta = f"En {dias} días"

    puntaje = base + pendiente.importancia * 8
    return puntaje, etiqueta


def priorizar_pendientes(
    pendientes: Iterable[Pendiente],
    incluir_completados: bool = False,
    hoy: Optional[date] = None,
) -> List[Tuple[Pendiente, int, str]]:
    """Filtra y ordena pendientes usando un pipeline funcional."""
    filtrados = (
        pendientes
        if incluir_completados
        else filter(lambda p: not p.completado, pendientes)
    )
    enriquecidos = map(
        lambda p: (p, *calcular_puntaje_urgencia(p, hoy)),
        filtrados,
    )
    return sorted(
        enriquecidos,
        key=lambda item: (item[0].completado, -item[1]),
    )