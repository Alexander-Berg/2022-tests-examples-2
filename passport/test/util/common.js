var superagent = require('superagent');
var trackID;
// Может пригодиться, если тестировать на реальном апи, чтобы трек был
// настоящий

function commonBefore(done) {
    superagent
        .post('http://127.0.0.1:80/1/track/?consumer=passport')
        .send({track_type: 'authorize'})
        .end(function(res) {
            if (res.ok) {
                console.error(res.body);
                trackID = res.body.id;
            } else {
                console.error(`Oh no! error ${res.text}`);
            }
            done();
        });
}

function commonAfter(done) {
    superagent.del(`http://127.0.0.1:80/1/track/${trackID}?consumer=passport`).end(function() {
        done();
    });
}

exports.before = commonBefore;
exports.after = commonAfter;
