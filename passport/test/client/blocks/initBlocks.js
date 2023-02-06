if (!passport) {
    throw new Error("Run 'make testfiles'");
} else {
    $(function() {
        nb.init = $.noop;
        nb.block = $.noop;

        var blockstore = $("<div style='display:none' id='blockstore'></div>");
        $('body').append(blockstore);

        $.each(passport.blocks, function(id, block) {
            if (id === 'user') {
                return; //User block should not be tested here
            }

            if (block.controlSelector) {
                block.controlSelector = null; //Rewrite control selector
            }

            blockstore.append('<div data-block="' + id + '"><input /></div>');
        });

        try {
            passport.init();
        } catch(err) {
            console.error(err);
        }
    });
}
