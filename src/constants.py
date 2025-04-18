from jsonvalidator import ActaReunion, AsistenteCargo, Proposicion, Acuerdo, TipoSesion

ASISTENTE_CARGO = AsistenteCargo(nombre="", cargo="")
PROPOSICION = Proposicion(descripcion="No hay proposiciones", aprobada=True)
ACUERDO = Acuerdo(descripcion="", fecha_cumplimiento="", responsable="")
TIPO_SESION = TipoSesion("Ordinaria")
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
