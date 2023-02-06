import { execView } from '@lib/views/execView';
import { mockReq } from '@lib/views/mockReq';
import { Ads } from '@lib/utils/ads';
import { DistPopup__counters } from '@block/dist-popup/__counters/dist-popup__counters.view';

describe('dist-popup__counters', function() {
    let ads = new Ads({
        Banners: {
            banners: {
                popup: {
                    linknext: '+popup'
                }
            },
            pixelBase: 'https://pixel.base/path/',
            displayed: null
        }
    });

    let reqStatNo = mockReq({
        statEnabled: false
    }, {
        ads
    });

    let reqStatYes = mockReq({
        statEnabled: true
    }, {
        ads
    });

    let yabsPopup = {
        close_counter: 'path.no',
        install_yes: 'install_yes'
    } as Req3DistPopup;

    function getEmptyCounters(): {[key: string]: {type: string; content: string}[]} {
        return {
            show: [],
            no: [],
            yes: [],
            install: []
        };
    }

    function getPathCounter(path?: string) {
        return {
            type: 'path',
            content: path || 'path'
        };
    }
    function geShowCounter() {
        return {
            type: 'show',
            content: 'path.show'
        };
    }
    function getPathNoCounter(path?: string) {
        return {
            type: 'path',
            content: path || 'path.no'
        };
    }
    function getImageCounter(path?: string) {
        return {
            type: 'image',
            content: path || 'path'
        };
    }

    /* export */
    function getExportCounters() {
        let counters = getEmptyCounters();

        counters.no.push(getPathNoCounter());
        counters.show.push(geShowCounter());

        return counters;
    }

    /* yabs */
    function getYabsCounters() {
        let counters = getEmptyCounters();

        counters.no.push(getImageCounter(yabsPopup.close_counter));
        counters.yes.push(getImageCounter(yabsPopup.install_yes));
        counters.show.push(getImageCounter(ads.getShowUrl('popup')));

        return counters;
    }

    function getYabsAndMordaCounters() {
        let counters = getExportCounters();

        counters.no.push(getImageCounter(yabsPopup.close_counter));
        counters.yes.push(getImageCounter(yabsPopup.install_yes));
        counters.show.push(getImageCounter(ads.getShowUrl('popup')));

        return counters;
    }

    function getExportCountersWithInline() {
        let counters = getExportCounters();

        counters.yes.push(getPathCounter('path.yes'));

        return counters;
    }

    describe('yabs', function() {
        it('morda stat is off', function() {
            expect(execView(DistPopup__counters, {
                statPath: '',
                flags: {
                    isInnerAction: false,
                    source: 'yabs'
                },
                popup: yabsPopup
            }, reqStatNo)).toEqual(getYabsCounters());
        });
        it('morda stat is on', function() {
            expect(execView(DistPopup__counters, {
                statPath: 'path',
                flags: {
                    isInnerAction: false,
                    source: 'yabs'
                },
                popup: yabsPopup
            }, reqStatYes)).toEqual(getYabsAndMordaCounters());
        });
    });

    describe('madm export', function() {
        it('stat is off', function() {
            expect(execView(DistPopup__counters, {
                statPath: '',
                flags: {
                    source: 'export',
                    isInnerAction: false
                },
                popup: yabsPopup
            }, reqStatNo)).toEqual(getEmptyCounters());
        });
        it('stat is on', function() {
            expect(execView(DistPopup__counters, {
                statPath: 'path',
                flags: {
                    source: 'export',
                    isInnerAction: false
                },
                popup: yabsPopup
            }, reqStatYes)).toEqual(getExportCounters());
        });
        it('stat is on, isInnerAction=true', function() {
            expect(execView(DistPopup__counters, {
                statPath: 'path',
                flags: {
                    source: 'export',
                    isInnerAction: true
                },
                popup: yabsPopup
            }, reqStatYes)).toEqual(getExportCountersWithInline());
        });
    });
});
