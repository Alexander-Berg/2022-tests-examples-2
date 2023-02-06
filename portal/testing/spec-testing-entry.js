/* global __INJECTED_LEVEL_PATH__ */
function importAll (r) {
    r.keys().forEach(r);
}
importAll(require.context(__INJECTED_LEVEL_PATH__, true, /\.spec\.js$/));
