void (function () {
    return new Promise<void>((_, reject) => setTimeout(() => reject(new Error('I am an error')), 0)).catch((_err) => {
        process.exit(1);
    });
})();
