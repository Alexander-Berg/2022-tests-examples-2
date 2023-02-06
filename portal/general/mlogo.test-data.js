const drawLogo = req => (execView, {home}) => {
    const getStaticURL = new home.GetStaticURL({
        s3root: 's3/home-static'
    });
    const customReq = {
        JSON: {
            common: {}
        },
        getStaticURL,
        ...req
    };
    const resources = new home.Resources('touch', customReq, execView);
    customReq.resources = resources;

    let html = execView('Mlogo__resources', {}, customReq) +
        execView('Mlogo', {}, customReq);

    return resources.getHTML('head') + html;
};

exports.simple = drawLogo({});

exports.custom = drawLogo({
    Logo: {
        url: 'korolev',
        title: 'Korolev',
        width: 140,
        height: 140
    }
});

exports.customLink = drawLogo({
    Logo: {
        url: 'korolev',
        title: 'Korolev',
        width: 140,
        height: 140,
        href: 'https://ya.ru/'
    }
});

exports.customSize = drawLogo({
    Logo: {
        url: 'korolev',
        title: 'Korolev',
        width: 140,
        height: 40
    }
});

exports.broken = drawLogo({
    Logo: {
        url: 'korolev2',
        title: 'Korolev',
        width: 140,
        height: 140
    }
});
