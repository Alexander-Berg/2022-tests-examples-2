const mockData = {
    props: {
        dispatch: jest.fn()
    },
    getState: () => ({
        settings: {
            language: 'ru',
            uatraits: {
                isMobile: false,
                isTouch: false
            }
        },
        common: {
            csrf: '12345',
            track_id: '1234',
            from: 'mail'
        },
        form: {
            values: {
                name: 'test',
                lastname: 'example',
                email: 'test@example.com',
                login: '',
                password: ''
            },
            states: {
                name: 'valid',
                lastname: 'valid',
                email: 'valid'
            },
            errors: {
                active: 'firstname'
            }
        }
    })
};

export default mockData;
