const mocks = require('./mocks');

function get(mock) {
    return (execView, {home}) => {
        const req = Object.assign({
            getStaticURL: new home.GetStaticURL({
                s3root: 's3/home-static'
            })
        }, mock);

        return (
            `<script>
                    $(function () {
                        window.mocks = {
                            stocks__popup_tomorrow: ${JSON.stringify(mocks.popupTomorrow)},
                            stocks__popup_sale: ${JSON.stringify(mocks.popupSale)}
                        };

                        const oldAjax = $.ajax;
                        $.ajax = (opts) => {
                            if (opts.url.indexOf('stocks') > -1) {
                                window.sessionsDeferred = $.Deferred();

                                return window.sessionsDeferred.then((data) => opts.success(data),() => opts.error())
                            }

                            return oldAjax.apply(this, arguments);
                        };
                    });
            </script>
            <div style="padding: 50px;width: 900px;">
                ${execView.withReq('InlineStocks', {}, req)}
            </div>`
        );

    };
}

exports.stocksBank = get(mocks.stocksBank);
exports.stocksCash = get(mocks.stocksCash);
