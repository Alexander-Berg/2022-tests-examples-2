const express = require('express');
const router = express.Router();
const csp = require('../utils/csp/csp');
const config = require('config');

router.post('/', function(req, res) {
    let result = {
        issues: [],
        pretty: '',
        errors: [],
        protects: false,
    };
    let policy = new csp.Policy();
    policy.__ = res.__;
    let settings = config.get('csp');
    let value = req.body.policy.trim();

    for (let key in settings) {
        if (key in policy) {
            policy[key] = settings[key];
        }
    }

    if (value.startsWith("https://") || value.startsWith("http://")) {
        let fetcher = new csp.Fetcher(settings.trustedHosts);
        fetcher.getPolicy(value).then(csp_value => {
            if (csp_value.length > 0) {
                result.policy = csp_value;
                if (policy.initValue(csp_value)) {
                    result.issues = policy.findIssues();
                    result.pretty = policy.getStringPolicy(true);
                    result.protects = policy.protectsAgainstXss();
                } else {
                    result.errors.push("Can't parse CSP value");
                }
            }
            res.json(result);
        }).catch(error => {
            if (error instanceof csp.FetcherError) {
                result.errors.push(error.message);
                res.json(result);
            }
        });
    } else {
        ["Content-Security-Policy", "Content-Security-Policy-Report-Only"].forEach((h) => {
            let chunks = value.split(h + ":");
            if (chunks.length > 1) {
                value = chunks[1].trim();
            }
        });

        if (policy.initValue(value)) {
            result.issues = policy.findIssues();
            result.pretty = policy.getStringPolicy(true);
            result.protects = policy.protectsAgainstXss();
        } else {
            result.errors.push("Can't parse CSP value");
        }
        res.json(result);
    }
});

module.exports = router;
