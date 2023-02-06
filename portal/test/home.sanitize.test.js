describe('home.sanitize', function() {
    it('works as expected', function() {
        home.sanitize('"+alert(\'document.domain+" param layoutType")+"')
            .should.equal('&#34;+alert(&#39;document.domain+&#34; param layoutType&#34;)+&#34;');
    });
});
