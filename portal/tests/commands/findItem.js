module.exports = async function findItem(items, text) {
    for (let item of items) {
        const itemText = await item.getText();
        if (itemText.includes(text)) {
            return item;
        }
    }
    throw new Error(`Не найден элемент, содержащий "${text}"`);
};
