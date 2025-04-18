import gradio as gr
import pandas as pd

#from transcriber import transcriber
from generator import generate
from generator import get_client
from jsonvalidator import ActaReunion
from act_downloadable import Act_pdf as create_pdf
from constants import ACTA_DEFAULT

llm = get_client()

def generate_act(text):
    res = generate(text, llm)
    
    final_act = ActaReunion.model_validate_json(res)

    return (final_act, gr.update(visible=False))


def delete_transcription():
    return (
        gr.update(value=None, interactive=False),
        gr.update(value=None),
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def transcribe(audio):
    if audio is None:
        gr.Error("Please upload an audio file.")

    #transcription = transcriber(audio)
    transcription = 'Transcription example'
    return (
        transcription,
        transcription,
        gr.update(interactive=True),
        gr.update(interactive=True),
    )


def activate_edit_mode():
    return (
        gr.update(visible=True),  # edit_controls
        gr.update(interactive=True),  # transcription text editable
        gr.update(visible=False),  # edit button
        gr.update(visible=False),  # delete button
        gr.update(interactive=False),
    )  # transcribe button


def save_changes(edited_text, old_text):
    if old_text != edited_text:
        old_text = edited_text

    return (
        gr.update(value=old_text, interactive=False),  # transcription_text_editable
        edited_text,  # transcription_text_show
        gr.update(visible=False),  # edit_controls
        gr.update(visible=True),  # edit_button
        gr.update(visible=True),  # delete_button
        gr.update(interactive=True),
    )


def cancel_edit(old_text):
    return (
        gr.update(value=old_text, interactive=False),
        gr.update(value=old_text),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(interactive=True),
    )



with gr.Blocks(fill_height=True, theme=gr.themes.Soft()) as demo:
    transcription_value = gr.State()
    act_state = gr.State(ACTA_DEFAULT)

    gr.Markdown("# Generador de actas de reuniones")

    with gr.Column() as paso1:
        audio_input = gr.Audio(label="Subir audio", type="filepath", interactive=True)
        transcribe_button = gr.Button("Transcribir", interactive=False)
        transcription_editable_value = gr.Textbox(
            label="Transcripción del audio", max_lines=100, interactive=False
        )

        with gr.Row():
            edit_button = gr.Button("Editar", interactive=False)
            delete_button = gr.Button("Eliminar", interactive=False)

        with gr.Row(visible=False) as edit_controls:
            save_changes_button = gr.Button("Guardar cambios")
            cancel_edit_button = gr.Button("Descartar")

        generate_button = gr.Button("Generar Acta")

    @gr.render(inputs=[act_state], triggers=[act_state.change])
    def display_form(acta: ActaReunion):
        with gr.Row():
            fecha_input = gr.Textbox(value=acta.fecha, label="Fecha")
            with gr.Row():
                hora_input = gr.Textbox(value=acta.hora, label="Hora de inicio")
                hora_f_input = gr.Textbox(
                    label="Hora de finalizacion", value=acta.hora_finalizacion
                )

        with gr.Row():
            lugar_input = gr.Textbox(value=acta.lugar, label="Lugar")

            tipo_sesion = gr.Radio(
                choices=["Ordinaria", "Extraordinaria"],
                interactive=True,
                label="Tipo de sesión",
                value=acta.tipo_sesion,
            )

        df_asistencia = pd.DataFrame([ac.__dict__ for ac in acta.asistencia_cargo])
        df_asistencia.columns = ["Nombre", "Cargo"]
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

        df_propuestas = pd.DataFrame([p.__dict__ for p in acta.proposiciones])
        if df_propuestas.empty:
            df_propuestas = pd.DataFrame(columns=["Propuesta", "Estado"])
            df_propuestas.loc[0] = ["No se detectaron propuestas", '']
        df_propuestas.columns = ["Propuesta", "Estado"]
        df_propuestas.replace({True: "Aprobado", False: "No aprobado"}, inplace=True)

        gr.Markdown("Propuestas planteadas:")
        propuestas = gr.Dataframe(
            value=df_propuestas,
        )

        df_acuerdos = pd.DataFrame([a.__dict__ for a in acta.acuerdos_adoptados])
        if df_acuerdos.empty:
            df_acuerdos = pd.DataFrame(columns=["Acuerdo", "Fecha limite", "Responsable"])
            df_acuerdos.loc[0] = ["No se detectaron acuerdos", '', '']
        df_acuerdos.columns = ["Acuerdo", "Fecha limite", "Responsable"]

        gr.Markdown("Acuerdos Aprobados:")
        acuerdos = gr.Dataframe(
            value=df_acuerdos,
        )

        submit_form = gr.Button('Generar archivo de acta')

        with gr.Column(visible = False) as Download_side:
            gr.Markdown("Su archivo está listo para descargarse!")
            Archivo = gr.File()

        submit_form.click(
            fn = create_pdf,
            inputs=[fecha_input, 
                    hora_input, 
                    hora_f_input, 
                    lugar_input, 
                    tipo_sesion, 
                    asistencia, 
                    orden_del_dia, 
                    temas_desarrollados, 
                    propuestas, 
                    acuerdos],
            outputs=[Download_side, Archivo]
        )

    
    audio_input.change(
        fn=lambda audio: gr.update(interactive=audio is not None),
        inputs=audio_input,
        outputs=transcribe_button,
    )

    transcribe_button.click(
        fn=transcribe,
        inputs=audio_input,
        outputs=[
            transcription_value,
            transcription_editable_value,
            edit_button,
            delete_button,
        ],
    )

    edit_button.click(
        fn=activate_edit_mode,
        outputs=[
            edit_controls,
            transcription_editable_value,
            edit_button,
            delete_button,
            transcribe_button,
        ],
    )

    save_changes_button.click(
        fn=save_changes,
        inputs=[transcription_editable_value, transcription_value],
        outputs=[
            transcription_editable_value,
            transcription_value,
            edit_controls,
            edit_button,
            delete_button,
            transcribe_button,
        ],
    )

    cancel_edit_button.click(
        fn=cancel_edit,
        inputs=transcription_value,
        outputs=[
            transcription_editable_value,
            transcription_value,
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
            transcription_value,
            edit_button,
            delete_button,
        ],
    )

    generate_button.click(
        fn=generate_act,
        inputs=[transcription_value],
        outputs=[act_state, paso1],
    )
