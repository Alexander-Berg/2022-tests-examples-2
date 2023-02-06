/* global Detector */
describe('detector', function() {

    'use strict';

    it('should detect css3 transform property', function() {
        var detector = new Detector();
        detector.getCSS3TransformProperty().should.match(/(MsT|OT|MozT|WebkitT|t)ransform/);
    });
});
