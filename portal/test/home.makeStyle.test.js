describe('home.makeStyle', function() {
    it('should render nothing on empty', function () {
        home.makeStyle({}).should.equal('');
    });

    it('should render style', function () {
        home.makeStyle({
            width: '10px'
        }).should.equal('width:10px');

        home.makeStyle({
            width: '10px',
            height: '20px'
        }).should.equal('width:10px;height:20px');

        home.makeStyle({
            width: '10px',
            height: '20px',
            margin: undefined
        }).should.equal('width:10px;height:20px');

        home.makeStyle({
            width: '10px',
            height: '20px',
            margin: 0
        }).should.equal('width:10px;height:20px;margin:0');
    });
});
