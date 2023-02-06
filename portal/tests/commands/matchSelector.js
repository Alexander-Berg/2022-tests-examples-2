module.exports = async function matchSelector(elem, selector) {
    const className = (await elem.getAttribute('class')).split(/\s+/);
    const tokens = selector.split(/\s+/);
    const last = tokens.pop();

    names = last.replace(/\./g, ' ').split(' ');

    return names.every(item => className.includes(item));
};
