import aqt
import anki.hooks

def failure(exception, text):
    # don't do anything, can't popup any dialogs
    print(f"* failure: {exception}")


def makeLinkHandler(addon):
    def linkHandler(deckbrowser, url):

        print(f"* linkHandler {url}")

        (cmd, arg) = url.split(":")

        if cmd == "awesomettsplayback":

            callbacks = dict(
                okay=addon.player.preview,
                fail=failure
            )

            text = arg
            awesometts_preset_name = 'Aria Neural'
            preset = addon.config['presets'][awesometts_preset_name]            

            addon.router(
                svc_id=preset['service'],
                text=text,
                options=preset,
                callbacks=callbacks
            )                                


    
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
        <button onclick="return pycmd('awesomettsplayback:' + document.getElementById('speech-input').value)">say</button>
        """

        content.stats += html_content

    return on_deckbrowser_will_render_content



