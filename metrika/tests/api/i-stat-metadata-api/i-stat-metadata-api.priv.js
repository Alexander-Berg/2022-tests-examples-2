BEM.decl('i-stat-metadata-api', null, {
    getSegmentsTree: function () {
        return Vow.fulfill(BN('d-stat-metadata-api').getSegmentsTree())
            .then(function (segmentsTree) {
                return this._transformSegmentsStruct(jQuery.extend(true, [], segmentsTree.common_segments)).concat(
                    this._transformSegmentsStruct(jQuery.extend(true, [], segmentsTree.usercentric_segments), true)
                );
            }.bind(this));
    }
});
