import gradio as gr

def transcribe_audio(audio_file):
    # result = transcription_model.transcribe(audio_file)
    # transcription = result["text"]
    # return transcription
    return 'This is a transcription example...'

def edit_transcription(text):
    return text

def delete_transcription():
    return "", False


def audio_interface(audio):
    assert audio, 'Audio should be defined'

    if audio is None:
        return "Please upload an audio file.", False
#add error handlers with the transcription
    transcription = transcribe_audio(audio)

    return transcription, transcription, gr.update(interactive=True), gr.update(interactive=True) 


def edit_mode(edit_mode):
    return gr.update(visible=True),gr.update(visible=True),gr.update(visible=False),gr.update(visible=False), gr.update(visible=False)


def save_changes(edited_text, old_text):
    if old_text != edited_text:
        return gr.update(value = edited_text, visible=False), gr.update(value = edited_text, visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True)
    else: 
        return gr.update(value = old_text, visible=False), gr.update(value = old_text, visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True) 


def cancel_edit(old_text):
    return gr.update(value = old_text, visible=False), gr.update(value = old_text, visible=True), gr.update(visible=False), gr.update(visible=True),gr.update(visible=True)




with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("### Audio Transcription Interface")


    audio_input = gr.Audio(label="Upload Audio", type="filepath", interactive=True) #done
        
    transcribe_button = gr.Button("Transcribe Audio", interactive=False) #done
    
    transcription_text_show = gr.Markdown(label="Transcription")

    transcription_text_editable = gr.Textbox(label="Transcription", visible=False)

    with gr.Row():
        edit_button = gr.Button("Edit Transcription", interactive=False) #done
        delete_button = gr.Button("Delete Transcription", interactive=False) #pending

    with gr.Row(visible=False) as edit_controls:
        save_button = gr.Button("Save Changes") 
        cancel_edit_button = gr.Button("Cancel Edit")

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
        outputs=[edit_controls, transcription_text_editable, edit_button, delete_button, transcription_text_show]
    )
    
    # Save changes
    save_button.click(
        fn=save_changes,
        inputs=[transcription_text_editable, transcription_text_show],
        outputs=[transcription_text_editable, transcription_text_show, edit_controls, edit_button, delete_button]
    )

    # Cancel edit
    cancel_edit_button.click(
        fn=cancel_edit,
        inputs=transcription_text_show,
        outputs=[transcription_text_editable, transcription_text_show, edit_controls, edit_button, delete_button]
    )

    # Delete transcription
    delete_button.click(
        fn=delete_transcription,
        outputs=[transcription_text_editable, edit_button]
    )

demo.launch()