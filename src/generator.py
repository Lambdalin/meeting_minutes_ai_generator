import typing as t
from openai import OpenAI
from jsonvalidator import schema
from settings import settings
from vllm import LLM, SamplingParams
from vllm.sampling_params import GuidedDecodingParams




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
            guided_decoding_params = GuidedDecodingParams(json = schema)
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
            # response = llm.responses.create(
            #     model=settings.LLM_MODEL,
            #     instructions= "Genera un JSON con la informacion necesaria para crear un acta de reunion",
            #     input=prompt,
            #     text={
            #         "format":{
            #             "type": "json_schema",
            #             "name": "acta-reunion",
            #             "schema": schema,
            #             "strict": True
            #         }
            #     },
            #     **params,
            # )
            # return response.output_text
            response = llm.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """Eres un experto encargado de generar un JSON con la informacion de un acta de reunion, debes tener en cuenta las siguientes especificaciones:
                        -La orden del dia es el o los temas principales de la reunion debe contener explicitamente lo que se dijo que seria la orden del dia, evita poner otros temas que se desarrollan en la reunion en este campo.
                        -En la asistencia_cargo debes excluir los nombres de las personas que estan ausentes aunque se hayan mencionado en la reunion.
                        -En el desarrollo de temas debes poner los temas de los que se hablaron con un pequeño resumen.
                        -las proposiciones son las propuestas que se hacen en la reunion, las puedes identificar porque siempre se dice si fueron aprobadas o no.
                        -los acuerdos pueden ser proposiciones aprobadas, tareas o cualquier evento que tenga un responsable y una fecha limite.
                        """,
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


llm = get_client()

text = "Bueno, bueno... ya estamos en el aula inteligente, son las 9:15, empecemos, hoy toca sesión Ordinaria. Director ejecutivo Oscar Lucero Moya, Secretaria del director Lucia Gomez Vidal, Directora de operaciones Ana Maria Sanchez Mora, director de redes Roberto Martinez Sanchez, no Roberto no vino, mandó un correo, está con el tema del servidor caído. La orden del día de hoy es las ventas del trimestre. Comencemos hablando del acta anterior,  fue aprobada, pero hay que cambiar la fecha, dice 2023 hay que poner 2024, bien, Ana, te corresponde cambiarle la fecha al acta, esta bien. Que pasa con las ventas del trimestre. Aquí tengo los números...  Mmm... 12% abajo. Nos dejaron colgados otra vez con los envíos. ¿propuestas para eso? Multarlos. Punto. Apoyo, pero que sea un porcentaje fijo. Yo propongo que dialoguemos con ellos, algún problema tuvieron que tener, ya hemos dialogado demasiado con ellos y es la cuarta vez que ocurre dialogar de nuevo es una perdida de tiempo, estoy de acuerdo, entonces votamos por aplicarles una multa? Todos a favor... Bien, aprobado, Maria redactara el documento de petición para sancionar a los multados, debes terminarlo antes de pasado manana. Hacemos teletrabajo el viernes?, yo digo que sí, no podemos hacer teletrabajo esta semana tenemos que asistir a la oficina para reunirnos nuevamente, no se hara teletrabajo el viernes.  Prepara una propuesta para mayo. ¿Algo más? Sí, que arreglen el aire acondicionado, aquí parece el Sahara, Oscar avísale hoy al equipo técnico por favor. Se levanta la sesión, 10:40."
res = generate(text, llm)
print(res)

output = {
    "lugar": "Aula Inteligente",
    "fecha": "2023-10-05",
    "hora": "9:15 AM",
    "tipo_sesion": "Ordinaria",
    "orden_del_dia": ["Ventas del trimestre"],
    "asistencia_cargo": [],
    "desarrollo_temas": [
        {
            "tema": "Ventas del trimestre",
            "sintesis": "Ventas del trimestre han caído 12% en comparación con el año anterior. Los envíos se han colgado otra vez, lo que ha llevado a una multa por parte de los clientes. Propuestas para resolver este problema incluyen multarlos o dialogar con ellos sobre un porcentaje fijo de la multa.",
        }
    ],
    "proposiciones": [
        {
            "descripcion": "Multar a los clientes por el descenso en las ventas.",
            "aprobada": false,
        },
        {
            "descripcion": "Dialogar con los clientes sobre un porcentaje fijo de la multa.",
            "aprobada": true,
        },
    ],
    "acuerdos_adoptados": [],
    "hora_finalizacion": "10:40 AM",
}
