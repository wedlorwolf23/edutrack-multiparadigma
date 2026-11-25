# EduTrack — Gestor de Progreso Académico y Prioridades

Aplicación de escritorio desarrollada en **Python** para el proyecto final de **Programación Multiparadigma**, enfocada en resolver un problema cotidiano de estudiantes y tutores: calcular con precisión qué calificación se necesita en las evaluaciones restantes para alcanzar una meta académica y priorizar tareas o sesiones según urgencia real.

## Problema real que resuelve

Al llevar múltiples materias con criterios de evaluación ponderados y fechas límite simultáneas, es común perder noción del promedio real o subestimar qué calificación exige el examen final. **EduTrack** centraliza:

- Registro de materias y evaluaciones con control de pesos porcentuales (validando que no excedan el 100%).
- **Calculadora automática de meta:** indica la calificación exacta requerida en el porcentaje restante y alerta cuando una materia está en riesgo o ya aseguró su meta.
- **Agenda con prioridad inteligente:** ordena tareas, exámenes y sesiones de tutoría combinando días restantes e importancia.
- Guardado automático en JSON y exportación de reportes a CSV listos para Excel.

## Enfoque Multiparadigma

La arquitectura separa explícitamente cuatro paradigmas de programación:

| Paradigma | Módulo | Aplicación en el código |
| :--- | :--- | :--- |
| **Orientado a Objetos (POO)** | `models.py` | Modelado de entidades (`Evaluacion`, `Materia`, `Pendiente`, `GestorAcademico`), encapsulación de validaciones, composición y serialización. |
| **Funcional** | `analytics.py` | Funciones puras e inmutabilidad; uso de `map`, `filter`, `reduce` y `sorted` con expresiones `lambda` para cálculos ponderados, proyecciones y *ranking* de urgencia. |
| **Imperativo / Procedural** | `storage.py` | Rutinas secuenciales de entrada/salida para persistencia en `JSON` y generación de reportes `CSV`. |
| **Orientado a Eventos** | `app.py` | Interfaz gráfica en `Tkinter` guiada por *callbacks*, selección de tablas (`<<TreeviewSelect>>`) y actualización reactiva de indicadores. |

## Requisitos y ejecución

No requiere instalar paquetes externos (utiliza únicamente la biblioteca estándar de **Python 3.10+**).

```bash
git clone [https://github.com/wedlorwolf23/edutrack-multiparadigma.git](https://github.com/wedlorwolf23/edutrack-multiparadigma.git)
cd edutrack-multiparadigma
python main.py