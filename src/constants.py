from schema import (
    ActaReunion,
    Acuerdo,
    AsistenteCargo,
    Proposicion,
)

ASISTENTE_CARGO = AsistenteCargo(nombre="", cargo="")
PROPOSICION = Proposicion(descripcion="No hay proposiciones", aprobada=True)
ACUERDO = Acuerdo(descripcion="", fecha_cumplimiento="", responsable="")
TIPO_SESION = "Ordinaria"
ACTA_DEFAULT = ActaReunion(
    lugar=None,
    fecha=None,
    hora=None,
    tipo_sesion=TIPO_SESION,
    asistencia_cargo=[ASISTENTE_CARGO],
    orden_del_dia=["", ""],
    desarrollo_temas=["", ""],
    proposiciones=[PROPOSICION],
    acuerdos_adoptados=[ACUERDO],
    hora_finalizacion=None,
)

PROMPT = """
<prompt>
  <rol>
    Eres un asistente experto en análisis de transcripciones de reuniones y generación de actas estructuradas en formato JSON.
  </rol>
  <objetivo>
    A partir de una transcripción informal y desordenada de una reunión, tu tarea es extraer únicamente la información explícitamente mencionada y organizarla en una estructura JSON predefinida.
  </objetivo>
  <restricciones>
    <item>No agregues información que no esté en la transcripción.</item>
    <item>No respondas preguntas, ni generes contenido nuevo o inferido.</item>
    <item>No hagas deducciones implícitas, ni completes con lógica externa.</item>
    <item>Evita cualquier símbolo que no sea punto (.) o coma (,).</item>
    <item>Si un dato no está presente en la transcripción, déjalo como campo vacío.</item>
  </restricciones>
  <formato_salida>
    El JSON debe contener los siguientes campos:
    {{\n
        "lugar": "<Lugar donde se realizó la reunión, si se menciona>",\n
        "fecha": "<Fecha de la reunión, si se menciona>",\n
        "hora": "<Hora de inicio, si se menciona>",\n
        "tipo_sesion": "<Tipo de sesión, 'Ordinaria' o 'Extraordinaria' exclusivamente, si se menciona>",\n
        "orden_del_dia": "<Lista de temas que se mencionaron explícitamente como parte del orden del día. No incluir temas discutidos que no estén en la agenda>",\n
        "asistencia_cargo": "<Lista de personas que asistieron y su cargo. Excluir personas que se mencione que no asistieron>",\n
        "desarrollo_temas": "<Lista de temas discutidos durante la reunión con una breve síntesis por tema>",\n
        "proposiciones": "<Lista de propuestas realizadas, indicando si fueron aprobadas (true) o rechazadas (false)>",\n
        "acuerdos_adoptados": "<Lista de acciones o decisiones con un responsable y fecha límite (si está presente). La descripción debe contener solo la acción concreta.>",\n
        "hora_finalizacion": "<Hora en que terminó la reunión, si se menciona>",\n
    }}
  </formato_salida>
  <transcripcion>
    {transcription}
  </transcripcion>
</prompt>
"""
