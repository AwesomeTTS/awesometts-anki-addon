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
2. Install Python **3.6**
3. **Install Pip3**
4. Install Boto3 library using Pip3 `sudo pip3 install boto3` 
5. Download awesometts-anki-addon and install using standard install.sh file 
6. Go to ~/.local/share/Anki2/addons21/folder-with-plugin/awesometts/service and open file amazon.py using text editor.
7. There are two string before import boto3 `/usr/lib/python3.6` and `/usr/local/lib/python3.5/dist-packages`. First - path to python3.6 in my case, second - path to pip3 packages in my case. **Change this strings if you have different paths. It's very important**
8. Make sure that AWS credentials was set as described [here](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration) 
9. Run Anki using standart executable file and check Amazon service.