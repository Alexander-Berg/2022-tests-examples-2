/*eslint-disable */
global.views = home.getView();

home.env = {
    devInstance: true
};

home.flags.setDesc('../flags_allowed.json');

home.error = function () {
    var msg = Array.prototype.slice.call(arguments).map(function (item) {
        var obj = {};
        for (var key in Object.getOwnPropertyDescriptors(item)) {
            obj[key] = item[key];
        }
        return JSON.stringify(obj);
    }).join(' -> ');
    console.error(msg);
    throw new Error(msg);
};

/*eslint-enable */
