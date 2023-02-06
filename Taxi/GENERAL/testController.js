const express = require('express');

const Response = require('../utils/response');

class TestController {
    /**
     * Контроллер ручки для тестов
     * @param {express.Request} req
     * @param {express.Response} res
     */
    static async doAnything(req, res) {
        res.send(Response.message({msg: 'test'}));
    }
}

module.exports = TestController;
