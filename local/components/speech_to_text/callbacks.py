# import dash
# from dash.dependencies import Input, Output
# import threading
# from components.speech_to_text.recorder import recorder

# transcript = "" 

# def get_callbacks(app: dash.Dash):
#     @app.callback(
#         Output("transcription-output", "children"),
#         Input("update-interval", "n_intervals"),
#         prevent_initial_call=True,
#     )
#     def update_output(_):
#         global transcript
#         while not recorder.transcription_queue.empty():
#             transcript += recorder.transcription_queue.get() + " "
#         return transcript

#     @app.callback(
#         Output("start-button", "disabled"),
#         Input("start-button", "n_clicks"),
#         prevent_initial_call=True,)
#     def start_recording(n_clicks):
#         if n_clicks:
#             t = threading.Thread(target=recorder.start_recording, name="start_recording")
#             # t.daemon = True
#             t.start()
#             return True
#         return False

#     @app.callback(
#         Output("stop-button", "disabled"),
#         Input("stop-button", "n_clicks"),
#         prevent_initial_call=True,)
#     def stop_recording(n_clicks):
#         if n_clicks:
#             recorder.stop_recording()
#             return True
#         return False
#     return
