const CounterGrantsData = {
    simpleUser: {
        realLogin: 'tsetaq2',
        expectedLogin: 'tsetaq2'
    },
    yandexMailUser: {
        realLogin: 'tsetaq2@yandex.ru',
        expectedLogin: 'tsetaq2'
    },
    liteUser: {
        realLogin: 'lite8@test.ru',
        expectedLogin: 'lite8@test.ru'
    },
    registeredLiteUser: {
        realLogin: 'lite0testru',
        expectedLogin: 'lite0testru'
    },
    pddUser: {
        realLogin: 'at-metrika-pdd-1@konkov.kida-lo-vo.name',
        expectedLogin: 'at-metrika-pdd-1@konkov.kida-lo-vo.name'
    },
    phoneNumberUser: {
        realLogin: '79105082780',
        expectedLogin: 'anastasiOU29'
    },
    //Пользователи для негативных проверок
    noneExistentUser: 'at-metrika-non-existent-user',
    emptyUser: '',
    existUser: 'tsetaq2',
    userWithInvalidLogin: 'at-metrika@',
    userWithWrongMail: 'at-metrika@gmail.com'
};

module.exports = CounterGrantsData;
