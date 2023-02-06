import profileData from './data/employees.json';
import dayjs, {Dayjs} from 'dayjs';

describe('Раздел сотрудники', () => {
    const wfmUser = 'autotest-profile';

    function addShedulle() {
        cy.addSchedule(
            wfmUser,
            profileData.data_row_key,
            profileData.schedule_date_from,
            profileData.schedule_date_to,
            profileData.schedule_alias_id,
            true
        );
    }
    function addAbsences() {
        cy.addAbsences(
            wfmUser,
            profileData.data_row_key,
            profileData.absences.start,
            profileData.absences.type,
            profileData.absences.duration_minutes
        );
    }

    before(() => {
        cy.removeAllSchedules(wfmUser, profileData.data_row_key);
        addShedulle();
    });
    beforeEach(() => {
        cy.yandexLogin(wfmUser);
        cy.visit('/employees');
    });

    it('Загрузка таблицы с сотрудниками', () => {
        cy.intercept('post', 'v2/operators/values', {
            limit: '10',
            offset: '0',
            fixture: 'responses/employees/employees.json'
        }).as('valuesOperators');

        cy.get('[data-cy=employees-table-fullname-cell]', {timeout: 10000}).should(
            'contain.text',
            profileData.operator_name
        );
    });

    it('Выбираем сотрудника и смотрим данные в таблице', () => {
        cy.get('[data-cy=employees-filter-fullname]').type(profileData.operator_name);

        cy.intercept('post', 'v2/operators/values', {
            full_name: profileData.operator_name,
            limit: '10',
            offset: '0',
            fixture: 'responses/employees/employees-filters.json'
        });

        cy.get('[data-cy="employees-table-fullname-cell"]', {timeout: 10000}).should(
            'contain.text',
            profileData.operator_name
        );
        cy.get('.ant-table-row > :nth-child(4)', {timeout: 10000}).should(
            'contain.text',
            profileData.callcenter
        );
        cy.get(':nth-child(5) > :nth-child(1) > p', {timeout: 10000}).should(
            'contain.text',
            profileData.schedule_alias
        );
        cy.get(':nth-child(5) > :nth-child(1) > .ant-row', {timeout: 10000}).should(
            'contain.text',
            dayjs(profileData.schedule_date_from).format('DD.MM.YY') +
                ' - ' +
                dayjs(profileData.schedule_date_to).format('DD.MM.YY')
        );
        cy.get('.ant-row > .anticon > svg > path', {timeout: 10000}).should(
            'have.css',
            'color',
            'rgb(82, 196, 26)'
        );
        cy.get('.ant-table-row > :nth-child(6)', {timeout: 10000}).should(
            'contain.text',
            profileData.skills.lavka
        );
        cy.get('.ant-table-row > :nth-child(7)', {timeout: 10000}).should(
            'contain.text',
            profileData.supervisor_name
        );
        cy.get('.ant-table-row > :nth-child(8)', {timeout: 10000}).should(
            'contain.text',
            profileData.mentor_name
        );
        cy.get('.ant-table-row > :nth-child(9)', {timeout: 10000}).should(
            'contain.text',
            profileData.phone
        );
        cy.get('.ant-table-row > :nth-child(9)', {timeout: 10000}).should(
            'contain.text',
            profileData.telegram
        );
        cy.get('.current', {timeout: 10000}).should('contain.text', 1);
    });

    it('Фильтрация по ФИО', () => {
        cy.get('[data-cy=employees-filter-fullname]').type(profileData.operator_name);
        cy.get('[data-cy="employees-table-fullname-cell"]', {timeout: 10000}).should(
            'contain.text',
            profileData.operator_name
        );
    });

    it('Фильтрация по Куратору', () => {
        cy.get('[data-cy=employees-filter-supervisors]').type(
            profileData.supervisor_name + '{enter}'
        );
        cy.get('[data-cy="employees-table-fullname-cell"]', {timeout: 10000}).should(
            'contain.text',
            profileData.operator_name
        );
        cy.get('.ant-table-row > :nth-child(7)', {timeout: 10000}).should(
            'contain.text',
            profileData.supervisor_name
        );
    });

    it('Фильтрация по Колл-центру', () => {
        cy.get('[data-cy=employees-filter-departments]').type(profileData.callcenter + '{enter}');
        cy.get('.ant-table-row > :nth-child(4)', {timeout: 10000})
            .first()
            .should('contain.text', profileData.callcenter);
    });

    it('Фильтрация по Графику', () => {
        cy.get('[data-cy=employees-filter-schedules]').type(profileData.schedule_alias + '{enter}');
        cy.get('.ant-table-row > :nth-child(5)', {timeout: 10000}).should(
            'contain.text',
            profileData.schedule_alias
        );
    });

    it('Фильтрация по Навыку', () => {
        cy.get('[data-cy=employees-filter-skills]').type(profileData.skills.lavka + '{enter}');
        cy.get('.ant-table-row > :nth-child(6)', {timeout: 10000})
            .first()
            .should('contain.text', profileData.skills.lavka);
    });

    it('Просмотр карточки сотрудника', () => {
        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('.ant-typography', {timeout: 10000}).should(
            'contain.text',
            profileData.operator_name
        );
        cy.get('.ant-typography').should('contain.text', profileData.data_row_key);
        cy.get(':nth-child(1) > .ant-space').should('contain.text', profileData.phone);
        cy.get(':nth-child(2) > .ant-space').should('contain.text', profileData.telegram);
        cy.get(':nth-child(1) > .ant-col-18').should('contain.text', profileData.login);
        cy.get(':nth-child(2) > .ant-col-18').should('contain.text', profileData.supervisor_name);
        cy.get(':nth-child(3) > .ant-col-18').should('contain.text', profileData.mentor_name);
        cy.get(':nth-child(4) > .ant-col-18').should('contain.text', profileData.status);
        cy.get(':nth-child(5) > .ant-col-18').should('contain.text', profileData.tags.tag1);
        cy.get(':nth-child(5) > .ant-col-18').should('contain.text', profileData.tags.tag2);
        cy.get(':nth-child(1) > .ant-col-14').should('contain.text', profileData.callcenter);
        cy.get(':nth-child(2) > .ant-col-14').should('contain.text', profileData.schedule_alias);
        cy.get(':nth-child(3) > .ant-col-14').should('contain.text', profileData.skills.lavka);
        cy.get(':nth-child(4) > .ant-col-14').should('contain.text', profileData.employment_date);
    });

    it('Добавление тега (' + profileData.tags.tag3 + ')', () => {
        cy.addTags(wfmUser, profileData.data_row_key);
        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);
        cy.wait(2000);
        cy.get('.ant-typography > .anticon > svg', {timeout: 10000}).click();
        cy.get(
            '.ant-typography > .ant-select > .ant-select-selector > .ant-select-selection-overflow'
        )
            .click()
            .type(profileData.tags.tag3 + '{enter}');
        cy.get('.ant-typography > .ant-select > .ant-select-arrow > .anticon > svg').click();
        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);
        cy.wait(2000);
        cy.get(':nth-child(5) > .ant-col-18').should('contain.text', profileData.tags.tag3);
    });

    it('Добавление графика (' + profileData.schedule_alias + ')', () => {
        cy.removeAllSchedules(wfmUser, profileData.data_row_key);

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-add]', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-skills-picker]', {timeout: 10000})
            .click()
            .type(profileData.skills.lavka + '{enter}');
        cy.get(
            '[data-cy=component-apply-schedule-form-schedule-picker] > .ant-select-selector'
        ).click();
        cy.get(
            '[data-cy=component-apply-schedule-form-schedule-picker] > .ant-select-selector'
        ).type(profileData.schedule_alias + '{enter}');
        cy.get(
            ':nth-child(1) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        )
            .click()
            .type(dayjs(profileData.schedule_date_from).format('DD.MM.YY') + '{enter}');
        cy.get(
            ':nth-child(3) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        )
            .click()
            .type(dayjs(profileData.schedule_date_to).format('DD.MM.YY') + '{enter}');
        cy.get('[data-cy=component-apply-schedule-form-save]').click();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-schedule-picker]', {timeout: 10000}).should(
            'contain.text',
            profileData.schedule_alias
        );
        cy.get(
            ':nth-child(1) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]',
            {timeout: 10000}
        ).should('have.value', dayjs(profileData.schedule_date_from).format('DD.MM.YY'));
        cy.get(
            ':nth-child(3) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        ).should('have.value', dayjs(profileData.schedule_date_to).format('DD.MM.YY'));
    });

    it('Добавление графика (' + profileData.schedule_alias + ' без конечного периода)', () => {
        cy.removeAllSchedules(wfmUser, profileData.data_row_key);

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-add]', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-skills-picker]', {timeout: 10000})
            .click()
            .type(profileData.skills.lavka + '{enter}');
        cy.get(
            '[data-cy=component-apply-schedule-form-schedule-picker] > .ant-select-selector'
        ).click();
        cy.get(
            '[data-cy=component-apply-schedule-form-schedule-picker] > .ant-select-selector'
        ).type(profileData.schedule_alias + '{enter}');
        cy.get(
            ':nth-child(1) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        )
            .click()
            .type(dayjs(profileData.schedule_date_from).format('DD.MM.YY') + '{enter}');
        cy.get('[data-cy=component-apply-schedule-form-save]').click();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-schedule-picker]', {timeout: 10000}).should(
            'contain.text',
            profileData.schedule_alias
        );
        cy.get(
            ':nth-child(1) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]',
            {timeout: 10000}
        ).should('have.value', dayjs(profileData.schedule_date_from).format('DD.MM.YY'));
        cy.get(
            ':nth-child(3) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        ).should('not.have.value');
    });

    it('Редактирование графика (' + profileData.schedule_alias + ')', () => {
        cy.removeAllSchedules(wfmUser, profileData.data_row_key);
        addShedulle();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-skills-picker]', {timeout: 10000})
            .click()
            .type(profileData.skills.order + '{enter}');
        cy.get(
            '[data-cy=component-apply-schedule-form-schedule-picker] > .ant-select-selector'
        ).click();
        cy.get(
            '[data-cy=component-apply-schedule-form-schedule-picker] > .ant-select-selector'
        ).type(profileData.schedule_alias_rn + '{enter}');
        cy.get(
            ':nth-child(1) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        )
            .click()
            .clear()
            .type(dayjs(profileData.schedule_date_from_rn).format('DD.MM.YY') + '{enter}');
        cy.get(
            ':nth-child(3) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        )
            .click()
            .clear()
            .type(dayjs(profileData.schedule_date_to_rn).format('DD.MM.YY') + '{enter}');
        cy.get('[data-cy=component-apply-schedule-form-save]').click();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-schedule-picker]', {timeout: 10000}).should(
            'contain.text',
            profileData.schedule_alias_rn
        );
        cy.get(
            ':nth-child(1) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]',
            {timeout: 10000}
        ).should('have.value', dayjs(profileData.schedule_date_from_rn).format('DD.MM.YY'));
        cy.get(
            ':nth-child(3) > .ant-picker > .ant-picker-input > [data-cy=component-apply-schedule-form-date-picker]'
        ).should('have.value', dayjs(profileData.schedule_date_to_rn).format('DD.MM.YY'));
    });

    it('Удаление графика (' + profileData.schedule_alias + ')', () => {
        cy.removeAllSchedules(wfmUser, profileData.data_row_key);
        addShedulle();
        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);
        cy.get('#rc-tabs-0-tab-schedules', {timeout: 10000}).click();
        cy.get('[data-cy=component-apply-schedule-form-remove]').click();
        cy.get('[data-cy=component-apply-schedule-form-schedule-picker]', {timeout: 10000}).should(
            'not.exist'
        );
    });

    it('Добавление Отсутствия ', () => {
        cy.removeAllAbsences(wfmUser, profileData.data_row_key);

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-absences', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-add]', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-type-picker] > .ant-select-selector').click();

        cy.get(`[label='${profileData.absences.name}']`).click();

        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="С"]', {
                timeout: 10000
            })
            .click()
            .type(profileData.absences.date_start_gui + '{enter}');
        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="По"]', {
                timeout: 10000
            })
            .click()
            .type(profileData.absences.date_end_gui + '{enter}');
        cy.get('[data-cy=component-absence-types-form-comment-btn] > .anticon > svg').click();
        cy.get('[data-cy=component-absence-types-form-comment-input]').type(
            profileData.absences.comment
        );
        cy.get('[data-cy=component-absence-types-form-save]').click();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-absences', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-type-picker]', {
            timeout: 10000
        }).should('contain.text', profileData.absences.name);

        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="С"]', {
                timeout: 10000
            })
            .should('have.value', profileData.absences.date_start_gui);

        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="По"]', {
                timeout: 10000
            })
            .should('have.value', profileData.absences.date_end_gui);
        cy.get('[data-cy=component-absence-types-form-comment-btn] > .anticon > svg').click();
        cy.get('[data-cy=component-absence-types-form-comment-input]').should(
            'have.value',
            profileData.absences.comment
        );
    });

    it('Редактирование Отсутствия ', () => {
        cy.removeAllAbsences(wfmUser, profileData.data_row_key);
        addAbsences();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-absences', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-type-picker] > .ant-select-selector').click();
        cy.get(`[label='${profileData.absences.rm_name}']`).click();

        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="С"]', {
                timeout: 10000
            })
            .click()
            .clear()
            .type(profileData.absences.rm_date_start_gui + '{enter}');
        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="По"]', {
                timeout: 10000
            })
            .click()
            .clear()
            .type(profileData.absences.rm_date_end_gui + '{enter}');
        cy.get('[data-cy=component-absence-types-form-comment-btn] > .anticon > svg').click();
        cy.get('[data-cy=component-absence-types-form-comment-input]')
            .clear()
            .type(profileData.absences.comment + '_rn');
        cy.get('[data-cy=component-absence-types-form-save]').click();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-absences', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-type-picker]', {
            timeout: 10000
        }).should('contain.text', profileData.absences.rm_name);

        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="С"]', {
                timeout: 10000
            })
            .should('have.value', profileData.absences.rm_date_start_gui);

        cy.get('[data-cy=component-absence-types-form-datepicker]')
            .find('[placeholder="По"]', {
                timeout: 10000
            })
            .should('have.value', profileData.absences.rm_date_end_gui);
        cy.get('[data-cy=component-absence-types-form-comment-btn] > .anticon > svg').click();
        cy.get('[data-cy=component-absence-types-form-comment-input]').should(
            'have.value',
            profileData.absences.comment + '_rn'
        );
    });

    it('Удаление Отсутствия', () => {
        cy.removeAllAbsences(wfmUser, profileData.data_row_key);
        addAbsences();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-absences', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-type-picker]', {timeout: 10000}).should(
            'exist'
        );
        cy.get('[data-cy=component-absence-types-form-datepicker]', {timeout: 10000}).should(
            'exist'
        );
        cy.get('[data-cy=component-absence-types-form-remove]', {timeout: 10000}).click();

        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        cy.get('#rc-tabs-0-tab-absences', {timeout: 10000}).click();
        cy.get('[data-cy=component-absence-types-form-type-picker]').should('not.exist');
        cy.get('[data-cy=component-absence-types-form-datepicker]').should('not.exist');
    });

    it('Просмотр смены', () => {
        cy.visit(`/employees?schedule_fixed=any&cardEmployeeId=${profileData.data_row_key}`);

        var backEndDateTo = dayjs(profileData.shift_date_to).add(1, 'day').format('YYYY-MM-DD');

        cy.intercept(
            'GET',
            `v1/operators/timetable/values?datetime_from=${profileData.shift_date_from}T00%3A00%3A00%2B03%3A00&datetime_to=${backEndDateTo}T00%3A00%3A00%2B03%3A00&yandex_uid=${profileData.data_row_key}`,
            {
                fixture: 'responses/employees/job_setup.json'
            }
        ).as('shifthValues');
        cy.get(':nth-child(1) > .ant-picker > .ant-picker-input-active > input')
            .click()
            .clear()
            .type(dayjs(profileData.shift_date_from).format('DD.MM.YY'));
        cy.get(':nth-child(1) > .ant-picker > :nth-child(3) > input')
            .click()
            .clear()
            .type(dayjs(profileData.shift_date_to).format('DD.MM.YY') + '{enter}');
        cy.get('.ant-col-4 > .ant-btn').contains('Загрузить').click();
        cy.wait('@shifthValues');
        cy.get('.skill-column').contains(profileData.skills.lavka);
        cy.get('.item', {timeout: 10000}).contains(profileData.shift_time);
    });
});
