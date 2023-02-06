module.exports = function appendStyles() {
    return this.execute(() => {
        const style = document.createElement('style');
        style.textContent = 'body, main {\n' +
            '    overflow: hidden;\n' +
            '}\n' +
            '*, *:before, *:after {\n' +
            '    transition-duration: 0s !important;\n' +
            '    transition-delay: 0s !important;\n' +
            '    animation-duration: 0s !important;\n' +
            '    animation-delay: 0s !important;\n' +
            '}';

        document.head.appendChild(style);
    });
};
