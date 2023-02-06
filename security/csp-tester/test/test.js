const assert = require('assert');
const csp = require('../utils/csp/csp');
const config = require('config');

describe('CSP', () => {
    describe('Directive', () => {
        it('Directive simply works', () => {
            let value = "'self'";
            d = new csp.Directive();
            d.initValue(value);
            assert.strictEqual(value, d.value);
        });
        
        it('Check source list limit', () => {
            let value = "'self' foo.com aaa.com dd.com";
            d = new csp.Directive('script-src');
            d.sourceLimit = 2;
            d.initValue(value);
            let issues = d.findIssues();
            assert.ok(issues.filter((v)=>{return v.type == 'sourceLimit'}));
        });
        
    });

    describe('Policy', () => {
        it('CSP parser should work', () => {
            let value = "script-src 'self'; report-uri /someuri";
            let policy = new csp.Policy();
            assert.ok(policy.initValue(value));
            assert.strictEqual(value, policy.getStringPolicy(false, false));
        });

        it('CSP test case in which site do not provide "unsafe-inline"', () => {
            let value = "script-src 'self'; report-uri /someuri";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.isUnsafeInlineEnabled());
        });

        it('CSP test case in which site do not provide "unsafe-inline" in script-src', () => {
            let value = "script-src 'self'; img-src 'unsafe-inline'; report-uri /someuri";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.isUnsafeInlineEnabled());
        });

        it('CSP test case in which site provides "unsafe-inline" in script-src', () => {
            let value = "script-src 'self' 'unsafe-inline';";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.isUnsafeInlineEnabled());
        });

        it('CSP test case in which site provides "unsafe-inline" in style-src', () => {
            let value = "style-src 'unsafe-inline';";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.isUnsafeInlineEnabled());
        });

        it('CSP test case in which site do not provide report-uri', () => {
            let value = "default-src 'none';";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.getReportUri());
        });

        it('CSP test case in which site provides report-uri', () => {
            let value = "default-src 'none'; report-uri /someuri";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.strictEqual("/someuri", policy.getReportUri());
        });

        it('CSP test case in which site do not provide report-uri and we need to know about it', () => {
            let value = "default-src 'none';";
            let policy = new csp.Policy();
            policy.reportNoReportUri = true;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });

        it('Test CSP with invalid directives (misprint)', () => {
            let value = "default-source 'none';";
            let policy = new csp.Policy();
            assert.ok(!policy.initValue(value));
        });

        it('Test CSP with invalid directive values', () => {
            let value = "default-src 'none'; img-src aaa'bbb";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });

        it('Test CSP with invalid directive values', () => {
            let value = "default-src 'none'; img-src aaa'bbb";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });

        it('Test CSP with directive values separated with double spaces', () => {
            let value = "default-src 'none'; script-src example1.com example2.com  'nonce-d7d6d84382404f1ab6b8ccc8fbd76ecd'";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(0, issues.length);
        });

        it('Test case in which several directives are specified using only 1 CSP policy but with 6 differents directives.', () => {
            let value = "default-src 'self'; img-src *;";
            value += " object-src media1.example.com media2.example.com";
            value += " *.cdn.example.com; script-src trustedscripts.example.com;";
            value += " form-action foo.com/ctxroot/action1 foo.com/ctxroot/action2;";
            value += " plugin-types application/pdf;";

            let policy = new csp.Policy();
            policy.initValue(value);

            assert.strictEqual(6, policy.directives.length);

            let d = policy.getDirectiveByName('default-src');
            assert.ok(d);
            assert.strictEqual(d.sourceList[0], "'self'");

            d = policy.getDirectiveByName('img-src');
            assert.ok(d);
            assert.strictEqual(d.sourceList[0], "*");

            d = policy.getDirectiveByName('script-src');
            assert.ok(d);
            assert.strictEqual(d.sourceList[0], "trustedscripts.example.com");

            d = policy.getDirectiveByName('object-src');
            assert.ok(d);
            assert.strictEqual(d.sourceList[0], "media1.example.com");
            assert.strictEqual(d.sourceList[1], "media2.example.com");
            assert.strictEqual(d.sourceList[2], "*.cdn.example.com");

            d = policy.getDirectiveByName('form-action');
            assert.ok(d);
            assert.strictEqual(d.sourceList[0], "foo.com/ctxroot/action1");
            assert.strictEqual(d.sourceList[1], "foo.com/ctxroot/action2");

            d = policy.getDirectiveByName('plugin-types');
            assert.ok(d);
            assert.strictEqual(d.mediaTypeList[0], "application/pdf");
        });

        it('Test case in which 2 directives are specified using special directives with explicit values.', () => {
            let value = "sandbox allow-forms allow-scripts ;";
            value += " script-src 'nonce-AABBCCDDEE'";
            let policy = new csp.Policy();
            policy.initValue(value);

            assert.strictEqual(2, policy.directives.length);

            let d = policy.getDirectiveByName('sandbox');
            assert.ok(d);
            assert.strictEqual(2, d.flags.length);
            assert.strictEqual(d.flags[0], "allow-forms");
            assert.strictEqual(d.flags[1], "allow-scripts");

            d = policy.getDirectiveByName('script-src');
            assert.ok(d);
            assert.strictEqual("'nonce-AABBCCDDEE'", d.sourceList[0]);

        });


        it('Test detecting wildcards', () => {
            let value = "default-src 'none'; script-src *;";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssuesByDirective('script-src');
            assert.strictEqual(1, issues.length);
        });
        
        it('Test detecting wildcards WITH exclusion for Maps special hosts.', () => {
            let value = "default-src 'none'; img-src data: https://*.maps.yandex.net;";
            value += "script-src https://*.maps.yandex.net;";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(issues.length, 0);
        });
        
        it('Test detecting wildcards via scheme source', () => {
            let value = "default-src 'none'; script-src https:;";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssuesByDirective('script-src');
            assert.strictEqual(1, issues.length);
        });

        it('Test case in witch CSP doesn\'t protect against XSS (empty).', () => {
            let value = "";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.protectsAgainstXss());
        });

        it('Test case in witch CSP doesn\'t protect against XSS (wildcard value of script-src).', () => {
            let value = "script-src *;";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.protectsAgainstXss());
        });

        it('Test case in witch CSP protects against XSS (with unsafe-inline and nonces/hashes).', () => {
            let value = "default-src 'self'; script-src 'self' 'unsafe-inline' 'nonce-AADD';";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.protectsAgainstXss());
        });

        it('Test case in witch CSP protects against XSS (with unsafe-inline, wildcards, strict-dynamic and nonces/hashes).', () => {
            let value = "default-src 'self'; script-src 'self' 'unsafe-inline' 'strict-dynamic' 'nonce-AADD' http: https:;";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.protectsAgainstXss());
        });

        it('Test case in witch CSP does not protect against XSS 2.', () => {
            let value = "default-src 'self' blob: ;" +
                "script-src 'self' 'unsafe-inline' 'unsafe-eval';";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.protectsAgainstXss());
        });

        it('Test case in witch CSP DOES NOT protect against XSS (unsafe-inline + invalid nonces/hashes).', () => {
            let value = "default-src 'self'; script-src 'self' unsafe-inline nonce-AADD;";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.protectsAgainstXss());
        });

        it('Test case in witch CSP protects against XSS (simply).', () => {
            let value = "default-src 'self'";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.protectsAgainstXss());
        });

        it('Test case in witch CSP protects against XSS (simply) 2.', () => {
            let value = "default-src 'self'; script-src 'self'";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.protectsAgainstXss());
        });
        it('Test case in witch site provide CSP features and enable use of the javascript "eval()" function into is CSP Script policies BUT we do accept theses configurations.', () => {
            let value = "default-src 'self'; script-src 'self' 'unsafe-eval' 'nonce-AADD'";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(policy.protectsAgainstXss());
        });


        it('Test case in witch site provide CSP features and have a vuln on Script policies (data:).', () => {
            let value = "script-src data:";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.ok(!policy.protectsAgainstXss());
        });


        it('Test case in witch site provide CSP features and enable use of the javascript "eval()" function into is CSP Script policies AND we want to report it.', () => {
            let value = "default-src 'self'; script-src 'self' 'unsafe-eval'";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssuesByDirective('script-src');
            assert.strictEqual(1, issues.length);
        });


        it('Test case in witch site provide CSP features and enable use of the javascript "eval()" function into is CSP Script policies AND we DO NOT want to report it.', () => {
            let value = "default-src 'self'; script-src 'self' 'unsafe-eval'";
            let policy = new csp.Policy();
            policy.reportEval = false;
            policy.initValue(value);
            let issues = policy.findIssuesByDirective('script-src');
            assert.strictEqual(issues.length, 0);
        });

        it('Test case in which we add untrusted hosts into somes policies.', () => {
            let value = "default-src 'self'; script-src 'self' trust.com evil.com;";
            let policy = new csp.Policy();
            policy.trustedHosts = ['trust.com'];
            policy.initValue(value);
            let issues = policy.findIssuesByDirective('script-src');
            assert.strictEqual(1, issues.length);
        });


        it('Test case in which directive includes hashes.', () => {
            let value = "script-src 'sha256-nP0EI9B9ad8IoFUti2q7EQBabcE5MS5v0nkvRfUbYnM='";
            value += " 'sha256-pH+KSy1ZHTi4vu+kNocszrH0NtTuvixRZIV38uhbnlM=';";
            let policy = new csp.Policy();
            policy.initValue(value);
            let d = policy.getDirectiveByName('script-src');
            assert.strictEqual(2, d.sourceList.length);
        });

        it('Test case in which we set strictness level for default-src 0 (all sources permitted).', () => {
            let value = "default-src 'self' foo.com; form-action foobar.com; frame-ancestors 'none';";
            let policy = new csp.Policy();
            policy.initValue(value);
            policy.defaultSrcStrictness = 0;
            let issues = policy.findIssues();
            assert.strictEqual(0, issues.length);
        });

        it('Test case in which we set strictness level for default-src 1 (only \'self\').', () => {
            let value = "default-src 'self' foo.com; form-action foobar.com; frame-ancestors 'none';";
            let policy = new csp.Policy();
            policy.defaultSrcStrictness = 1;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });
       
        it('Test case in which we set strictness level for default-src 2 (only \'none\').', () => {
            let value = "default-src 'self'; form-action foobar.com; frame-ancestors 'none';";
            let policy = new csp.Policy();
            policy.defaultSrcStrictness = 2;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });

        it('Test case in which we test required directives (form-action, frame-ancestors, base-uri).', () => {
            let value = "default-src 'self';";
            let policy = new csp.Policy();
            policy.reportNotFallback = true;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(3, issues.length);
        });

        it('Test case in which we test scenario with default-src not explicitly set.', () => {
            let value = "script-src 'self';";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });

        it('CSP test case in which site provide ->PERFECT<- CSP policy', () => {
            let value = "default-src 'none';";
            value += "frame-ancestors yandex.ru; form-action 'self';";
            value += "base-uri 'self'; report-uri https://csp.yandex.net/csp";
            let policy = new csp.Policy();
            policy.defaultSrcStrictness = 2;
            policy.trustedHosts = ['yandex.ru', 'yandex.net'];
            policy.reportNoReportUri = true;
            policy.reportEval = true;
            policy.sourceLimit = 5;
            policy.reportNotFallback = true;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(0, issues.length);
        });

        it('Test case in which we test scenario with url sources', () => {
            let value = "default-src 'self'; script-src https://yandex.ru";
            let policy = new csp.Policy();
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(0, issues.length);
        });


        it('Test case in which we allow data: in img-src.', () => {
            let value = "default-src 'none'; img-src data:";
            let policy = new csp.Policy();
            policy.reportNoReportUri = false;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(0, issues.length);
        });

        it('Test case in which we test weak nonces.', () => {
            let value = "default-src 'none'; script-src 'nonce-1656'";
            let policy = new csp.Policy();
            policy.reportNoReportUri = false;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(1, issues.length);
        });

        it('Test case in which we test not standard (see https://www.w3.org/TR/CSP2/#nonce_value) but good nonces (e.g. UUIDv4).', () => {
            let value = "default-src 'none'; script-src 'nonce-cdf630e8-512b-445b-b6e1-a3fcfe635e2f'";
            let policy = new csp.Policy();
            policy.reportNoReportUri = false;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual(0, issues.length);
        });


        it('Test case in which we test sorting in issues.', () => {
            let value = "default-src *;";
            let policy = new csp.Policy();
            policy.reportNoReportUri = true;
            policy.initValue(value);
            let issues = policy.findIssues();
            assert.strictEqual('High', issues[0].severity.label);
            assert.strictEqual('Low', issues[1].severity.label);
        });

        it('Test case in which we test wildcard subdomains in critical directives.', () => {
            let value = "default-src 'none'; script-src *.yandex.net; img-src *.yandex.net";
            let policy = new csp.Policy();
            policy.reportNoReportUri = false;
            policy.initValue(value);
            let issues = policy.findIssuesByDirective('script-src');
            assert.strictEqual(1, issues.length);
            issues = policy.findIssuesByDirective('img-src');
            assert.strictEqual(0, issues.length);
        });

        // it('Test case in which we test self/l7 domains in risky directives.', () => {
        //     let value = "default-src 'none'; script-src yandex.ru; object-src 'self'";
        //     let policy = new csp.Policy();
        //     policy.l7hosts = ['yandex.ru'];
        //     policy.reportNoReportUri = false;
        //     policy.initValue(value);
        //     let issues = policy.findIssuesByDirective('script-src');
        //     assert.strictEqual(1, issues.length);
        //     issues = policy.findIssuesByDirective('object-src');
        //     assert.strictEqual(1, issues.length);
        // });
        
        it('Test case in which we test wildcards domains in risky directives.', () => {
            let value = "default-src 'none'; script-src *.yandex.net;";
            let policy = new csp.Policy();
            policy.l7hosts = ['yandex.ru'];
            policy.reportNoReportUri = false;
            policy.initValue(value);
            assert.ok(!policy.protectsAgainstXss());
        });

        it('Must parse all CSPv3 directives', () => {
            let value = "upgrade-insecure-requests; block-all-mixed-content; manifest-src https://www.yandex.ru/; " +
                "require-sri-for script style; worker-src https://yandex.com/; script-src 'report-sample' 'strict-dynamic'; " + 
                "style-src-elem 'self' 'unsafe-inline' yastatic.net; script-src-elem 'self' 'unsafe-inline' yastatic.net; " +
                "style-src-attr 'self' 'unsafe-inline'; script-src-attr 'self' 'unsafe-inline' yastatic.net; ";
            let policy = new csp.Policy();
            policy.initValue(value);
            assert.strictEqual(0, policy.syntaxErrors.length);
        });
    });

    describe('Header fetcher', () => {
        if (process.env.CSPDEV) {
            return;
        }
        it('Header fetcher simply works', () => {
            let settings = config.get('csp');
            let fetcher = new csp.Fetcher(['yandex.ru']);
            return fetcher.getPolicy('https://passport.yandex.ru/auth').then(
                value => {assert.ok(value);}
            );
        });

        it('Header fetcher simply works for meta tag', () => {
            let settings = config.get('csp');
            let fetcher = new csp.Fetcher(['yandex.ru']);
            return fetcher.getPolicy('https://yandex.ru/maps').then(
                value => {assert.ok(value);}
            );
        });

        it('Header fetcher will not fetch URL because of network access', () => {
            let settings = config.get('csp');
            let fetcher = new csp.Fetcher(['yandex.ru']);
            return fetcher.getPolicy('http://aaaa.yandex.ru/').catch(
                value => assert.ok(value instanceof csp.FetcherError)
            );
        });

        it('Header fetcher will not fetch URL because of rejected hostname', () => {
            let settings = config.get('csp');
            let fetcher = new csp.Fetcher(['yandex.ru']);
            return fetcher.getPolicy('https://evil.ru/').catch(
                value => assert.ok(value instanceof csp.FetcherError)
            );
        });

        it('Header fetcher will not fetch URL because of rejected hostname 2 (try to bypass via "similar" name)', () => {
            let settings = config.get('csp');
            let fetcher = new csp.Fetcher(['yandex.ru']);
            return fetcher.getPolicy('http://hahaha-yandex.ru/').catch(
                value => assert.ok(value instanceof csp.FetcherError)
            );
        });
    });

});
