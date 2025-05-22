from pydantic import BaseModel, Field


class AsistenteCargo(BaseModel):
    nombre: str | None = Field(
        ...,
        description="Nombre completo del asistente a la reunión. Solo incluye nombres y apellidos.",
        examples=["Mario Diaz González", "Roberto", "Joaquin Rivas"],
    )
    cargo: str | None = Field(
        ...,
        description="Rol o posición del asistente en la organización",
        examples=[
            "Director ejecutivo",
            "Decana de la facultad de tecnologias interactivas",
        ],
    )


class Proposicion(BaseModel):
    descripcion: str | None = Field(
        ...,
        description="Texto de la propuesta presentada.",
        examples=[
            "Se propone extender el tiempo de descanso después de la guardia laboral",
            "Se propone multar a los que dañen la propiedad de la empresa",
        ],
    )
    aprobada: bool | None = Field(
        ...,
        description="Indica si la propuesta fue aprobada (True/False).",
        examples=[True, False],
    )


class Acuerdo(BaseModel):
    descripcion: str | None = Field(
        ...,
        description="Detalles del acuerdo adoptado. Toda acción o decisión que tenga un responsable y una fecha límite, o que se aprobó como obligación. Debe contener solo la tarea concreta o acción a realizar, no el nombre del responsable.",
        examples=[
            "Mandar una carta de peticion para extender el tiempo de descanzo",
            "Crear un documento de aviso para eviar a los multados",
        ],
    )
    fecha_cumplimiento: str | None = Field(
        ...,
        description="Fecha límite para cumplir el acuerdo (formato DD-MM-YYYY).",
        examples=["15-04-2025"],
    )
    responsable: str | None = Field(
        ...,
        description="Nombre de la persona encargada de cumplir el acuerdo.",
        examples=["Mario Diaz González", "Roberto", "Joaquin Rivas"],
    )


class ActaReunion(BaseModel):
    lugar: str | None = Field(
        ...,
        description="Ubicación física donde se realizó la reunión.",
        examples=["Aula Inteligente"],
    )
    fecha: str | None = Field(
        ...,
        description="Fecha de realización de la reunión (formato DD-MM-YYYY).",
        examples=["15-04-2025"],
    )
    hora: str | None = Field(
        ...,
        description="Hora de inicio de la reunión (formato HH:MM). Opcional.",
        examples=["10:30"],
    )
    tipo_sesion: str | None = Field(
        ...,
        description="Tipo de sesión ('Ordinaria' o 'Extraordinaria'). Opcional.",
        examples=["Ordinaria", "Extraordinaria"],
    )
    asistencia_cargo: list[AsistenteCargo] = Field(
        ...,
        description="Lista de personas presentes con su cargo. Excluye a personas que se dijo explícitamente que no asistieron.",
    )
    orden_del_dia: list[str] = Field(
        ...,
        description="Lista de temas planificados para tratar en la reunión. Solo incluye lo que se dijo que sería la orden del día, no todo lo que se discutió.",
    )
    desarrollo_temas: list[str] = Field(
        ..., description="Lista de temas discutidos durante la reunión."
    )
    proposiciones: list[Proposicion] = Field(
        ...,
        description="Lista de propuestas presentadas y su estado de aprobación.",
    )
    acuerdos_adoptados: list[Acuerdo] = Field(
        ..., description="Acuerdos alcanzados durante la reunión."
    )
    hora_finalizacion: str | None = Field(
        ...,
        description="Hora de finalización de la reunión (formato HH:MM).",
        examples=["12:30"],
    )
