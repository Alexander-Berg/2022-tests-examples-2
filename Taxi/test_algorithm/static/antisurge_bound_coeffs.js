function stage(category, value) {
    const kDefaultSurgeValue = 1.0;
    return {value: Math.max(value, kDefaultSurgeValue)};
}