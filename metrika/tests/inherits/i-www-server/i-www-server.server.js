(function () {
    var Domain = require('domain'),
        domain =  Domain.create();

    //It's required to enter into domain
    //to make block that uses i-state directly or indirectly
    //(for example i-router, i-locale, all models)
    process.domain = domain;
})();
BEM.decl('i-www-server', {}, {
    // prevent running server for 'test' environment
    init: function () {
    }
});
