/*
 * AwesomeTTS text-to-speech add-on for Anki
 * Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * Really simple JScript gateway for talking to the Microsoft Speech API.
 *
 * cscript sapi5js.js voice-list
 * cscript sapi5js.js speech-output <output_path> <rate> <volume> <quality>
 *                                  <flags> <voice_in_hex> <phrase_in_hex>
 */

/*globals WScript*/


var argv = WScript.arguments;

if (typeof argv !== 'object') {
    throw new Error("Unable to read from the arguments list");
}


var argc = argv.count();

if (typeof argc !== 'number' || argc < 1) {
    throw new Error("Expecting the command to execute");
}


var command = argv.item(0);
var options = {};

if (command === 'voice-list') {
    if (argc > 1) {
        throw new Error("Unexpected extra arguments for voice-list");
    }
} else if (command === 'speech-output') {
    if (argc !== 8) {
        throw new Error("Expecting exactly 7 arguments for speech-output");
    }

    var getWavePath = function (path) {
        if (path.length < 5 || !/\.wav$/i.test(path)) {
            throw new Error("Expecting a path ending in .wav");
        }

        return path;
    };

    var getInteger = function (str, lower, upper, what) {
        if (!/^-?\d{1,3}$/.test(str)) {
            throw new Error("Expected an integer for " + what);
        }

        var value = parseInt(str, 10);

        if (value < lower || value > upper) {
            throw new Error("Value for " + what + " out of range");
        }

        return value;
    };

    var getUnicodeFromHex = function (hex, what) {
        if (typeof hex !== 'string' || hex.length < 4 || hex.length % 4 !== 0) {
            throw new Error("Expected quad-chunked hex string for " + what);
        }

        var i;
        var unicode = [];

        for (i = 0; i < hex.length; i += 4) {
            unicode.push(parseInt(hex.substr(i, 4), 16));
        }

        return String.fromCharCode.apply('', unicode);
    };

    // See also sapi5js.py when adjusting any of these
    options.file = getWavePath(argv.item(1));
    options.rate = getInteger(argv.item(2), -10, 10, "rate");
    options.volume = getInteger(argv.item(3), 1, 100, "volume");
    options.quality = getInteger(argv.item(4), 4, 39, "quality");
    options.flags = getInteger(argv.item(5), 0, 16, "flags");
    options.voice = getUnicodeFromHex(argv.item(6), "voice");
    options.phrase = getUnicodeFromHex(argv.item(7), "phrase");
} else {
    throw new Error("Unrecognized command sent");
}


var sapi = WScript.createObject('SAPI.SpVoice');

if (typeof sapi !== 'object') {
    throw new Error("SAPI does not seem to be available");
}


var voices = sapi.getVoices();

if (typeof voices !== 'object') {
    throw new Error("Voice retrieval does not seem to be available");
}

if (typeof voices.count !== 'number' || voices.count < 1) {
    throw new Error("There does not seem to be any voices installed");
}


var i;

if (command === 'voice-list') {
    WScript.echo('__AWESOMETTS_VOICE_LIST__');

    var getHexFromUnicode = function (unicode) {
        if (typeof unicode !== 'string' || !unicode.length) { return ''; }

        var i = 0;
        var chunk;
        var hex = [];

        for (i = 0; i < unicode.length; ++i) {
            chunk = unicode.charCodeAt(i).toString(16);
            switch (chunk.length) {
                case 4:  break;
                case 3:  chunk = '0' + chunk;   break;
                case 2:  chunk = '00' + chunk;  break;
                case 1:  chunk = '000' + chunk; break;
                default: throw new Error("Bad chunk from toString(16) call");
            }

            hex.push(chunk);
        }

        return hex.join('');
    };

    for (i = 0; i < voices.count; ++i) {
        var name;
        try { name = voices.item(i).getAttribute('name'); }
        catch (e) { }

        var language;
        try { language = voices.item(i).getAttribute('language'); }
        catch (e) { }

        if (typeof name == 'string' && name.length > 0) {
          WScript.echo(
              getHexFromUnicode(name) + ' ' +
              (
                  language && getHexFromUnicode(language) ||
                  getHexFromUnicode('unknown')
              )
          );
        }
    }
} else if (command === 'speech-output') {
    var found = false;
    var voice;

    for (i = 0; i < voices.count; ++i) {
        voice = voices.item(i);

        if (voice.getAttribute('name') === options.voice) {
            found = true;
            sapi.voice = voice;
            break;
        }
    }

    if (!found) {
        throw new Error("Could not find the specified voice.");
    }

    var audioOutputStream = WScript.createObject('SAPI.SpFileStream');

    if (typeof audioOutputStream !== 'object') {
        throw new Error("Unable to create an output file");
    }

    audioOutputStream.format.type = options.quality;
    audioOutputStream.open(options.file, 3 /* SSFMCreateForWrite */);

    sapi.audioOutputStream = audioOutputStream;
    sapi.rate = options.rate;
    sapi.volume = options.volume;

    if (options.flags) {
      sapi.speak(options.phrase, options.flags);
    } else {
      sapi.speak(options.phrase);
    }
}
