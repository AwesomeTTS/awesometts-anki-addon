import aqt
import anki.hooks
import json
import base64
import aqt


def makeLinkHandler(addon):
    def playbackFailure(exception, text):
        playback_error_message = f"Could not play back {text}: {exception}"
        aqt.utils.showWarning("AwesomeTTS: " + playback_error_message)

    def linkHandler(deckbrowser, url):

        # print(f"* linkHandler {url}")

        if url.startswith('awesomettsplayback:'):
            # load the json part
            colon_index = url.find(':')

            base64_str = url[colon_index+1:]
            # print(f"* base64 string: {base64_str}")

            # base64_bytes = str.encode(base64_str)
            json_bytes = base64.b64decode(base64_str)
            json_str = json_bytes.decode('utf-8')
            # print(f"* json string: {json_str}")

            data = json.loads(json_str)

            callbacks = dict(
                okay=addon.player.preview,
                fail=playbackFailure
            )

            text = data['text']
            awesometts_preset_name = data['preset']
            preset = addon.config['presets'][awesometts_preset_name]

            addon.router(
                svc_id=preset['service'],
                text=text,
                options=preset,
                callbacks=callbacks
            )

            addon.config['homescreen_last_preset'] = awesometts_preset_name

        return False

    
    return linkHandler

def makeDeckBrowserRenderContent(addon):

    def on_deckbrowser_will_render_content(deck_browser, content):
        if addon.config['homescreen_show'] == False:
            # user doesn't want to see the homescreen
            return

        night_mode = aqt.mw.pm.night_mode()

        preset_names = list(addon.config['presets'].keys())
        if len(preset_names) == 0:
            # no presets defined
            return
        preset_names.sort()
        html_select_options = [f'<option value="{preset_name}" {"selected" if preset_name == addon.config["homescreen_last_preset"] else ""}>{preset_name}</option>' for preset_name in preset_names]
        html_select_options_str = '\n'.join(html_select_options)

        # theme colors are plagiarized from review heatmap
        # https://github.com/glutanimate/review-heatmap/blob/master/resources/web/review-heatmap.css

        light_dark_background = "#E0E0E0"
        light_dark_border_color = "#9E9E9E"
        light_dark_placeholder_color = "#BDBDBD"
        if night_mode:
            light_dark_background = "#616161"
            light_dark_border_color = "#424242"
            light_dark_placeholder_color = "#757575"

        awesometts_plus_tag = ''
        if addon.languagetools.use_plus_mode():
            awesometts_plus_tag= '<span style="font-size: 18px;">AwesomeTTS <span style="color:#FF0000; font-weight: bold;">Plus</span></span>'


        html_content = """
        <br/>

        <style>
        .atts-common {
            font-size: 40px;  
            margin-bottom: 10px;
        }

        .atts-common-background {
            background-color: """ + light_dark_background + """;
            border: 1px solid """ + light_dark_border_color + """;
            border-radius: 4px;
        }

        .atts-text-input {
            width: 100%;
        }
        .atts-text-input:focus {
            background-color: #BBDEFB;
            color: #0063de;
        }
        .atts-text-input::placeholder { /* Chrome, Firefox, Opera, Safari 10.1+ */
            color: """ + light_dark_placeholder_color + """;
        }        

        .atts-presets {
            font-size: 16px;
            border-radius: 4px;  
            width: 100%;
        }

        .atts-say-button {
            border-radius: 10px;
        }       
        .atts-say-button-label {
            font-size: 30px;
            color: #0063de;
        } 
        .atts-frame {
            margin-top: 25px;
            width: 70%;
        }

        </style>
        <div class="atts-frame-common atts-frame">
        """ + awesometts_plus_tag + """
        <input id='speech-input' class="atts-common atts-text-input atts-common-background" placeholder="Pronounce with AwesomeTTS">
        <br/>
        <select name='preset' id='preset' class='atts-common atts-presets atts-common-background'>
        """ + html_select_options_str + """
        </select>
        <script>
        function getCommand() {
            const input_text = document.getElementById('speech-input').value;
            const preset = document.getElementById('preset').value;;
            const json_data = {'text': document.getElementById('speech-input').value, 'preset': preset};
            const final_command = 'awesomettsplayback:' +  btoa(unescape(encodeURIComponent(JSON.stringify(json_data))));
            return final_command;
        }
        </script>
        <br/>
        <button onclick="return pycmd(getCommand())" class="atts-common atts-say-button"><span class="atts-common atts-say-button-label">Say</span></button>
        </div>
        """

        content.stats += html_content

    return on_deckbrowser_will_render_content



