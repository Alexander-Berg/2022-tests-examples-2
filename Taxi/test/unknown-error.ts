void (function () {
    return new Promise<void>((_, reject) => {
        setTimeout(() => {
            reject('some unknown error :(');
        }, 1_000);
    });
})();
