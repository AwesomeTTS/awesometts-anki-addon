import aqt
import anki.hooks


def makeLinkHandler(addon):
    def linkHandler(deckbrowser, url):
        print(f"* linkHandler {url}")
    
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



