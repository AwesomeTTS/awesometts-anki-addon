# AwesomeTTS Anki add-on

AwesomeTTS makes it easy for language-learners and other students to add
speech to their personal [Anki](https://apps.ankiweb.net) card decks.

Once loaded into the Anki `addons` directory, the AwesomeTTS add-on code
enables both on-demand playback and recording functionality.


## License

AwesomeTTS is free and open-source software. The add-on code that runs within
Anki is released under the [GNU GPL v3](LICENSE.txt).

## Polly version install instruction

1. Install Anki **2.1**
2. Download awesometts-anki-addon from this repository and install using standard install.sh file 
3. There are two ways to setup you AWS credentials: you can write them into config file as described [here](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration) or just input them into special fields after start AwesomeTTS and choose Amazon Polly service.
4. Run Anki using standart executable file and check Amazon service.