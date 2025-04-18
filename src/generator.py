# import typing as t
from openai import OpenAI
from jsonvalidator import schema
from settings import settings
from vllm import LLM, SamplingParams
from vllm.sampling_params import GuidedDecodingParams


system_prompt = '''
Eres un experto encargado de generar un acta de reunión en formato JSON estructurado a partir de una transcripción de audio desordenada o informal. El texto puede incluir interrupciones, repeticiones, errores de lenguaje y contenido hablado de manera natural. Tu trabajo es identificar y extraer correctamente la información clave de la reunión, siguiendo esta estructura:

- "lugar": Lugar donde se realizó la reunión si se menciona. Si no se menciona, dejar vacío.
- "fecha": Fecha de la reunión si se menciona. Si no se menciona, dejar vacío.
- "hora": Hora de inicio de la reunión si se menciona.
- "tipo_sesion": Puede ser "Ordinaria", "Extraordinaria" u otro tipo si se menciona explícitamente.
- "orden_del_dia": Lista de temas principales de la reunión. Solo incluye lo que se dijo que sería la orden del día, no todo lo que se discutió.
- "asistencia_cargo": Lista de personas presentes con su cargo. Excluye a personas que se dijo explícitamente que no asistieron.
- "desarrollo_temas": Lista de temas discutidos con una pequeña síntesis para cada uno.
- "proposiciones": Todas las propuestas realizadas, indicando si fueron aprobadas o no. Generalmente se dice que se aprueban o se vota sobre ellas.
- "acuerdos_adoptados": Toda acción o decisión que tenga un responsable y una fecha límite, o que se aprobó como obligación. El campo `descripcion` debe contener solo la **tarea concreta o acción a realizar**, no el nombre del responsable. El responsable debe ir únicamente en el campo `responsable`.
- "hora_finalizacion": Hora en la que terminó la reunión si se menciona.


Ejemplo de entrada:
"""
Bueno, bueno... ya estamos en el aula inteligente, son las 9:15, empecemos, hoy toca sesión Ordinaria. Director ejecutivo Oscar Lucero Moya, Secretaria del director Lucia Gomez Vidal, Directora de operaciones Ana Maria Sanchez Mora, director de redes Roberto Martinez Sanchez, no Roberto no vino, mandó un correo, está con el tema del servidor caído. La orden del día de hoy es las ventas del trimestre. Comencemos hablando del acta anterior, fue aprobada, pero hay que cambiar la fecha, dice 2023 hay que poner 2024, bien, Ana, te corresponde cambiarle la fecha al acta, esta bien. Que pasa con las ventas del trimestre. Aquí tengo los números...  Mmm... 12% abajo. Nos dejaron colgados otra vez con los envíos. ¿propuestas para eso? Multarlos. Punto. Apoyo, pero que sea un porcentaje fijo. Yo propongo que dialoguemos con ellos, algún problema tuvieron que tener, ya hemos dialogado demasiado con ellos y es la cuarta vez que ocurre dialogar de nuevo es una perdida de tiempo, estoy de acuerdo, entonces votamos por aplicarles una multa? Todos a favor... Bien, aprobado, Maria redactara el documento de petición para sancionar a los multados, debes terminarlo antes de pasado mañana. Hacemos teletrabajo el viernes?, yo digo que sí, no podemos hacer teletrabajo esta semana tenemos que asistir a la oficina para reunirnos nuevamente, no se hará teletrabajo el viernes.  Prepara una propuesta para mayo. ¿Algo más? Sí, que arreglen el aire acondicionado, aquí parece el Sahara, Oscar avísale hoy al equipo técnico por favor. Se levanta la sesión, 10:40.
"""

Salida esperada:

{
    "lugar": "aula inteligente",
    "fecha": "",
    "hora": "9:15",
    "tipo_sesion": "Ordinaria",
    "asistencia_cargo": [
    {
        "nombre_apellidos": "Oscar Lucero Moya",
        "cargo": "Director ejecutivo"
    },
    {
        "nombre_apellidos": "Lucia Gomez Vidal",
        "cargo": "Secretaria del director"
    },
    {
        "nombre_apellidos": "Ana Maria Sanchez Mora",
        "cargo": "Directora de operaciones"
    }
    ],
    "orden_del_dia": [
        "las ventas del trimestre"
    ],
    "desarrollo_temas": [
        "Se aprobó el acta anterior con la observación de corregir la fecha del año de 2023 a 2024.",
        "Se analizaron los resultados de ventas, que presentaron una disminución del 12%, y se debatió sobre los problemas de envío.",
        "Se propuso hacer teletrabajo el viernes, pero se decidió que no sería posible por la necesidad de reunirse presencialmente.",
        "Se solicitó solucionar el problema del aire acondicionado debido a condiciones incómodas en el aula."
    ],
    "proposiciones": [
    {
        "descripcion": "Aplicar una multa a los responsables de los retrasos en los envíos",
        "aprobada": true
    },
    {
        "descripcion": "Dialogar con los responsables de los envíos",
        "aprobada": false
    },
    {
        "descripcion": "Hacer teletrabajo el viernes",
        "aprobada": false
    }
    ],
    "acuerdos_adoptados": [
    {
        "descripcion": "corregir la fecha del acta anterior",
        "fecha_cumplimiento": "",
        "responsable": "Ana Maria Sanchez Mora"
    },
    {
        "descripcion": "redactar el documento de sanción",
        "fecha_cumplimiento": "pasado mañana",
        "responsable": "Maria"
    },
    {
        "descripcion": "avisar al equipo técnico sobre la rotura del aire acondicionado",
        "fecha_cumplimiento": "hoy",
        "responsable": "Oscar Lucero Moya"
    }
    ],
    "hora_finalizacion": "10:40"
}

'''
def get_client():
    match settings.ENVIRONMENT:
        case "dev":
            model = OpenAI(api_key="API", base_url=settings.CLIENT_URL)
        case "prod":
            model = LLM(
                model=settings.LLM_MODEL,
                dtype=settings.DTYPE,
                task="generate",
                seed=42,
                enforce_eager=False,
                max_model_len=settings.CTX_WINDOW,
                max_num_seqs=2,
                enable_chunked_prefill=True,
                gpu_memory_utilization=0.5
            )
        case _:
            raise ValueError("env should be dev | prod")
    return model


def generate(prompt: str, llm, model_params: dict = {}) -> str:
    assert prompt, "A prompt must be provided!"
    assert len(prompt) // 4 < settings.CTX_WINDOW, "Prompt too large!!"

    match settings.ENVIRONMENT:
        case "prod":
            assert isinstance(llm, LLM), "LLM should be an instance of LLM class"
            guided_decoding_params = GuidedDecodingParams(json=schema)
            sampling_params = SamplingParams(
                max_tokens=model_params.get("max_tokens", 2048),
                temperature=model_params.get("temperature", 0),
                top_p=model_params.get("top_p", 0.95),
                frequency_penalty=model_params.get("frequency_penalty", 0.5),
                presence_penalty=model_params.get("presence_penalty", 1.2),
                repetition_penalty=model_params.get("repetition_penalty", 1.2),
                guided_decoding=guided_decoding_params
            )
            outputs = llm.generate(prompt, sampling_params)
            return outputs[0].outputs[0].text
        case "dev":
            assert isinstance(llm, OpenAI), "LLM should be and instance of OpenAI class"
            params = {
                "max_tokens": model_params.get("max_t okens", 2048),
                "temperature": model_params.get("temperature", 0),
                "top_p": model_params.get("top_p", 0.95),
                "frequency_penalty": model_params.get("frequency_penalty", 0.5),
                "presence_penalty": model_params.get("presence_penalty", 1.2),
            }
            response = llm.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"{system_prompt}",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}",
                    },
                ],
                extra_body={"guided_json": schema},
                **params,
            )
            return response.choices[0].message.content
        case _:
            raise ValueError("Correctly configure the env to be dev | prod")






text = "Buenos días, son las 9:03, estamos ya todos aquí en el aula de reuniones. Vamos a comenzar la sesión ordinaria de hoy. A ver, voy pasando lista rápido: Oscar Lucero Moya, director ejecutivo, presente; Lucía Gómez Vidal, secretaria del director, presente; Ana María Sánchez Mora, directora de operaciones, sí, aquí; Roberto Martínez Sánchez ausente, dejó un mensaje diciendo que sigue con problemas de conexión en casa. María Torres y Pedro López ambos presentes. La orden del día de hoy es revisión del presupuesto para el segundo trimestre y planificación del evento de innovación tecnológica. Empecemos con el presupuesto. Ana, tienes los números. Sí, bueno, lo que vemos es que hay un desvío de casi el 15% en los gastos operativos, principalmente por el aumento del precio de materiales y servicios logísticos. Pedro, ¿cómo ves eso? No podemos seguir así, tenemos que renegociar los contratos o buscar nuevos proveedores. Lucía propone hacer una revisión de todos los contratos activos antes del 20 de este mes. ¿Están de acuerdo? Todos a favor. Aprobado. Sobre el evento de innovación tecnológica, será el 15 de mayo. María propuso hacerlo en el salón principal del edificio central. Oscar cree que es mejor en el aula magna, pero al final se acuerda mantenerlo en el salón principal por su disponibilidad. Pedro se encargará de coordinar con logística la reserva y acondicionamiento del espacio antes del 10 de mayo. Lucía sugiere invitar a un experto internacional. Ana propone contactar a un profesor de la universidad que trabaja en IA. La propuesta fue votada pero no fue aprobada, se decidió mantener invitados locales por presupuesto. Otro punto, el acta de la reunión anterior no fue firmada por Roberto. Se acuerda que Lucía le enviará el documento para que lo firme antes del viernes. Oscar comenta que el proyector de la sala sigue fallando. María se encargará de reportarlo al área técnica hoy mismo. Nada más que añadir, se levanta la sesión a las 10:18."

