const isFintech = require('../scripts/is-fintech');

module.exports = {
    ...(require(`./${isFintech ? 'fintech' : 'non-fintech'}/testing`))
};
