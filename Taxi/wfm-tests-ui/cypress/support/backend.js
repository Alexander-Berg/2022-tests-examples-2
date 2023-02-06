import profileData from '../integration/e2e/data/employees.json';

const getUserAuth = user => {
    cy.yandexLogin(user);
    return cy
        .request({
            url: '/api/auth',
            headers: {
                Origin: 'https://wfm.taxi.dev.yandex.ru'
            }
        })
        .then(response => {
            const token = response.body.csrf_token;
            const clientId = response.body.client_id;
            return {
                token: token,
                client_id: clientId
            };
        });
};

Cypress.Commands.add(
    'addSchedule',
    (user, yandex_uid, starts_at, expires_at, schedule_type_id, fixed) => {
        getUserAuth(user).then(user => {
            cy.request({
                method: 'POST',
                url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/schedule/type/modify`,
                headers: {
                    'x-csrf-token': user.token,
                    Origin: 'https://wfm.taxi.dev.yandex.ru',
                    'X-WFM-Domain': 'taxi'
                },
                body: {
                    yandex_uid: yandex_uid,
                    starts_at: starts_at,
                    starts_at_with_tz: starts_at + 'T00:00:00 +0300',
                    expires_at: expires_at,
                    expires_at_with_tz: expires_at + 'T00:00:00 +0300',
                    schedule_type_id: schedule_type_id,
                    schedule_fixed: fixed,
                    skills: ['lavka']
                }
            }).then(response => {
                return response.body;
            });
        });
    }
);

Cypress.Commands.add('delSchedule', (user, record_id, revision_id) => {
    getUserAuth(user).then(user => {
        cy.log(revision_id);
        cy.request({
            method: 'DELETE',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/schedule/type/modify`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru'
            },
            body: {
                record_id: record_id,
                revision_id: revision_id
            }
        });
    });
});

Cypress.Commands.add('removeAllSchedules', (user, yandex_uids) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: `https://cc-api.taxi.tst.yandex.ru//v1/operator?yandex_uid=${yandex_uids}`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            }
        }).then(response => {
            Object.keys(response.body.schedules).forEach(schedulesID => {
                const recordID = response.body.schedules[schedulesID].record_id;
                cy.request({
                    method: 'DELETE',
                    url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/schedule/type/modify`,
                    headers: {
                        'x-csrf-token': user.token,
                        Origin: 'https://wfm.taxi.dev.yandex.ru',
                        'X-WFM-Domain': 'taxi'
                    },
                    body: {
                        record_id: recordID
                    }
                });
                cy.wait(500);
            });
        });
    });
});

Cypress.Commands.add('addAbsences', (user, yandex_uid, start, type, duration_minutes) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/operator?yandex_uid=${yandex_uid}`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            }
        }).then(response => {
            cy.request({
                method: 'POST',
                url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/absences/modify`,
                headers: {
                    'x-csrf-token': user.token,
                    Origin: 'https://wfm.taxi.dev.yandex.ru',
                    'X-WFM-Domain': 'taxi'
                },
                body: {
                    absences: [
                        {
                            duration_minutes: duration_minutes,
                            revision_id: response.body.revision_id,
                            start: start,
                            type: type,
                            yandex_uid: yandex_uid
                        }
                    ]
                }
            }).then(response => {
                return response.body;
            });
        });
    });
});

Cypress.Commands.add('removeAllAbsences', (user, yandex_uids) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/absences/values`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru'
            },
            body: {
                yandex_uids: [yandex_uids],
                datetime_from: '2020-03-20T13:44:23.173Z',
                datetime_to: '2022-03-24T13:44:23.174Z',
                state: 'all',
                limit: 10,
                offset: 0
            }
        }).then(response => {
            Object.keys(response.body.operators[0].absences).forEach(absencesID => {
                const id = response.body.operators[0].absences[absencesID].id;
                const revisionID = response.body.operators[0].operator.revision_id;
                cy.request({
                    method: 'POST',
                    url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/absences/delete`,
                    headers: {
                        'x-csrf-token': user.token,
                        Origin: 'https://wfm.taxi.dev.yandex.ru'
                    },
                    body: {
                        absences: [
                            {
                                id: id,
                                revision_id: revisionID
                            }
                        ]
                    }
                });
                cy.wait(500);
            });
        });
    });
});

Cypress.Commands.add('addSkills', (user, yandex_uid, skills) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/absences/values`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru'
            },
            body: {
                yandex_uids: [yandex_uid],
                datetime_from: '2020-03-20T13:44:23.173Z',
                datetime_to: '2022-03-24T13:44:23.174Z',
                state: 'all',
                limit: 10,
                offset: 0
            }
        }).then(response => {
            cy.request({
                method: 'POST',
                url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/modify`,
                headers: {
                    'x-csrf-token': user.token,
                    Origin: 'https://wfm.taxi.dev.yandex.ru'
                },
                body: {
                    skills: skills,
                    revision_id: response.body.operators[0].operator.revision_id,
                    yandex_uid: yandex_uid
                }
            }).then(response => {
                return response.body;
            });
        });
    });
});

Cypress.Commands.add('addAbsencesType', (user, alias, description) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/absence-types/modify`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            },
            body: {
                alias: alias,
                description: description
            }
        }).then(response => {
            return response.body;
        });
    });
});

Cypress.Commands.add('removeAbsencesType', (user, alias) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/absence-types/values`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            }
        }).then(response => {
            Object.keys(response.body.absence_types).forEach(absencesID => {
                const alias_name = response.body.absence_types[absencesID].alias;
                if (alias_name === alias) {
                    cy.request({
                        method: 'POST',
                        url: `https://cc-api.taxi.tst.yandex.ru/v1/absence-types/delete`,
                        headers: {
                            'x-csrf-token': user.token,
                            Origin: 'https://wfm.taxi.dev.yandex.ru',
                            'X-WFM-Domain': 'taxi'
                        },
                        body: {
                            id: response.body.absence_types[absencesID].id,
                            revision_id: response.body.absence_types[absencesID].revision_id
                        }
                    });
                }
            });
        });
    });
});

Cypress.Commands.add('addProjectActivities', (user, alias, description) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/shift/event/modify`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            },
            body: {
                alias: alias,
                description: description
            }
        }).then(response => {
            return response.body;
        });
    });
});

Cypress.Commands.add('removeProjectActivities', (user, alias) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/shift/event/values`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            }
        }).then(response => {
            Object.keys(response.body.shift_events).forEach(ActivitiesID => {
                const alias_name = response.body.shift_events[ActivitiesID].alias;
                if (alias_name === alias) {
                    cy.request({
                        method: 'POST',
                        url: `https://cc-api.taxi.tst.yandex.ru/v1/shift/event/delete`,
                        headers: {
                            'x-csrf-token': user.token,
                            Origin: 'https://wfm.taxi.dev.yandex.ru',
                            'X-WFM-Domain': 'taxi'
                        },
                        body: {
                            id: response.body.shift_events[ActivitiesID].id,
                            revision_id: response.body.shift_events[ActivitiesID].revision_id
                        }
                    });
                }
            });
        });
    });
});

Cypress.Commands.add('addTags', (user, yandex_uid) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: `https://cc-api.taxi.tst.yandex.ru/v1/operator?yandex_uid=${yandex_uid}`,
            headers: {
                'x-csrf-token': user.token,
                Origin: 'https://wfm.taxi.dev.yandex.ru',
                'X-WFM-Domain': 'taxi'
            }
        }).then(response => {
            cy.request({
                method: 'POST',
                url: `https://cc-api.taxi.tst.yandex.ru/v1/operators/modify`,
                headers: {
                    'x-csrf-token': user.token,
                    Origin: 'https://wfm.taxi.dev.yandex.ru',
                    'X-WFM-Domain': 'taxi'
                },
                body: {
                    // revision_id: revision_id,
                    revision_id: response.body.revision_id,
                    tags: ['потеряшка', 'новичок'],
                    yandex_uid: yandex_uid
                }
            });
        });
    });
});
