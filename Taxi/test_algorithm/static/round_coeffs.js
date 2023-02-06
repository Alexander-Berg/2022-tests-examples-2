function stage(precision, value) {
    const factor = Math.pow(10, precision);
    return {value: Math.round(value * factor) / factor};
}