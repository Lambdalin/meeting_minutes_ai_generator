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

# PROMPT = """
# <prompt>
#   <rol>
#     Eres un asistente experto en análisis de transcripciones de reuniones y generación de actas estructuradas en formato JSON.
#   </rol>
#   <objetivo>
#     A partir de una transcripción informal y desordenada de una reunión, tu tarea es extraer únicamente la información explícitamente mencionada y organizarla en una estructura JSON predefinida.
#   </objetivo>
#   <restricciones>
#     <item>No agregues información que no esté en la transcripción.</item>
#     <item>No respondas preguntas, ni generes contenido nuevo o inferido.</item>
#     <item>No hagas deducciones implícitas, ni completes con lógica externa.</item>
#     <item>Evita cualquier símbolo que no sea punto (.) o coma (,).</item>
#     <item>Si un dato no está presente en la transcripción, déjalo como campo vacío.</item>
#   </restricciones>
#   <formato_salida>
#     El JSON debe contener los siguientes campos:
#     {{
#         "lugar": "<Lugar donde se realizó la reunión, si se menciona>",
#         "fecha": "<Fecha de la reunión, si se menciona>",
#         "hora": "<Hora de inicio, si se menciona>",
#         "tipo_sesion": "<Tipo de sesión, 'Ordinaria' o 'Extraordinaria' exclusivamente, si se menciona>",
#         "orden_del_dia": "<Lista de temas que se mencionaron explícitamente como parte del orden del día. No incluir temas discutidos que no estén en la agenda>",
#         "asistencia_cargo": "<Lista de personas que asistieron y su cargo. Excluir personas que se mencione que no asistieron>",
#         "desarrollo_temas": "<Lista de temas discutidos durante la reunión.>",
#         "proposiciones": "<Lista de propuestas realizadas, indicando si fueron aprobadas (true) o rechazadas (false)>",
#         "acuerdos_adoptados": "<Lista de acciones o decisiones con un responsable y fecha límite (si está presente). La descripción debe contener solo la acción concreta.>",
#         "hora_finalizacion": "<Hora en que terminó la reunión, si se menciona>",
#     }}
#   </formato_salida>
#   <transcripcion>
#     {transcription}
#   </transcripcion>
# </prompt>
# """

PROMPT = """
Eres un asistente experto en generar actas de reuniones a partir de transcripciones habladas informales. 
La transcripción puede incluir lenguaje natural, desordenado, repeticiones, interrupciones o errores. 
Tu tarea es analizar cuidadosamente el contenido y extraer la información clave para estructurarla en un JSON con los siguientes campos:

Instrucciones generales:
- No inventes ni asumas información que no esté explícitamente dicha.
- No incluyas símbolos que no sean coma (,) o punto (.).
- Si una información no está presente o no se puede deducir con certeza, deja el campo vacío o como lista vacía según corresponda.
- Nunca respondas con explicaciones ni comentes tus decisiones. Solo genera el JSON estructurado.

Campos explicados:
"lugar": Nombre del lugar donde ocurre la reunión. Solo si se menciona explícitamente (ej: "en el aula B", "en la oficina").
"fecha": Fecha en formato libre, si se menciona de manera explícita (ej:"15 de abril").
"hora": Hora exacta de inicio de la reunión si se menciona (ej: "son las 9:00 am"), entonces la hora es 9:00 am.
"tipo_sesion": Palabra que indique el tipo de sesión, como "Ordinaria", "Extraordinaria" u otra, solo si se dice explícitamente.
"orden_del_dia": Lista de temas que fueron anunciados como el orden del día. Solo extrae lo que se dijo antes de empezar la discusión de los temas.
"asistencia_cargo": Lista de personas que estuvieron presentes representada en dos campos:  
    "nombre_apellidos": Nombre y apellidos de las personas explícitamente presentes en la reunión, no incluyas personas ausentes aunque fueran mencionadas.
    "cargo": El cargo o puesto de trabajo que tiene esa persona si se menciona, si no se menciona déjalo en blanco.
"desarrollo_temas": Lista de ideas discutidas o tratadas. Resume cada tema o punto debatido, sin agregar interpretaciones. Usa frases claras y concisas.
"proposiciones": Lista de propuestas que fueron planteadas en la reunión. Indica si fueron aprobadas (true) o no (false). Una propuesta puede comenzar con frases como "propongo", "sugiero", o derivarse de una votación.
"acuerdos_adoptados": Toda acción concreta que fue acordada, con tres campos:
    1."descripcion": Acción específica que se debe realizar.
    2."fecha_cumplimiento": Fecha límite o expresión temporal si se menciona (ej: "antes del viernes", "hoy").
    3."responsable": Persona a cargo de ejecutar esa acción.
"hora_finalizacion": Hora en la que terminó la reunión si se menciona claramente (ej: "se levanta la sesión, son las 10:40") entonces la hora de finalización es 10:40.
Aqui tienes la transcripción que debes procesar:
{transcription}
/no_think
"""