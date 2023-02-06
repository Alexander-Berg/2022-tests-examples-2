import BannerRefresh from '../banner-refresh';
import { clearUsedBanners } from '../banner-refresh';

describe('banner-refresh', function() {
    describe('skip-banner', function() {
        const params = {
            node: document.body,
            autoRefreshCheck: () => false
        };

        afterEach(() => {
            clearUsedBanners();
        });
        it('Добавляет переданные при создании баннеры', function() {
            let instance = new BannerRefresh({
                ...params,
                skip: ['1234', '5678']
            });

            expect(instance._getUsedBanners()).toEqual(['1234', '5678']);
        });

        it('Обрезает список баннеров до 10', function() {
            let instance = new BannerRefresh({
                ...params,
                skip: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
            });
            expect(instance._getUsedBanners()).toEqual(['3', '4', '5', '6', '7', '8', '9', '10', '11', '12']);
        });

        it('Обрезает список баннеров до 10 последних после добавления руками', function() {
            let instance = new BannerRefresh({
                ...params,
                skip: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
            });

            instance.updateUsedBanners('11');

            expect(instance._getUsedBanners()).toEqual(['2', '3', '4', '5', '6', '7', '8', '9', '10', '11']);

            instance.updateUsedBanners(['12', '13']);

            expect(instance._getUsedBanners()).toEqual(['4', '5', '6', '7', '8', '9', '10', '11', '12', '13']);

            instance.updateUsedBanners(['2', '3']);

            expect(instance._getUsedBanners()).toEqual(['6', '7', '8', '9', '10', '11', '12', '13', '2', '3']);
        });
    });
});
