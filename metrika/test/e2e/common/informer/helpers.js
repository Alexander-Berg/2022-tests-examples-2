/* eslint-disable */
function findScriptFromURL(url, scripts) {
    var script = null;

    for (var i = 0; i < scripts.length; i += 1) {
        if (scripts[i].src === url) {
            script = scripts[i];
        }
    }

    return script;
}
