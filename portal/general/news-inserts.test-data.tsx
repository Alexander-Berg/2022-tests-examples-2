/* eslint-disable @typescript-eslint/ban-ts-comment */
import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
// @ts-ignore
import { NewsInserts } from '@block/news-inserts/news-inserts.view';
import reqTopnews from './mocks/reqTopnews.json';
import reqStocks from './mocks/reqStocks.json';

const newsInsertsReqWithStocks = mockReq({ isClient: true }, Object.assign({}, reqTopnews, reqStocks));
const newsInsertsReqWithoutStocks = mockReq({ isClient: true }, reqTopnews);

enum Size {
   small = 'small',
   normal = 'normal',
   big = 'big'
}

const width = {
    [Size.small]: '728px',
    [Size.normal]: '856px',
    [Size.big]: '1024px'
};
const classes = {
    [Size.small]: 'b-page_width_normal b-page_tablo_normal',
    [Size.normal]: 'b-page_width_wide b-page_tablo_normal',
    [Size.big]: 'b-page_width_wide b-page_hd_yes'
};

const createNewsNoZen = (size: Size, issReqWithStocks?: boolean) => {
    return function() {
        return (
         <div>
            <style>
               {`
                  body {background-color: antiquewhite;}
                  .b-page {
                     width: ${width[size]};
                     margin: 0 auto;
                  }
               `}
            </style>
            <div class={`b-page b-page_tablo2021_yes b-page_zen_no b-page_topnews_yes b-page_visible_yes ${classes[size]} fonts-loaded`}>
               <div class="news-no-zen">
                  {execView(NewsInserts, {}, issReqWithStocks ? newsInsertsReqWithStocks : newsInsertsReqWithoutStocks)}
               </div>
            </div>
         </div>
        );
    };
};
export const smallNewsNoZen = createNewsNoZen(Size.small);
export const normalNewsNoZen = createNewsNoZen(Size.normal);
export const bigNewsNoZen = createNewsNoZen(Size.big);
export const newsNoZenWithStocks = createNewsNoZen(Size.big, true);

const createNewsInZen = (size: Size) => {
    return function() {
        return (
      <div>
            <style>
               {`
                  body {background-color: antiquewhite;}
                  .placeholder-card {
                     height: 490px;
                     margin: 0 auto;
                  }
                  ._size_big {width: 610px;}
                  ._size_small {width: 290px;}
               `}
            </style>
            <div class={`b-page b-page_tablo2021_yes b-page_zen_yes b-page_topnews_yes b-page_visible_yes ${classes[size]} fonts-loaded`}>
               <div class={`placeholder-card _size_${size}`}>
                     {execView(NewsInserts, {}, newsInsertsReqWithStocks)}
               </div>
            </div>
      </div>
        );
    };
};

export const smallNewsInZen = createNewsInZen(Size.small);
export const bigNewsInZen = createNewsInZen(Size.big);
