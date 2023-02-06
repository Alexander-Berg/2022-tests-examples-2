import svgInlined from './test.svg?inline';
import svgEncoded from './test.svg?encode';
import pngEncoded from './test.png?encode';
import svgUrl from './test1.svg?link';
import pngUrl from './test1.png?link';
import svgUrl2 from './test1.svg';
import pngUrl2 from './test1.png';

import styleContent0 from './test.styl?inline';
import styleContent1 from './test.css?inline';
import styleUrl0 from './test1.styl?link';
import styleUrl1 from './test1.css?link';
import './test2.styl';
import './test2.css';

import scriptContent from './test.js?inline';
import scriptUrl from './test1.js?link';
import scriptExcluded from './test2.js';
import scriptImported from './test.view.js';

export const style = {
    inline: [
        styleContent0,
        styleContent1
    ],
    link: [
        styleUrl0,
        styleUrl1
    ]
};

export const images = {
    inline: [
        svgInlined
    ],
    encode: [
        svgEncoded,
        pngEncoded
    ],
    link: [
        svgUrl,
        pngUrl
    ],
    link2: [
        svgUrl2,
        pngUrl2
    ]
};

export const scripts = {
    inline: [
        scriptContent
    ],
    link: [
        scriptUrl
    ],
    extracted: [
        scriptExcluded
    ],
    imported: [
        scriptImported
    ]
};
