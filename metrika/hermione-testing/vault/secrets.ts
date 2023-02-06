const robotMetrikaTestSecret = {
    secretName: 'robot-metrika-test',
    id: 'sec-01cq6h5rtj649gg8h94zwqshc8',
    version: 'ver-01f8z3028462mxthpb8rtjpeef',
};

function getEnvSecrets() {
    return [
        {
            name: 'BISHOP_OAUTH_TOKEN',
            key: 'bishop-token',
            ...robotMetrikaTestSecret,
        },
        {
            name: 'YAV_OAUTH_TOKEN',
            key: 'yav-token',
            ...robotMetrikaTestSecret,
        },
    ];
}

export {
    getEnvSecrets,
};
