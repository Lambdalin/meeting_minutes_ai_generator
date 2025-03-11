import gradio as gr
from transcriber import transcriber


def delete_transcription():
    return (gr.update(value = None, interactive = False), 
            gr.update(value = None), 
            gr.update(interactive = False), 
            gr.update(interactive = False))

def audio_interface(audio):
    
    if audio is None:
        error_message = "Please upload an audio file."
        return (
            error_message,  
            error_message,  
            gr.update(interactive=False),  
            gr.update(interactive=False)   
        )
    
    #transcription = transcriber(audio)
    transcription = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida. Duis ac tellus et risus vulputate vehicula. Donec lobortis risus a elit. Etiam tempor. Ut ullamcorper, ligula eu tempor congue, eros est euismod turpis, id tincidunt sapien risus a quam. Maecenas fermentum consequat mi. Donec fermentum. Pellentesque malesuada nulla a mi. Duis sapien sem, aliquet nec, commodo eget, consequat quis, neque. Aliquam faucibus, elit ut dictum aliquet, felis nisl adipiscing sapien, sed malesuada diam lacus eget erat. Cras mollis scelerisque nunc. Nullam arcu. Aliquam consequat. Curabitur augue lorem, dapibus quis, laoreet et, pretium ac, nisi. Aenean magna nisl, mollis quis, molestie eu, feugiat in, orci. In hac habitasse platea dictumst.Fusce convallis, mauris imperdiet gravida bibendum, nisl turpis suscipit mauris, sed placerat ipsum nisi eu enim. In hac habitasse platea dictumst. Integer nec libero. Vivamus nec lorem. Donec leo. Vivamus fermentum nibh in augue. Praesent a lacus at urna congue rutrum. Nulla enim eros, porttitor eu, tempus id, varius non, nibh. Duis enim nulla, luctus eu, dapibus lacinia, venenatis id, quam. Vestibulum imperdiet, magna nec eleifend rutrum, nunc lectus vestibulum velit, euismod lacinia quam nisl id lorem. Quisque erat. Vestibulum pellentesque, justo mollis pretium suscipit, justo nulla blandit libero, in blandit augue justo quis nisl. Fusce mattis viverra elit. Fusce quis tortor. Integer commodo, orci ut porttitor lobortis, odio magna sodales lectus, at molestie diam odio nec magna. Praesent nec nisl a purus blandit viverra. Nullam ac urna. Proin eget elit. Nunc scelerisque venenatis urna. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed vulputate, ligula eget sollicitudin vehicula, arcu libero sodales leo, eget blandit nunc tortor eu nibh. Nullam libero. Integer nec libero. Vivamus nec lorem. Donec leo. Vivamus fermentum nibh in augue. Praesent a lacus at urna congue rutrum. Nulla enim eros, porttitor eu, tempus id, var.'

    return (transcription, 
            transcription, 
            gr.update(interactive = True), 
            gr.update(interactive = True)) 


def edit_mode():
    return (gr.update(visible = True), #edit_controls
            gr.update(interactive = True), #transcription text editable
            gr.update(visible = False), #edit button
            gr.update(visible = False), # delete button
            gr.update(interactive = False)) # transcribe button


def save_changes(edited_text, old_text):
    if old_text != edited_text:
        return (gr.update(value = edited_text, interactive = False), # transcription_text_editable
                gr.update(value = edited_text), # transcription_text_show
                gr.update(visible = False), # edit_controls
                gr.update(visible = True), # edit_button
                gr.update(visible = True), # delete_button
                gr.update(interactive = True)) # transcribe_button
    else: 
        return (gr.update(value = old_text, interactive = False), 
                gr.update(value = old_text), 
                gr.update(visible = False), 
                gr.update(visible = True),
                gr.update(visible = True), 
                gr.update(interactive = True)) 


def cancel_edit(old_text):
    return (gr.update(value = old_text, interactive = False), 
            gr.update(value = old_text), 
            gr.update(visible = False), 
            gr.update(visible = True),
            gr.update(visible = True), 
            gr.update(interactive = True))




with gr.Blocks(fill_height=True) as demo:

    gr.Markdown("### Generador de actas de reuniones")

    audio_input = gr.Audio(label = "Subir audio", 
                        type = "filepath", 
                        interactive = True) 
        
    transcribe_button = gr.Button("Transcribir", 
                                interactive = False) 
    
    #transcription_text_show = gr.Markdown(label = "Transcripción del audio")
    transcription_text_show = gr.State()
    transcription_text_editable = gr.Textbox(label = "Transcripción del audio",
                                            max_lines=100,
                                            interactive=False)

    with gr.Row():
        edit_button = gr.Button("Editar", 
                                interactive = False) 
        delete_button = gr.Button("Eliminar", 
                                interactive=False) 
        

    with gr.Row(visible = False) as edit_controls:
        save_changes_button = gr.Button("Guardar cambios") 
        cancel_edit_button = gr.Button("Descartar")

    # Update transcription button state based on audio upload
    audio_input.change(
        fn = lambda audio: gr.update(interactive = audio is not None),
        inputs = audio_input,
        outputs = transcribe_button
    )
    # Perform transcription
    transcribe_button.click(
        fn = audio_interface,
        inputs = audio_input,
        outputs = [transcription_text_editable, 
                transcription_text_show, 
                edit_button, 
                delete_button]
    )

    # Enable edit mode
    edit_button.click(
        fn = edit_mode,
        outputs = [edit_controls, 
                transcription_text_editable, 
                edit_button, 
                delete_button, 
                transcribe_button]
    )
    
    # Save changes
    save_changes_button.click(
        fn = save_changes,
        inputs = [transcription_text_editable, 
                transcription_text_show],
        outputs = [transcription_text_editable, 
                transcription_text_show, 
                edit_controls, 
                edit_button, 
                delete_button, 
                transcribe_button]
    )

    # Cancel edit
    cancel_edit_button.click(
        fn = cancel_edit,
        inputs = transcription_text_show,
        outputs = [transcription_text_editable, 
                transcription_text_show, 
                edit_controls, 
                edit_button, 
                delete_button, 
                transcribe_button]
    )

    # Delete transcription
    delete_button.click(
        fn = delete_transcription,
        outputs = [transcription_text_editable,
                transcription_text_show, 
                edit_button, 
                delete_button]
    )

demo.launch()