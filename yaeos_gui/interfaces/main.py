import gradio as gr


def main_int():
    gr.Text("Hello, this is the main interface.")


interface = gr.Interface(
    main_int,
    inputs=[gr.Component()],
    outputs=[0],
)