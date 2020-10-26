import aqt
import anki.hooks
import json
import base64

def failure(exception, text):
    # don't do anything, can't popup any dialogs
    print(f"* failure: {exception}")


def makeLinkHandler(addon):
    def linkHandler(deckbrowser, url):

        print(f"* linkHandler {url}")

        if url.startswith('awesomettsplayback:'):
            # load the json part
            colon_index = url.find(':')

            base64_str = url[colon_index+1:]
            print(f"* base64 string: {base64_str}")

            # base64_bytes = str.encode(base64_str)
            json_bytes = base64.b64decode(base64_str)
            json_str = json_bytes.decode('utf-8')
            print(f"* json string: {json_str}")

            data = json.loads(json_str)


            callbacks = dict(
                okay=addon.player.preview,
                fail=failure
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

        return False

    
    return linkHandler

def makeDeckBrowserRenderContent(addon):

    def on_deckbrowser_will_render_content(deck_browser, content):
        print(f"** on_deckbrowser_will_render_content")
        #print(deck_browser)    
        #print(content)

        preset_names = addon.config['presets'].keys()
        html_select_options = [f'<option value="{preset_name}">{preset_name}</option>' for preset_name in preset_names]
        html_select_options_str = '\n'.join(html_select_options)

        html_content = """
        <br/>
        AwesomeTTS
        <br/>
        <style>
        .atts-common {
        font-size: 50px;  
        margin-bottom: 10px;
        }

        .atts-text-input {
        border: 2px solid red;
        border-radius: 4px;  
        }
        .atts-text-input:focus {
            background-color: lightblue;
        }

        .atts-presets {
        font-size: 20px;
        }

        .atts-say-button {
            -webkit-appearance: none;
            font-size: 60px;
            background-color: #4CAF50;
            border-radius: 12px;
        }       
        .atts-say-button-label {
            font-size: 50px;
        } 
        </style>
        <input id='speech-input' class="atts-common atts-text-input">
        <br/>
        <select name='preset' id='preset' class='atts-common atts-presets'>
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
        """

        content.stats += html_content

    return on_deckbrowser_will_render_content



