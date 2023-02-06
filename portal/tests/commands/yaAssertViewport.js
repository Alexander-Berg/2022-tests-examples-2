'use strict';

module.exports = function(name, opts = {}) {
    const rectId = 'rect' + String(Math.random()).substr(3, 6);
    let err;

    return this.execute(function addRect(id, margin) {
        const rect = document.createElement('div');
        const style = rect.style;

        rect.id = id;
        style.position = 'fixed';
        style.top = margin[0] || 0;
        style.right = margin.length > 1 ? margin[1] : margin[0] || 0;
        style.bottom = margin.length > 2 ? margin[2] : style.top;
        style.left = margin.length > 3 ? margin[3] : style.right;

        document.body.appendChild(rect);
    }, rectId, opts.margin || [])
        .then(() => {
            return this.assertView(name, `#${rectId}`, opts).catch(e => {
                err = e;
            });
        })
        .then(() => {
            return this.execute(function rmRect(id) {
                document.body.removeChild(document.getElementById(id));
            }, rectId);
        })
        .then(() => {
            if (err) {
                throw err;
            }
        });
};
