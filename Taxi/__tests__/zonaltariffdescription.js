import {getCallCenter} from '../zonaltariffdescription';

describe('zonaltariffdescription', () => {
    describe('getCallCenter', () => {
        it('Должен вернуть undefined, если нет контактов', () => {
            expect(getCallCenter({contact_options: {call_centers: []}})).toEqual(undefined);
            expect(getCallCenter({})).toEqual(undefined);
        });

        it('Должен вернуть локальный номер, если он есть', () => {
            expect(
                getCallCenter({
                    contact_options: {
                        call_centers: [
                            {phone: '+79991112233', formatted_phone: '+7 (999) 111-22-33', type: 'local'},
                            {phone: '+77777777777', formatted_phone: '+7 (777) 777-77-77', type: 'national'}
                        ]
                    }
                })
            ).toEqual({phone: '+79991112233', formattedPhone: '+7 (999) 111-22-33'});
            expect(
                getCallCenter({
                    contact_options: {
                        call_centers: [
                            {phone: '+77777777777', formatted_phone: '+7 (777) 777-77-77', type: 'national'},
                            {phone: '+79991112233', formatted_phone: '+7 (999) 111-22-33', type: 'local'}
                        ]
                    }
                })
            ).toEqual({phone: '+79991112233', formattedPhone: '+7 (999) 111-22-33'});
        });

        it('Должен вернуть первый номер, если нет локального', () => {
            expect(
                getCallCenter({
                    contact_options: {
                        call_centers: [
                            {phone: '+79991112233', formatted_phone: '+7 (999) 111-22-33', type: 'other'},
                            {phone: '+77777777777', formatted_phone: '+7 (777) 777-77-77', type: 'national'}
                        ]
                    }
                })
            ).toEqual({phone: '+79991112233', formattedPhone: '+7 (999) 111-22-33'});
            expect(
                getCallCenter({
                    contact_options: {
                        call_centers: [
                            {phone: '+77777777777', formatted_phone: '+7 (777) 777-77-77', type: 'national'},
                            {phone: '+79991112233', formatted_phone: '+7 (999) 111-22-33', type: 'other'}
                        ]
                    }
                })
            ).toEqual({phone: '+77777777777', formattedPhone: '+7 (777) 777-77-77'});
        });
    });
});
