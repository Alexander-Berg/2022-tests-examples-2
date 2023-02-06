//TODO bad, copy&paste from priv part
//need to fix i-proxy to make it work with client-side part of tests
//@see https://st.yandex-team.ru/METR-20427 for details
BEM.decl('i-stat-metadata-api', null, {
    getSegmentsTree: function () {
        return Vow.fulfill(BN('d-stat-metadata-api').getSegmentsTree())
            .then(function (segmentsTree) {
                return this._transformSegmentsStruct(jQuery.extend(true, [], segmentsTree.common_segments)).concat(
                    this._transformSegmentsStruct(jQuery.extend(true, [], segmentsTree.usercentric_segments), true)
                );
            }.bind(this));
    },

    _transformSegmentsStruct: function (tree, userCentric) {
        return tree.filter(function (item) {
            if (item.chld) {
                item.chld = this._transformSegmentsStruct(item.chld, userCentric);
                return Boolean(item.chld.length);
            }

            if (item.dims) {
                item.id = item.dims[0];
            } else if (item.dim) {
                item.id = item.dim;
            }

            item.id += userCentric ? '-usercentric' : '';
            item.userCentric = Boolean(userCentric);
            return true;
        }, this);
    }
});
