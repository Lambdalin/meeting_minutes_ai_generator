import gradio as gr

def transcribe_audio(audio_file):
    # result = transcription_model.transcribe(audio_file)
    # transcription = result["text"]
    # return transcription
    return 'This is a transcription example...'

def delete_transcription():
    return gr.update(value = None, visible=False), gr.update(value = None, visible=True), gr.update(interactive = False), gr.update(interactive = False)

def audio_interface(audio):
    
    if audio is None:
        return "Please upload an audio file.", False
#add error handlers with the transcription
    transcription = transcribe_audio(audio)

    return transcription, transcription, gr.update(interactive=True), gr.update(interactive=True) 


def edit_mode(edit_mode):
    return gr.update(visible=True),gr.update(visible=True),gr.update(visible=False),gr.update(visible=False), gr.update(visible=False), gr.update(interactive=False)


def save_changes(edited_text, old_text):
    if old_text != edited_text:
        return gr.update(value = edited_text, visible=False), gr.update(value = edited_text, visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True), gr.update(interactive=True)
    else: 
        return gr.update(value = old_text, visible=False), gr.update(value = old_text, visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True), gr.update(interactive=True) 


def cancel_edit(old_text):
    return gr.update(value = old_text, visible=False), gr.update(value = old_text, visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True), gr.update(interactive=True)




with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("### Generador de actas de reuniones")


    audio_input = gr.Audio(label="Subir audio", type="filepath", interactive=True) #done
        
    transcribe_button = gr.Button("Transcribir", interactive=False) #done
    
    transcription_text_show = gr.Markdown(label="Transcripción del audio")

    transcription_text_editable = gr.Textbox(label="Transcripción del audio", visible=False)

    with gr.Row():
        edit_button = gr.Button("Editar", interactive=False) #done
        delete_button = gr.Button("Eliminar", interactive=False) #pending

    with gr.Row(visible=False) as edit_controls:
        save_button = gr.Button("Guardar cambios") 
        cancel_edit_button = gr.Button("Descartar")

    # Update transcription button state based on audio upload
    audio_input.change(
        fn=lambda audio: gr.update(interactive=audio is not None),
        inputs=audio_input,
        outputs=transcribe_button
    )
    # Perform transcription
    transcribe_button.click(
        fn=audio_interface,
        inputs=audio_input,
        outputs=[transcription_text_editable, transcription_text_show, edit_button, delete_button]
    )

    # Enable edit mode
    edit_button.click(
        fn=lambda: edit_mode(True),
        outputs=[edit_controls, transcription_text_editable, edit_button, delete_button, transcription_text_show, transcribe_button]
    )
    
    # Save changes
    save_button.click(
        fn=save_changes,
        inputs=[transcription_text_editable, transcription_text_show],
        outputs=[transcription_text_editable, transcription_text_show, edit_controls, edit_button, delete_button, transcribe_button]
    )

    # Cancel edit
    cancel_edit_button.click(
        fn=cancel_edit,
        inputs=transcription_text_show,
        outputs=[transcription_text_editable, transcription_text_show, edit_controls, edit_button, delete_button, transcribe_button]
    )

    # Delete transcription
    delete_button.click(
        fn=delete_transcription,
        outputs=[transcription_text_editable,transcription_text_show, edit_button, delete_button]
    )

demo.launch()