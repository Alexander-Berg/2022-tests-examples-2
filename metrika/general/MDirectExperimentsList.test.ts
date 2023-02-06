import { MDirectExperimentsList } from './MDirectExperimentsList';

describe('MDirectExperimentsList', () => {
    it('works with default params', () => {
        const model = MDirectExperimentsList.create();

        expect(model).toMatchSnapshot();
    });

    it('can add new item', () => {
        const model = MDirectExperimentsList.create();

        model.add({
            id: null,
            name: 'эксперимент',
            active: false,
            permission: 'own',
        });

        expect(model).toMatchSnapshot();
    });

    it('can search by experiments', () => {
        const model = MDirectExperimentsList.create({
            experiments: [
                {
                    id: 12345,
                    name: 'Эксперимент',
                },
                {
                    id: 67890,
                    name: 'qweqwe',
                },
            ],
        });

        // by name
        model.changeSearch('  экспер   ');
        expect(model.filteredExperiments).toMatchSnapshot();

        model.changeSearch('QWE');
        expect(model.filteredExperiments).toMatchSnapshot();

        // by id
        model.changeSearch('  34   ');
        expect(model.filteredExperiments).toMatchSnapshot();

        model.changeSearch('  89  ');
        expect(model.filteredExperiments).toMatchSnapshot();
    });
});
