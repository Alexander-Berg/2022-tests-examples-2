/* eslint no-unused-expressions: 0 */
describe('home.ads', function() {
    var Banners = {
        pixelBase: 'https://pixel.base/path/',
        banners: {
            'media': {
                linknext: '+media'
            },
            'popup': {
                linknext: '+popup'
            },
            'teaser': {
                linknext: '+teaser'
            },
            'qwe': {
                linknext: '+qwe'
            },
            'zxc': {
                linknext: '+zxc'
            }
        },
        displayed: {
            'smart-banner': '+smart-banner',
            'asd': '+asd'
        }
    };


    describe('баннеры отключены', function () {
        var ads = new home.Ads({
            Banners: {}
        });

        it('отрицает наличие', function () {
            ads.hasBanner('media').should.equal(false);
        });

        it('не возвращает баннер', function () {
            expect(ads.banner('media')).to.not.exist;
        });

        it('ничего не репортит', function () {
            ads.report().should.equal('');
        });
    });

    describe('есть только awaps', function () {
        var banner = {
                text: 'awaps banner'
            },
            ads = new home.Ads({
                Banners: {
                    banners: {
                        media: banner
                    },
                    pixelBase: null,
                    displayed: null
                }
            });

        it('показывает наличие баннера', function() {
            ads.hasBanner('media').should.equal(true);
        });

        it('отрицает наличие элементов yabs', function() {
            ads.hasBanner('popup').should.equal(false);
        });

        it('возвращает баннер', function () {
            ads.banner('media').should.equal(banner);
        });

        it('не возвращает элементы yabs', function () {
            expect(ads.banner('popup')).to.not.exist;
        });


        it('ничего не репортит', function () {
            ads.report().should.equal('');
        });

    });

    describe('hasBanner', function () {
        var ads;
        beforeEach(function () {
            ads = new home.Ads({
                Banners: Banners
            });
        });

        it('без id', function () {
            ads.hasBanner().should.equal(false);
        });

        it('report', function () {
            ads.hasBanner('report').should.equal(false);
        });

        it('неизвестный id', function () {
            ads.hasBanner('rty').should.equal(false);
        });

        it('известный id', function () {
            ads.hasBanner('qwe').should.equal(true);
        });
    });

    describe('banner', function () {
        var ads;

        beforeEach(function () {
            ads = new home.Ads({
                Banners: Banners
            });
        });

        it('возвращает существующий баннер', function () {
            ads.banner('popup').should.equal(Banners.banners.popup);
        });

        it('не возвращает несуществующий баннер', function () {
            expect(ads.banner('fake-banner')).to.not.exist;
        });

        it('засчитывает показ', function () {
            ads.banner('qwe').should.equal(Banners.banners.qwe);
            ads.banner('media').should.equal(Banners.banners.media);

            ads.report().should.be.a('string')
                .and.include('+qwe')
                .and.include('+media');
        });

        it('не засчитывает показ не показаных баннеров', function () {
            ads.banner('media').should.equal(Banners.banners.media);

            ads.report().should.be.a('string')
                .and.not.include('+qwe')
                .and.not.include('+zxc');
        });

        it('не засчитывает показ баннера типа статпикселя', function () {
            ads = new home.Ads({
                Banners: Banners,
                Banners_awaps: {
                    options: {
                        ad_type: 'stat_pixel'
                    }
                }
            });
            ads.banner('media').should.equal(Banners.banners.media);
            ads.report().should.be.a('string')
                .and.not.include('+media');
        });

    });


    describe('report', function () {
        var report;

        beforeEach(function () {
            var ads = new home.Ads({
                Banners: Banners
            });
            report = ads.report();
        });

        it('репортит показы из перла', function () {
            report.should.be.a('string')
                .and.include(Banners.pixelBase)
                .and.include('+smart-banner')
                .and.include('+asd');
        });

        it('возвращает скрытую картинку', function () {
            report.should.match(/<img.+src="/);
            report.should.include('style="display:none;position:absolute;"');
        });

        it('содержит параметр wmode', function () {
            report.should.match(/\bsrc="[^"]+\?wmode=0\b/);
        });

        it('не репортит пиксель без показов', function () {
            var ads = new home.Ads({
                Banners: {
                    pixelBase: 'https://pixel.base/path/',
                    banners: {
                        'media': {
                            linknext: '+media'
                        }
                    }
                }
            });
            report = ads.report();
            report.should.equal('');
        });

        it('повторный репорт возвращает пустую строчку', function() {
            var ads = new home.Ads({
                Banners: Banners
            });
            ads.report().should.not.be.empty;
            ads.report().should.equal('');
        });
    });

    describe('ручной режим репорта через {report:false} и getShowUrl', function() {
        var ads;

        beforeEach(function () {
            ads = new home.Ads({
                Banners: Banners
            });
        });

        it('не возвращает несуществующий баннер', function() {
            expect(ads.banner('fake-banner', {report: false})).to.not.exist;
        });

        it('getShowUrl возвращает пустую строчку для несуществующего баннера', function() {
            ads.getShowUrl('fake-banner').should.equal('');
        });

        it('не добавляет в report баннер, для которого передан report:false', function () {
            var popup = Banners.banners.popup;

            ads.banner('popup', {report: false}).should.equal(popup);
            ads.report().should.be.a('string')
                .and.not.include(popup.linknext);
        });

        it('возвращает ссылку с показом баннера', function () {
            ads.getShowUrl('popup').should.equal(Banners.pixelBase + Banners.banners.popup.linknext);
        });

        it('getShowUrl возвращает ссылку с показом баннера, вырезая linknext из _displayed', function () {
            var popup = Banners.banners.popup;

            ads.banner('popup');
            ads.getShowUrl('popup').should.equal(Banners.pixelBase + popup.linknext);
            ads.report().should.be.a('string')
                .and.not.include(popup.linknext);
        });

        it('getShowUrl возвращает пустую строку для баннера, linknext которого уже был отгружен через report', function () {
            var popup = Banners.banners.popup;

            ads.banner('popup');
            ads.report().should.be.a('string')
                .and.include(popup.linknext);
            ads.getShowUrl('popup').should.equal('');
        });
    });
});
