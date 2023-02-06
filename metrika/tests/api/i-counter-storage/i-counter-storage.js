//TODO bad, copy&paste from priv part
//need to fix i-proxy to make it work with client-side part of tests
//@see https://st.yandex-team.ru/METR-20427 for details
BEM.decl('i-counter-storage', {}, {
    find: function () {
        return Vow.fulfill(BN('d-counter').get());
    }
});
