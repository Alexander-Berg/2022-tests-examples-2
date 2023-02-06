/* eslint-env es6 */
const teaserData =
    {
        text: 'Фильмы, мультфильмы и&nbsp;телеканалы на СмартТВ',
        age_restriction: '0+',
        img: {
            height: '180',
            width: '280',
            url: 'https://avatars.mds.yandex.net/get-banana/41024/x25CR8nYVDiJ5FqrXXiCILQLX_banana_20161021_tv-2-1-8.png/optimize'
        }
    };
var wrap = (teaserHtml) => {
    return `
    <style>
        body{
            font-size:6.8px;
            width: 100%;
        }
        .main
        {   font-size:2.2rem;
            padding: 0 280px;
            width: 100%;
            box-sizing: border-box;
        }
        .main__row
        {
            display:flex;
        }
        .news
        {
            width:67%;
        }
    </style>
    <div class="main">
        <div class="main__row">
            <div class="news"></div>
            ${teaserHtml}
        </div>
    </div>`;
};

exports.simple = (execView) => {
    return wrap(execView('TvTeaser', teaserData)
    );
};
