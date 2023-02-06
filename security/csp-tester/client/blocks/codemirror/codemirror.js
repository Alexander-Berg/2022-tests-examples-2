/* borschik:include:../../../node_modules/codemirror/lib/codemirror.js */
/* borschik:include:../../../node_modules/codemirror/mode/javascript/javascript.js */
/* borschik:include:../../../node_modules/codemirror/addon/mode/simple.js */

/* Definition of Content Security Policy mode
 */
CodeMirror.defineSimpleMode("csp", {
  start: [
    {regex: /'(unsafe-inline|self|unsafe-eval|none)'/, token: "atom"},
    {regex: /'nonce-[a-zA-Z0-9+/-]+[=]{0,2}'/, token: "atom"},
    {regex: /'(sha256|sha384|sha512)-[a-zA-Z0-9+/]+[=]{0,2}'/, token: "atom"},
    {regex: /(?:default-src|script-src|base-uri|child-src|connect-src|default-src|font-src|form-action|frame-ancestors|frame-src|img-src|media-src|object-src|plugin-types|report-uri|sandbox|script-src|style-src)\b/, token: "keyword"},
  ]
});
