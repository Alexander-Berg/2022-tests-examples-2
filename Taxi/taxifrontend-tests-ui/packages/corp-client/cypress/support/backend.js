const getUserAuth = user => {
    cy.yandexLogin(user);
    return cy
        .request({url: '/api/auth', headers: {'X-Application-Version': '0.0.82'}})
        .then(response => {
            const token = response.body.csrf_token;
            const clientId = response.body.client_id;
            return {
                token: token,
                client_id: clientId
            };
        });
};

Cypress.Commands.add('addDepartment', (user, name, parentId = null) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `/api/1.0/client/${user.client_id}/department`,
            headers: {
                'x-csrf-token': user.token,
                'X-Application-Version': '0.0.82'
            },
            body: {
                name: name,
                parent_id: parentId
            }
        }).then(response => {
            return response.body._id;
        });
    });
});
Cypress.Commands.add('setProfile', (user, tariff, email, comment) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'PUT',
            url: `/api/1.0/client/${user.client_id}/profile`,
            headers: {
                'x-csrf-token': user.token,
                'X-Application-Version': '0.0.82'
            },
            body: {
                email: email,
                comment: comment,
                default_category: tariff,
                low_balance_threshold: 500,
                low_balance_notification_enabled: true
            }
        });
    });
});

Cypress.Commands.add('removeAllDisctrict', user => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: `/api/1.0/client/${user.client_id}/geo_restrictions`,
            headers: {
                'x-csrf-token': user.token,
                'X-Application-Version': '0.0.82'
            }
        }).then(response => {
            Object.keys(response.body.items).forEach(dis => {
                const districtID = response.body.items[dis]._id;

                cy.request({
                    method: 'DELETE',
                    url: `/api/1.0/client/${user.client_id}/geo_restrictions/${districtID}`,
                    headers: {
                        'x-csrf-token': user.token,
                        'X-Application-Version': '0.0.82'
                    }
                });
                cy.wait(500);
            });
        });
    });
});

Cypress.Commands.add('addDistrict', (user, name, center, radius) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `/api/1.0/client/${user.client_id}/geo_restrictions`,
            headers: {
                'x-csrf-token': user.token,
                'X-Application-Version': '0.0.82'
            },
            body: {
                geo_type: 'circle',
                name: name,
                geo: {
                    center: center,
                    radius: radius
                }
            }
        }).then(response => {
            return response.body._id;
        });
    });
});

Cypress.Commands.add('addTemplate', (user, name, comment, tariff) => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url:
                '/api/b2b/cargo-misc/v1/claims/comments/create?idempotency_token=6d6c1127-0420-4a92-9c11-' +
                Date.now(),
            headers: {
                'x-csrf-token': user.token,
                'accept-language': 'ru-RU',
                'X-Application-Version': '0.0.82'
            },
            body: {
                name: name,
                comment: comment,
                tariff: tariff
            }
        }).then(response => {
            return response.body.id;
        });
    });
});

Cypress.Commands.add('removeAllTemplates', user => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'GET',
            url: '/api/b2b/cargo-misc/v1/claims/comments/list',
            headers: {
                'x-csrf-token': user.token,
                'accept-language': 'ru-RU',
                'X-Application-Version': '0.0.82'
            }
        }).then(response => {
            Object.keys(response.body.comments).forEach(temp => {
                const templateID = response.body.comments[temp].id;

                cy.request({
                    method: 'DELETE',
                    url: `/api/b2b/cargo-misc/v1/claims/comments/delete?id=${templateID}`,
                    headers: {
                        'x-csrf-token': user.token,
                        'accept-language': 'ru-RU',
                        'X-Application-Version': '0.0.82'
                    }
                });
                cy.wait(500);
            });
        });
    });
});

Cypress.Commands.add(
    'addRole',
    (user, department_id, email, fullname, phone, role, yandex_login) => {
        getUserAuth(user).then(user => {
            cy.request({
                method: 'POST',
                url: `/api/1.0/client/${user.client_id}/department_manager`,
                headers: {
                    'x-csrf-token': user.token,
                    'X-Application-Version': '0.0.82'
                },
                body: {
                    department_id: department_id,
                    email: email,
                    fullname: fullname,
                    phone: phone,
                    role: role,
                    yandex_login: yandex_login
                }
            }).then(response => {
                return response.body._id;
            });
        });
    }
);

Cypress.Commands.add('removeAllRoles', user => {
    getUserAuth(user).then(user => {
        cy.request({
            method: 'POST',
            url: `/api/1.0/client/${user.client_id}/department_manager/search`,
            headers: {
                'x-csrf-token': user.token,
                'accept-language': 'ru-RU',
                'X-Application-Version': '0.0.82'
            },
            body: {
                limit: 50,
                offset: 0,
                sort: [
                    {
                        direction: 'asc',
                        field: 'fullname'
                    }
                ]
            }
        }).then(response => {
            Object.keys(response.body.department_managers).forEach(role => {
                const roleID = response.body.department_managers[role]._id;
                cy.request({
                    method: 'DELETE',
                    url: `/api/1.0/client/${user.client_id}/department_manager/${roleID}`,
                    headers: {
                        'x-csrf-token': user.token,
                        'accept-language': 'ru-RU',
                        'X-Application-Version': '0.0.82'
                    }
                });
                cy.wait(500);
            });
        });
    });
});

Cypress.Commands.add('addGroup', (user, depId, groupName) => {
    getUserAuth(user).then(user => {
        cy.fixture('requests/group_create').then(body => {
            body['department_id'] = depId;
            body['name'] = groupName;
            cy.request({
                method: 'POST',
                url: `/api/1.0/group`,
                headers: {
                    'x-csrf-token': user.token,
                    'X-Application-Version': '0.0.82'
                },
                body: body
            }).then(response => {
                return response.body._id;
            });
        });
    });
});
