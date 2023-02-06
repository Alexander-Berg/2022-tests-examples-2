BEM.decl('i-counter-storage', {}, {
    find: function () {
        return Vow.fulfill(BN('d-counter').get());
    }
});
