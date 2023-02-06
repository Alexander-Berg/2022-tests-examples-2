INCLUDE("result/some.ru.view.js");
INCLUDE("result/some.uk.view.js");

WATCH("lang.json", "command");
// Source views
WATCH("blocks/test/test.view.js", "command");
// INCLUDE and RAWINC files
WATCH("blocks/test/test2.js", "command");
