from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import json

# Schema
# schema = {
#     "lugar": "string",
#     "hora": "string",
#     "fecha": "string",
#     "tipo_sesion": "string",
#     "orden_del_dia": ["string"],
#     "asistencia_cargo": [{"nombre": "string", "cargo": "string"}],
#     "desarrollo_temas": [
#         {"tema": "string", "sintesis": "string", "participante_numero": "number"}
#     ],
#     "proposiciones": [{"descripcion": "string", "aprobada": "boolean"}],
#     "acuerdos_adoptados": [
#         {
#             "descripcion": "string",
#             "fecha_cumplimiento": "string",
#             "responsable": "string",
#         }
#     ],
#     "hora_finalizacion": "string",
# }

# # Assume that `model` and `tokenizer` are loaded
# model.generation_config = GenerationConfig(do_sample=False, max_new_tokens=128, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)

# user_system_prompt = 'The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format.'
# json_system_prompt = f"""{user_system_prompt}

# ## Response Format

# Reply with JSON object ONLY."""

# json_messages = [{"role": "system", "content": json_system_prompt}, {"role": "user", "content": "Which is the highest mountain in the world? Mount Everest."}]
# json_inputs = tokenizer.apply_chat_template(json_messages, add_generation_prompt=True, return_tensors="pt")
# json_outpus = model.generate(json_inputs.to(model.device))
# # Generated text: '```json\n{\n  "question": "Which is the highest mountain in the world?",\n  "answer": "Mount Everest."\n}\n```<｜end▁of▁sentence｜>'


class AsistenteCargo(BaseModel):
    nombre: str = Field(..., description="Nombre completo del asistente a la reunión. Solo incluye nombres y apellidos, sin el cargo o rol que tiene en la empresa o cualquier informacion extra",
                        examples=["Mario Diaz González", "Roberto", "Joaquin Rivas"])
    cargo: str = Field(..., description="Rol o posición del asistente en la organización",
                    examples=["Director ejecutivo", "Decana de la facultad de tecnologias interactivas"])


class Proposicion(BaseModel):
    descripcion: str = Field(..., description="Texto de la propuesta presentada.",
                        examples=["Se propone extender el tiempo de descanso después de la guardia laboral", "Se propone multar a los que dañen la propiedad de la empresa"])
    aprobada: bool = Field(..., description="Indica si la propuesta fue aprobada (True/False).")


class Acuerdo(BaseModel):
    descripcion: str = Field(...,description="Detalles del acuerdo adoptado. Toda acción o decisión que tenga un responsable y una fecha límite, o que se aprobó como obligación. Debe contener solo la tarea concreta o acción a realizar, no el nombre del responsable.",
                            examples=["Mandar una carta de peticion para extender el tiempo de descanzo", "Crear un documento de aviso para eviar a los multados"])
    fecha_cumplimiento: str = Field(..., description="Fecha límite para cumplir el acuerdo (formato DD-MM-YYYY).",
                            examples=['15-04-25'])
    responsable: str = Field(..., description="Nombre de la persona encargada de cumplir el acuerdo.",
                            examples=["Mario Diaz González", "Roberto", "Joaquin Rivas"]
    )


class TipoSesion(str, Enum):
    Ordinaria = "Ordinaria"
    Extraordinaria = "Extraordinaria"


class ActaReunion(BaseModel):
    lugar: Optional[str] = Field(description="Ubicación física donde se realizó la reunión.")
    fecha: Optional[str] = Field(
        description="Fecha de realización de la reunión (formato DD-MM-YYYY)."
    )
    hora: Optional[str] = Field(
        ..., description="Hora de inicio de la reunión (formato HH:MM). Opcional."
    )
    tipo_sesion: Optional[TipoSesion] = Field(
        ..., description="Tipo de sesión (ej. 'Ordinaria', 'Extraordinaria'). Opcional."
    )
    asistencia_cargo: List[AsistenteCargo] = Field(
        ..., description="Lista de personas presentes con su cargo. Excluye a personas que se dijo explícitamente que no asistieron."
    )
    orden_del_dia: List[str] = Field(
        ..., description="Lista de temas planificados para tratar en la reunión. Solo incluye lo que se dijo que sería la orden del día, no todo lo que se discutió."
    )
    desarrollo_temas: List[str] = Field(
        ..., description="Lista de temas discutidos durante la reunión."
    )
    proposiciones: List[Proposicion] = Field(
        ..., description="Lista de propuestas presentadas y su estado de aprobación.",
    )
    acuerdos_adoptados: List[Acuerdo] = Field(
        ..., description="Acuerdos alcanzados durante la reunión."
    )
    hora_finalizacion: Optional[str] = Field(
        ..., description="Hora de finalización de la reunión (formato HH:MM)."
    )

# def to_json(self, file_path: str):
#         with open(file_path, 'w', encoding='utf-8') as f:
#             json.dump(self.model_dump(), f, indent=4, ensure_ascii=False)

schema = ActaReunion.model_json_schema()



