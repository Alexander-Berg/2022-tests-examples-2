const reportPresets = require('./presets.json');
import { createPresetsMenu, mapPresets } from '..';

describe('menu structure', () => {
    it('should transform report prestets array to menu structure', () => {
        const result = createPresetsMenu(reportPresets);
        expect(result).toEqual([
            { name: 'traffic', title: 'Дни' },
            { name: 'sites', title: 'Площадки' },
            { name: 'placements', title: 'Размещения' },
            { name: 'fraud', title: 'Фрод' },
            { name: 'video', title: 'Видеореклама' },
            {
                name: 'audience',
                title: 'Аудитория',
                chlds: [
                    { name: 'geo', title: 'География' },
                    { name: 'gender', title: 'Пол' },
                    { name: 'age', title: 'Возраст' },
                    { name: 'interests', title: 'Интересы' },
                    { name: 'device_type', title: 'Устройства' },
                ],
            },
        ]);
    });
});

describe('presets meta', () => {
    it('should create presets flat map', () => {
        const result = mapPresets(reportPresets);
        expect(result).toMatchObject({
            traffic: {},
            sites: {},
            placements: {},
            fraud: {},
            video: {},
            geo: {},
            gender: {},
            age: {},
            interests: {},
            device_type: {},
        });
    });
});
