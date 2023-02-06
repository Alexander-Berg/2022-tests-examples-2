/* global sinon */

if (!passport) {
    throw new Error("Run 'make testfiles'");
} else {
    if (nb) {
        ['init', 'block', 'blocks'].forEach(function(key) {
            sinon.stub(nb, key);
        });
    }

    if (yr) {
        sinon.stub(yr, 'run');
    }

    $(function() {
        var blockstore = $("<div style='display:none' id='blockstore'></div>");

        $('body').append(blockstore);

        $.each(passport.blocks, function(id, block) {
            if (id === 'user') {
                return; //No need to test a block from header
            }

            if (block.controlSelector) {
                block.controlSelector = null; //Rewrite control selector
            }

            if (id === 'birthday') {
                blockstore.append(
                    '<div data-block="' +
                        id +
                        '"><input /><input name="bday"/><input name="bmohth"/><input name="byear"/></div>'
                );
            } else {
                blockstore.append('<div data-block="' + id + '"><input /></div>');
            }
        });

        try {
            passport.init();
        } catch (e) {
            // eslint-disable-next-line no-console
            console.log(e);
        }
    });
}
