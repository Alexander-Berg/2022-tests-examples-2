void (function () {
    return new Promise<void>((resolve) => setTimeout(() => resolve(), 0)).then(() => {
        process.exit(0);
    });
})();
