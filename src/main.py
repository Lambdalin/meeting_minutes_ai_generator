import logging
from functools import cache

import gradio as gr
import pandas as pd

from constants import ACTA_DEFAULT, PROMPT
from lib.ai.asr import Whisper
from lib.ai.llm import OpenAIClient, vLLMClient
from lib.pdf import generate_and_save
from schema import ActaReunion
from settings import settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S", 
    filename="logs.log",
    filemode="a",
    encoding="utf-8",
)
log = logging.getLogger("app")

llm = vLLMClient() if settings.ENVIRONMENT == "prod" else OpenAIClient()
asr = Whisper()


@cache
def transcribe(audio_path: str | None):
    log.info("Transcribe: %s", audio_path)
    if audio_path is None:
        log.error("Audio not sended")
        gr.Error("Suba un audio.")
        return

    try:
        transcription = asr.transcribe(audio_path)
        log.debug("Transcription: %s", transcription)
        return (
            transcription,
            transcription,
            gr.update(interactive=True),
            gr.update(interactive=True),
        )

    except Exception as e:
        log.error("Error to transcribe audio: %s", e)
        gr.Error("Ocurrió un error al generar la transcripción.")


def activate_edit_transcription():
    return (
        gr.update(visible=True),  # edit_controls
        gr.update(interactive=True),  # transcription text editable
        gr.update(visible=False),  # edit button
        gr.update(visible=False),  # delete button
        gr.update(interactive=False),
    )  # transcribe button


def save_edit_transcription(edited_text, old_text):
    if old_text != edited_text:
        old_text = edited_text

    return (
        gr.update(
            value=old_text, interactive=False
        ),  # transcription_text_editable
        edited_text,  # transcription_text_show
        gr.update(visible=False),  # edit_controls
        gr.update(visible=True),  # edit_button
        gr.update(visible=True),  # delete_button
        gr.update(interactive=True),
    )


def cancel_edit_transcription(old_text):
    return (
        gr.update(value=old_text, interactive=False),
        gr.update(value=old_text),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(interactive=True),
    )


def delete_transcription():
    return (
        gr.update(value=None, interactive=False),
        gr.update(value=None),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


@cache
def generate_acta(transcription: str | None) -> ActaReunion | None:
    log.info("Generating 'Acta'")
    if transcription is None:
        log.error("No transcription sended")
        gr.Error("Debe haber una transcripción para generar un acta.")
        return

    try:
        prompt = PROMPT.format(transcription=transcription)
        log.debug("Prompt:\n%s", prompt)

        res = llm.generate(prompt, ActaReunion)
        log.debug("Response:\n%s", res)

        acta = ActaReunion.model_validate_json(res)
        log.debug("Acta:\n%s", acta)

        return acta

    except Exception as e:
        log.error("Error al generar acta: %s", e)
        gr.Error("Ocurrió un error al generar el acta.")


@cache
def generate_pdf(
    fecha,
    hora_inicio,
    hora_final,
    lugar,
    tipo_sesion,
    asistencia,
    orden,
    temas,
    propuestas,
    acuerdos,
    filepath="acta.pdf",
):
    log.info("Generating PDF")
    try:
        generate_and_save(
            fecha,
            hora_inicio,
            hora_final,
            lugar,
            tipo_sesion,
            asistencia,
            orden,
            temas,
            propuestas,
            acuerdos,
            filepath,
        )
        log.info("Correctly generated PDF")
        return gr.update(visible=True), gr.update(value=filepath)

    except Exception as e:
        log.error("Error al generar pdf:\n%s", e)
        gr.Error("Ocurrió un error al generar el PDF.")


def main():
    with gr.Blocks(fill_height=True, theme=gr.themes.Soft()) as ui:  # type: ignore
        transcription_state = gr.State()
        acta_state = gr.State(ACTA_DEFAULT)

        gr.Markdown("# Generador de actas de reuniones")

        with gr.Tab("Transcripción"):
            audio_input = gr.Audio(
                label="Subir audio", type="filepath", interactive=True
            )

            transcribe_button = gr.Button("Transcribir", interactive=False)
            transcription_editable_value = gr.Textbox(
                label="Transcripción del audio",
                max_lines=100,
                interactive=False,
            )

            with gr.Row():
                edit_button = gr.Button("Editar", interactive=False)
                delete_button = gr.Button("Eliminar", interactive=False)

            with gr.Row(visible=False) as edit_controls:
                save_changes_button = gr.Button("Guardar cambios")
                cancel_edit_button = gr.Button("Descartar")

            generate_button = gr.Button("Generar Acta")

            # 1. Recibe el audio y lo transcribe
            audio_input.change(
                fn=lambda audio: gr.update(interactive=audio is not None),
                inputs=audio_input,
                outputs=transcribe_button,
            )
            transcribe_button.click(
                fn=transcribe,
                inputs=audio_input,
                outputs=[
                    transcription_state,
                    transcription_editable_value,
                    edit_button,
                    delete_button,
                ],
            )

            # 2. Editar la transcripcion
            edit_button.click(
                fn=activate_edit_transcription,
                outputs=[
                    edit_controls,
                    transcription_editable_value,
                    edit_button,
                    delete_button,
                    transcribe_button,
                ],
            )

            save_changes_button.click(
                fn=save_edit_transcription,
                inputs=[transcription_editable_value, transcription_state],
                outputs=[
                    transcription_editable_value,
                    transcription_state,
                    edit_controls,
                    edit_button,
                    delete_button,
                    transcribe_button,
                ],
            )

            cancel_edit_button.click(
                fn=cancel_edit_transcription,
                inputs=transcription_state,
                outputs=[
                    transcription_editable_value,
                    transcription_state,
                    edit_controls,
                    edit_button,
                    delete_button,
                    transcribe_button,
                ],
            )

            delete_button.click(
                fn=delete_transcription,
                outputs=[
                    transcription_editable_value,
                    transcription_state,
                    edit_button,
                    delete_button,
                ],
            )

            # 3. Generar el acta
            generate_button.click(
                fn=generate_acta,
                inputs=[transcription_state],
                outputs=[acta_state],
            )

        with gr.Tab("Acta"):
            @gr.render(inputs=[acta_state], triggers=[acta_state.change])
            def display_form(acta: ActaReunion):
                with gr.Row():
                    fecha_input = gr.Textbox(value=acta.fecha, label="Fecha")
                    with gr.Row():
                        hora_input = gr.Textbox(
                            value=acta.hora, label="Hora de inicio"
                        )
                        hora_f_input = gr.Textbox(
                            label="Hora de finalizacion",
                            value=acta.hora_finalizacion,
                        )

                with gr.Row():
                    lugar_input = gr.Textbox(value=acta.lugar, label="Lugar")

                    tipo_sesion = gr.Radio(
                        choices=["Ordinaria", "Extraordinaria"],
                        interactive=True,
                        label="Tipo de sesión",
                        value=acta.tipo_sesion,
                    )

                df_asistencia = pd.DataFrame([
                    dict(ac) for ac in acta.asistencia_cargo
                ])
                if df_asistencia.empty:
                    df_asistencia = pd.DataFrame(columns=["Nombre", "Cargo"])
                    df_asistencia.loc[0] = [
                        "No se detectaron participantes",
                        "",
                    ]
                asistencia = gr.Dataframe(
                    interactive=True,
                    value=df_asistencia,
                    label="Asistencia",
                    row_count=(20, "dynamic"),
                    col_count=(2, "fixed"),
                )

                orden_del_dia = gr.Dataframe(
                    headers=["Orden"],
                    interactive=True,
                    value=acta.orden_del_dia,
                    label="Orden del día",
                    row_count=(10, "dynamic"),
                    col_count=(1, "fixed"),
                )

                temas_desarrollados = gr.Dataframe(
                    headers=["Temas"],
                    interactive=True,
                    value=acta.desarrollo_temas,
                    label="Temas desarrollados",
                    row_count=(10, "dynamic"),
                    col_count=(1, "fixed"),
                )

                df_propuestas = pd.DataFrame([
                    p.__dict__ for p in acta.proposiciones
                ])
                if df_propuestas.empty:
                    df_propuestas = pd.DataFrame(
                        columns=["Propuesta", "Estado"]
                    )
                    df_propuestas.loc[0] = ["No se detectaron propuestas", ""]
                df_propuestas.columns = ["Propuesta", "Estado"]
                df_propuestas.replace(
                    {True: "Aprobado", False: "No aprobado"}, inplace=True
                )

                gr.Markdown("Propuestas planteadas:")
                propuestas = gr.Dataframe(value=df_propuestas, interactive=True)

                df_acuerdos = pd.DataFrame([
                    a.__dict__ for a in acta.acuerdos_adoptados
                ])
                if df_acuerdos.empty:
                    df_acuerdos = pd.DataFrame(
                        columns=["Acuerdo", "Fecha limite", "Responsable"]
                    )
                    df_acuerdos.loc[0] = ["No se detectaron acuerdos", "", ""]
                df_acuerdos.columns = ["Acuerdo", "Fecha limite", "Responsable"]

                gr.Markdown("Acuerdos Aprobados:")
                acuerdos = gr.Dataframe(value=df_acuerdos, interactive=True)

                submit_form = gr.Button("Generar archivo de acta")

                with gr.Column(visible=False) as Download_side:
                    gr.Markdown("Su archivo está listo para descargarse!")
                    Archivo = gr.File()

                submit_form.click(
                    fn=generate_pdf,
                    inputs=[
                        fecha_input,
                        hora_input,
                        hora_f_input,
                        lugar_input,
                        tipo_sesion,
                        asistencia,
                        orden_del_dia,
                        temas_desarrollados,
                        propuestas,
                        acuerdos,
                    ],
                    outputs=[Download_side, Archivo],
                )
    ui.launch(share=True, debug=True)


if __name__ == "__main__":
    main()
