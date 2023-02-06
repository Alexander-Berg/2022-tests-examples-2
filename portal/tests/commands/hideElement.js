module.exports = function(selector) {
    return this.execute(function(selector) {
        if (typeof selector !== 'string') {
            selector = selector.join(',');
        }
        const elems = document.querySelectorAll(selector);

        for (let i = 0; i < elems.length; ++i) {
            elems[i].style.display = 'none';
        }
    }, selector);
};
