const langSetup = require('./common/langSetup');
const apiSetup = require('./common/apiSetup');
const getMetrics = require('./common/getMetrics');
const createState = require('./common/createState');
const createAMState = require('./authv2/createAMState');
const validateAMParams = require('./authv2/validateAMParams');
const rumCounterSetup = require('./common/rumCounterSetup');
const express = require('express');
const router = express.Router();

const enter = [
    apiSetup,
    langSetup,
    createState,
    validateAMParams,
    createAMState,
    rumCounterSetup,
    function(req, res, next) {
        res.locals.ua = {
            isTouch: true
        };

        return next();
    },
    getMetrics({
        header: 'Пуш для теста ресайза'
    }),
    function renderPage(req, res) {
        const lang = res.locals.language;

        res.render(`react.push-test-popup-resize.${lang}.jsx`);
    }
];

router.get('/', enter);
exports.router = router;
