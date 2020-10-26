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

        html_content = """
        <br/>
        AwesomeTTS
        <br/>
        <input id='speech-input'><br/>
        <button onclick="return pycmd('awesomettsplayback:' +  btoa(unescape(encodeURIComponent(JSON.stringify({'text': document.getElementById('speech-input').value, 'preset': 'Aria Neural'})))))">say</button>
        """

        content.stats += html_content

    return on_deckbrowser_will_render_content



