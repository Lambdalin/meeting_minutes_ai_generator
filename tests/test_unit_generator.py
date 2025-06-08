from src.constants import PROMPT
from src.lib.ai.llm import OpenAIClient
from src.schema import ActaReunion

def test_unit_generator():    
    text_example = 'Bueno, bueno... ya estamos en el aula inteligente, son las 9:15, empecemos, hoy toca sesión Ordinaria. Director ejecutivo Oscar Lucero Moya, Secretaria del director Lucia Gomez Vidal, Directora de operaciones Ana Maria Sanchez Mora, director de redes Roberto Martinez Sanchez, no Roberto no vino, mandó un correo, está con el tema del servidor caído. La orden del día de hoy es las ventas del trimestre. Comencemos hablando del acta anterior, fue aprobada, pero hay que cambiar la fecha, dice 2023 hay que poner 2024, bien, Ana, te corresponde cambiarle la fecha al acta, esta bien. Que pasa con las ventas del trimestre. Aquí tengo los números...  Mmm... 12% abajo. Nos dejaron colgados otra vez con los envíos. ¿propuestas para eso? Multarlos. Punto. Apoyo, pero que sea un porcentaje fijo. Yo propongo que dialoguemos con ellos, algún problema tuvieron que tener, ya hemos dialogado demasiado con ellos y es la cuarta vez que ocurre dialogar de nuevo es una perdida de tiempo, estoy de acuerdo, entonces votamos por aplicarles una multa? Todos a favor... Bien, aprobado, Maria redactara el documento de petición para sancionar a los multados, debes terminarlo antes de pasado mañana. Hacemos teletrabajo el viernes?, yo digo que sí, no podemos hacer teletrabajo esta semana tenemos que asistir a la oficina para reunirnos nuevamente, no se hará teletrabajo el viernes.  Prepara una propuesta para mayo. ¿Algo más? Sí, que arreglen el aire acondicionado, aquí parece el Sahara, Oscar avísale hoy al equipo técnico por favor. Se levanta la sesión, 10:40.'

    llm = OpenAIClient()
    prompt = PROMPT.format(transcription=text_example)

    acta_json = llm.generate(prompt, ActaReunion)
    assert ActaReunion.model_validate_json(acta_json)

    acta_model = ActaReunion.model_validate_json(acta_json)
    assert isinstance(acta_model, ActaReunion)
