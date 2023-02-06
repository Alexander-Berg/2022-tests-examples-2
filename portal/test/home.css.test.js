describe('home.CSS', function() {
    var CSS = home.css();
    it('have all methods', function() {
        CSS.should.be.an('object');
        CSS.decl.should.be.a('function');
        CSS.get.should.be.a('function');
        CSS.clear.should.be.a('function');
    });

    it('generates css', function() {
        CSS.clear();
        CSS.decl('.first').push('color:red', 'height:20px', 'width:30px');

        CSS.get().should.equal('.first{color:red;height:20px;width:30px}');

        CSS.decl('.second').push('background-color: whitesmoke');

        CSS.get('.second').should.equal('.second{background-color: whitesmoke}');
        CSS.get().should.equal('.first{color:red;height:20px;width:30px}.second{background-color: whitesmoke}');

        CSS.decl('.first').push('font-size:14px');

        CSS.get('.first').should.equal('.first{color:red;height:20px;width:30px;font-size:14px}');
        CSS.get().should.equal('.first{color:red;height:20px;width:30px;font-size:14px}.second{background-color: whitesmoke}');

        CSS.clear('.first');
        CSS.get('.second').should.equal('.second{background-color: whitesmoke}');
        CSS.get().should.equal('.second{background-color: whitesmoke}');
    });
});
