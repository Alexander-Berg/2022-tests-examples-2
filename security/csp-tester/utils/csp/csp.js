'use strict';

const url = require('url');
const got = require('got');

const KEYWORDS = ["'self'", "'unsafe-inline'", "'unsafe-eval'", "'report-sample'", "'strict-dynamic'"];

class Severity {
    constructor() {
        this.label = '';
        this.score = 0;
    }

    static get HIGH() {
        return new HighSeverity();
    }

    static get INFORMATION() {
        return new InformationSeverity();
    }

    static get LOW() {
        return new LowSeverity();
    }

    static get MEDIUM(){
        return new MediumSeverity();
    }
}


class HighSeverity extends Severity {
    constructor() {
        super();
        this.label = 'High';
        this.score = 4;
    }
}

class MediumSeverity extends Severity {
    constructor() {
        super();
        this.label = 'Medium';
        this.score = 3;
    }
}

class LowSeverity extends Severity {
    constructor() {
        super();
        this.label = 'Low';
        this.score = 2;
    }
}

class InformationSeverity extends Severity {
    constructor() {
        super();
        this.label = 'Information';
        this.score = 1;
    }
}

class Issue {
    constructor(desc, severity, type, directive) {
        this.desc = desc;
        this.severity = severity;
        this.type = type;
        this.directive = directive;
    }
}

// High issues are on the first place/top
function sortIssues(issues) {
    return issues.sort((i1, i2) => {
        if (i1.severity.score < i2.severity.score) {
            return 1;
        }
        if (i1.severity.score > i2.severity.score) {
            return -1;
        }
        return 0;
    });
}

class Directive {
    constructor(name="CSPDirective") {
        this.name = name;
        this.value = '';
        this.sourceList = [];
        this._sourceLimit = null;
        this.trustedHosts = [];
        this.l7hosts = [];
        this.syntaxErrors = [];
        this.__ = (m) => {return m};
    }

    initValue(value) {
        value = value.trim();
        if (!this._parseSourceList(value)) {
            return false;
        }
        this.value = value;
        return true;
    }
    
    /**
     * Parse directive value and set up directive sourse list.
     * See also https://www.w3.org/TR/CSP2/#source-list-parsing
     */
    _parseSourceList(value) {
        this.syntaxErrors = [];
        let sourceList = value.trim();
        
        if (sourceList.toLowerCase() == "'none'") {
            this.sourceList = [];
            return true;
        }
       
        let result = [];
        let tokens = value.split(' ');
        tokens = tokens.filter((x)=>{return x.trim()});

        for (let i=0; i<tokens.length; i++) {
            if (this.isValidSource(tokens[i])) {
                result.push(tokens[i]);       
            } else {
                let v = new Issue(this.__("issueParseSource", this.name, tokens[i]), Severity.HIGH, 'syntax', this.name);
                this.syntaxErrors.push(v);
            }
        }
        this.sourceList = result;
        return true
    }
    
    /**
     * Check if token is valid source. See also https://www.w3.org/TR/CSP2/#source-list-syntax
    */
    isValidSource(token) {
        if (token == '*') {
            return true;
        }
        // keyword-source
        if (KEYWORDS.indexOf(token) != -1) {
            return true;
        }

        // nonce-source
        if (/'nonce-[a-zA-Z0-9+/-]+[=]{0,2}'/.test(token)) {
            return true;
        }
        // hash-source
        if (/'(sha256|sha384|sha512)-[a-zA-Z0-9+/]+[=]{0,2}'/.test(token)) {
            return true;
        }
        // scheme-source
        if (this._isSchemeSource(token)) {
            return true;
        }
        // host-source
        if (this._isHostSource(token)) {
            return true;
        }
        return false;
    }
    
    _isSchemeSource(token) {
        // scheme-source
        let tmp = Directive._normalizeHostSource(token);
        let o = url.parse(tmp, false, true);
        if (o.protocol == tmp) {
            return true;
        }
        return false;
    }

    _isHostSource(token) {
        if (token.startsWith("'")) {
            return false;
        }
        let tmp = Directive._normalizeHostSource(token);
        let o = url.parse(tmp, false, true);

        if (/[^a-zA-Z:*0-9.-]/.test(o.host)) {
            return false;
        }
        if (!o.hostname) {
            return false;
        }
        if (o.href.toLowerCase() == tmp.toLowerCase()) {
            return true;
        }
        return false;
    }
    /**
     * Normalize host source for further processing.
     */
    static _normalizeHostSource(token) {
        let result = token;
        let o = url.parse(result, false, true);
        // scheme-part
        // We need this code to make hostname parsibale as url
        if (!o.protocol && !result.startsWith('//')) {
            result = '//' + result;
        }
        // port-part
        result = result.split(":*").join(":0");
        // host-part
        result = result.split("*.").join("Q.");
        result = result.split("*").join("A");
        o = url.parse(result, false, true);

        if (o.hostname && !result.endsWith('/')) {
            result = result + '/';
        }
        return result;
    }
    
    get sourceLimit() {
        return this._sourceLimit
    }
    
    set sourceLimit(value) {
        this._sourceLimit = value
    }
    
    getNoncesHashes(nonces=true, hashes=true) {
        let result = [];
        let targets = [];
        if (nonces) {
            targets.push("'nonce-");
        }
        if (hashes) {
            targets.push("'sha256-");
            targets.push("'sha384-");
            targets.push("'sha512-");
        }
        for (let i=0; i<this.sourceList.length; i++) {
            for (let j=0; j<targets.length; j++) {
                if (this.sourceList[i].startsWith(targets[j])) {
                    result.push(this.sourceList[i]);
                }
            }
        }
        return result;
    }
    
    _findWildcardIssues(severity) {
        let issues = [];
        let scheme_wildcards = this.sourceList.filter((token) => {
            // We pass there data: scheme because 
            // we have separate check for it in _checkDataSource
            if (this._isSchemeSource(token) && token != 'blob:' && token != 'data:') {
                return true;
            } else {
                return false;
            }
        });

        if (this.sourceList.indexOf('*') != -1 || scheme_wildcards.length > 0) {
            let tmp_severity = this._isRiskyDirective(this.name) ? Severity.HIGH : severity;
            let v = new Issue(this.__("issueWildcard", this.name), tmp_severity, 'wildcard', this.name);
            issues.push(v);
        }
        return issues;
    }

    _isRiskyDirective() {
        return ['default-src', 'script-src', 'object-src'].indexOf(this.name) != -1;
    }

    _findWildcardSubdomainIssues(severity) {
        let issues = [];

        if (!this._isRiskyDirective()) {
            return [];
        }
        // See https://tech.yandex.ru/maps/doc/jsapi/2.1/dg/concepts/load-docpage/#using-csp
        let exclusions = [
            'https://*.maps.yandex.net',
            '*.maps.yandex.net',
            'https://*.maps.yandex.ru',
            '*.maps.yandex.ru'];
            
        let wildcards = this.sourceList.filter((token) => {
             if (this._isHostSource(token) && exclusions.indexOf(token) == -1) {
                let source = Directive._normalizeHostSource(token);
                // See _normalizeHostSource() for more details
                if (source.indexOf('Q.') != -1) {
                    return true;
                }
            } else {
                return false;
            }
        });

        if (wildcards.length > 0) {
            let v = new Issue(
                this.__("issueWildcardSubdomain", this.name, wildcards.join(', ')), severity, 'wildcardsubdomain', this.name);
            issues.push(v);
        }
        return issues;
    }

    /**
     * Check if data: is included in source list of risky directives
     */
    _checkDataSource() {
        let issues = [];
        if (this.sourceList.indexOf('data:') != -1 && this._isRiskyDirective()) {
            let v = new Issue(this.__("issueDataSource", this.name), Severity.HIGH, 'data_source', this.name);
            issues.push(v)
        }
        return issues;
    }
    
    isUnsafeInlineEnabled() {
        return (this.sourceList.indexOf("'unsafe-inline'") != -1)
    }
    
    isStrictDynamicEnabled() {
        if (this.sourceList.indexOf("'strict-dynamic'") === -1) {
            return false;
        }

        if (this.getNoncesHashes(true, false).length === 0) {
            return false;
        }

        return true;
    }

    /**
     * Check if 'unsafe-eval' or equivalent is included in source list of directive
    */
    _findEvalIssues() {
        let issues = [];
        if (!this.reportEval) {
            return [];
        }
        let result = this.sourceList.filter((t)=>{return t == "'unsafe-eval'"});
        // See "Security Considerations for GUID URL schemes"
        // https://www.w3.org/TR/CSP/#source-list-guid-matching
        let riskySchemes = this.sourceList.filter((t)=>{return (['blob:', 'filesystem:'].indexOf(t) != -1)});

        if (['default-src', 'script-src'].indexOf(this.name) != -1 && riskySchemes.length > 0) {
            result.push(...riskySchemes);
        }
        
        if (result.length > 0) {
            let v = new Issue(this.__("issueEval", this.name, result.join(', ')),
Severity.MEDIUM, 'eval', this.name);
            issues.push(v);
        }
        return issues;
    }
    
    /**
     * Find source limit exceed vulnerabilities (when too many sources in directive source list)
     */
    _checkSourceLimit() {
        let issues = [];
        
        if (!this.sourceList.length) {
            return [];
        }

        if (this.sourceLimit !== null && this.sourceList.length > this.sourceLimit) {
            let v = new Issue(this.__("issueSourceLimit", this.name),
                Severity.LOW, 'sourceLimit', this.name);
            issues.push(v);
        }
        return issues;    
    }
    
    _checkUntrustedSources() {
        let issues = [];
        let untrusted = [];
        
        if (this.trustedHosts.length == 0) {
            return [];
        }

        for (let i=0; i<this.sourceList.length; i++) {
            if (this._isHostSource(this.sourceList[i])) {
                let tmp = Directive._normalizeHostSource(this.sourceList[i]);
                let o = url.parse(tmp, false, true);
                let result = true;

                for (let j=0; j<this.trustedHosts.length; j++) {
                    if (o.hostname.endsWith(this.trustedHosts[j])) {
                        result = false;
                    }
                } 

                if (result) {
                    untrusted.push(this.sourceList[i]);          
                }
            }        
        }
        if (untrusted.length > 0) {
            let v = new Issue(this.__("issueUntrust", this.name, untrusted.join(", ")), Severity.LOW, 'untrust', this.name);
            issues.push(v);
        }
        return issues;
    }
 
    _findWeakNoncesIssues() {
        let issues = [];
        let nonces = this.getNoncesHashes(true, false);
        let result = nonces.filter((n) => {
            if (!/'nonce-[a-zA-Z0-9+/-]{22,}[=]{0,2}'/.test(n)) {
                return true;
            }
        });

        if (result.length > 0) {
            let v = new Issue(this.__("issueWeakNonces", this.name, result.join(', ')),
Severity.LOW, 'weaknonces', this.name);
            issues.push(v);
        }
        return issues;
    }

    /**
     * Check if 'self' or L7 domain are included in source list of risky directives
     */
    _findSameOriginIssues() {
        if (!this._isRiskyDirective() || this.l7hosts.length == 0) {
            return [];
        }

        let issues = [];
        let untrusted = [];

        untrusted.push(...this.sourceList.filter((t)=>{return t == "'self'"}));

        for (let i=0; i<this.sourceList.length; i++) {
            if (this._isHostSource(this.sourceList[i])) {
                let tmp = Directive._normalizeHostSource(this.sourceList[i]);
                let o = url.parse(tmp, false, true);
                let result = this.l7hosts.filter((t) => {return t == o.hostname});

                if (result.length > 0) {
                    untrusted.push(...result);
                }
            }
        }

        if (untrusted.length > 0) {
            let v = new Issue(this.__("issueSameOrigin", this.name, untrusted.join(", ")), Severity.MEDIUM, 'sameorigin', this.name);
            issues.push(v);
        }

        return issues;
    }

    /**
     * Find all vulnerabilities in child directive
     */
    _findIssues() {
        return [];
    }
    
    /**
     * Find all vulnerabilities in directive
     */
     findIssues() {
        let issues = [];
        if (!this.isStrictDynamicEnabled()) {
            issues.push(...this._findWildcardIssues(Severity.MEDIUM));
            issues.push(...this._findWildcardSubdomainIssues(Severity.HIGH));
            issues.push(...this._checkSourceLimit());
            issues.push(...this._checkUntrustedSources());
            issues.push(...this._checkDataSource());
        }

        issues.push(...this._findEvalIssues());
        issues.push(...this._findIssues());
        issues.push(...this._findWeakNoncesIssues());
        
        // TODO(buglloc): enable me back
        // issues.push(...this._findSameOriginIssues());

        let noncesHashes = this.getNoncesHashes();
        if (this.isUnsafeInlineEnabled() && noncesHashes.length == 0) {
            let severity = (this.name == 'script-src' ? Severity.HIGH : Severity.LOW);
            let v = new Issue(this.__("issueInline", this.name), severity, 'inline', this.name);
            issues.push(v);
        }
        
        issues.push(...this.syntaxErrors);
        return sortIssues(issues);
     }
}

class DefaultSrcDirective extends Directive {
    constructor() {
        super('default-src');
        this.strictness = 0;

    }

    /**
     * Set smaller value because of risky nature of the directive.
     */ 
    set sourceLimit(value) {
        this._sourceLimit = parseInt(value/2);
    }

    _findIssues() {
        let issues = [];

        if (!this.strictness) {
            return issues;
        }
        
        let strictnessLevels = [
            {
            'level': 1,
            'value':"'self'"
            },
            {
            'level': 2,
            'value':"'none'"
            }];
        
        strictnessLevels.forEach((item, i, arr) => {
            if (this.strictness == item.level) { 
                if (this.sourceList.length > 1 || (this.sourceList.length == 1 && this.sourceList[0] != item.value)) {
                    let issue = new Issue(this.__("issueStrictness", item.value), Severity.HIGH, 'defaultSrcStrictness', this.name);
                        issues.push(issue);
                }
            }
        }, this);
        return issues;
    }
}

class ScriptSrcDirective extends Directive {
    constructor(name) {
        super(name || 'script-src');
    }
    /**
     * Set smaller value because of risky nature of the directive.
     */ 
    set sourceLimit(value) {
        this._sourceLimit = parseInt(value/2);
    }
}

class SandboxDirective extends Directive {
    constructor() {
        super('sandbox');
        this.flags = [];
    }

    initValue(directiveValue) {
        this.flags = this._parseFlagList(directiveValue);
        this.value = directiveValue;
        return true;
    }

    static _isValidFlag(flag) {
        let valid_flags = [
            'allow-forms', 'allow-pointer-lock', 
            'allow-popups', 'allow-same-origin', 
            'allow-scripts', 'allow-top-navigation'
        ];

        if (valid_flags.indexOf(flag) != -1) {
            return true;
        } else {
            return false;
        }
    }

    _parseFlagList(directiveValue) {
        let flag_list = directiveValue.trim();
        let result = [];
        flag_list.split(" ").forEach((flag, i, arr) => {
            if (SandboxDirective._isValidFlag(flag)) {
                result.push(flag);
            }
        }, this);
        return result;
    }
}

/**
 * See also https://www.w3.org/TR/CSP/#media-type-list-syntax
 */
class PluginTypesDirective extends Directive {
    constructor() {
        super('plugin-types');
        this.mediaTypeList = [];
        // We should use here list from RFC 2045
        // but we use short version of the list of types which are important for web
        this.validMediaTypes = [
        "application/xhtml+xml", "audio/webm", "text/html", "application/json", "audio/ogg", "text/css", "video/ogg", "font/woff", "image/svg+xml", "audio/aac", "image/tiff", "text/calendar", "application/xml", "image/x-icon", "font/woff2", "application/java-archive", "application/octet-stream", "application/msword", "application/pdf", "application/zip", "video/webm", "application/javascript", "application/ogg", "image/jpeg", "video/mpeg", "audio/midi", "font/ttf", "image/gif", "application/x-shockwave-flash", "image/webp", "text/csv"
        ];
    }

    initValue(directiveValue) {
        directiveValue = directiveValue.trim();
        if (!directiveValue) {
            return false;
        }
        this.mediaTypeList = this._parseMediaTypeList(directiveValue);
        this.value = directiveValue;
        return true;
    }

    _isValidMediaType(mediaType) {
        if (this.validMediaTypes.indexOf(mediaType.toLowerCase()) != -1) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * See also https://www.w3.org/TR/CSP/#media-type-list-parsing
     */
    _parseMediaTypeList(directiveValue) {
        let mediaTypeList = directiveValue.trim();
        let result = [];
        mediaTypeList.split(" ").forEach((mediaType, i, arr) => {
            if (this._isValidMediaType(mediaType)) {
                result.push(mediaType);
            }
        }, this);
        return result;
    }
}


/**
 * See also https://w3c.github.io/webappsec-mixed-content/#directive-initialization
 */
class BlockAllMixedContentDirective extends Directive {
    constructor() {
        super('block-all-mixed-content');
    }

    initValue(directiveValue) {
        return true;
    }
}

/**
 * See also https://w3c.github.io/webappsec/specs/upgrade/#delivery
 */
class UpgradeInsecureRequestsDirective extends Directive {
    constructor() {
        super('upgrade-insecure-requests');
    }

    initValue(directiveValue) {
        return true;
    }
}

/**
 * See also https://w3c.github.io/webappsec/specs/subresourceintegrity/#opt-in-require-sri-for
 */
class RequireSriForDirective extends Directive {
    constructor() {
        super('require-sri-for');
        this.script = false;
        this.style = false;
    }

    initValue(directiveValue) {
        directiveValue = directiveValue.trim();
        if (!directiveValue) {
            return false;
        }

        directiveValue.split(' ').forEach((resource, i, arr) => {
            if (resource === 'script') {
                this.script = true;
            } else if (resource === 'style') {
                this.style = true;
            }
        }, this);
        return true;
    }
}

/**
 *  Represents policy from Content Security Policy Level 2
 *  https://www.w3.org/TR/CSP2/
 */
class Policy {
    constructor() {
        this.value = "";
        this.directives = [];
        this.version = 2;
        this.reportOnly = false;
        this.syntaxErrors = [];
        this.trustedHosts = [];
        this.l7hosts = [];
        this.reportNoReportUri = false;
        this.reportEval = true;
        this.sourceLimit = null;
        this.defaultSrcStrictness = 0;
        this.reportNotFallback = false;
        this.__ = (m) => {return m};
    }
   
    initValue(policy) {
        let stringPolicy = policy.trim();
        if (!stringPolicy) {
            return false;
        }
        if (this._parsePolicy(stringPolicy)) {
            this.value = policy;
            return true;
        } else {
            return false;
        }
    }

    /**
     * Parse CSP policy and set list of directives.
     * See also https://www.w3.org/TR/CSP/#policy-parsing
     */
    _parsePolicy(policy) {
        this.directives = [];
        let result = [];
        let tokens = policy.split(';').map((x)=>{return x.trim()});
        tokens = tokens.filter((x)=>{return x.trim()});


        for (let i=0; i<tokens.length; i++) {
            let directiveValue = '';
            let chunks = tokens[i].trim().split(' ');
            let directiveName = chunks[0];

            if (chunks.length > 1) {
                directiveValue = chunks.slice(1).join(' ');
            }
            let directive = this.makeDirective(directiveName);
           
            if (!directive) {
                this.syntaxErrors.push(
                    new Issue(this.__("issueParseDirective", directiveName), Severity.HIGH, 'syntax', ''));
                continue;
            }
            // FIXME check for existing 
            // directive instance in result
            if (directive.initValue(directiveValue)){
                result.push(directive);
            }
        }
        if (result.length > 0) {
            this.directives = result;
            return true;
        } else {
            return false;
        }
    }
  
    static getSourceDirectiveNames() {
        return [
            'style-src', 'img-src', 'connect-src', 'child-src', 'font-src',
            'form-action', 'frame-ancestors', 'frame-src', 'media-src',
            'object-src', 'base-uri', 'report-uri', 'manifest-src',
            'worker-src', 'style-src-elem', 'style-src-attr',
        ];
    }

    static getScriptDirectiveNames() {
        return [
            "script-src", "script-src-elem", "script-src-attr",
        ]
    }

    static getSpecialDirectiveNames() {
        return [
            ...this.getScriptDirectiveNames(),
            'default-src', 'sandbox', 'plugin-types', 'block-all-mixed-content',
            'upgrade-insecure-requests', 'require-sri-for',
        ];
    }

    static getDirectiveNames() {
         return [
             ...this.getSourceDirectiveNames(),
             ...this.getSpecialDirectiveNames(),
         ]
    }

    makeDirective(directiveName) {
        let directive = null;
        directiveName = directiveName.toLowerCase();

        if (Policy.getSourceDirectiveNames().indexOf(directiveName) != -1) {
            directive = new Directive(directiveName);
        } else if ("default-src" == directiveName) {
            directive = new DefaultSrcDirective();
            directive.strictness = this.defaultSrcStrictness;
        } else if (Policy.getScriptDirectiveNames().indexOf(directiveName) != -1) {
            directive = new ScriptSrcDirective(directiveName);
        } else if ("sandbox" == directiveName) {
            directive = new SandboxDirective();
        } else if ("plugin-types" == directiveName) {
            directive = new PluginTypesDirective();
        } else if ("block-all-mixed-content" == directiveName) {
            directive = new BlockAllMixedContentDirective();
        } else if ("upgrade-insecure-requests" == directiveName) {
            directive = new UpgradeInsecureRequestsDirective();
        } else if ("require-sri-for" == directiveName) {
            directive = new RequireSriForDirective();
        }

        if (directive) {
            directive.sourceLimit = this.sourceLimit;
            directive.trustedHosts = this.trustedHosts;
            directive.l7hosts = this.l7hosts;
            directive.reportEval = this.reportEval;
            directive.__ = this.__;
            return directive;
        } else {
            return null;
        }
    }

    getStringPolicy(pretty=false, includeHeaderName=false) {
        let delim = pretty ? "\n" : ' ';
        let result = '';

        let tmp = this.directives.map((item, i, arr) => {
            return this.directives[i].name + ' ' + this.directives[i].value.trim();
        });

        if (includeHeaderName) {
            result += this.getHeaderName() + ':' + delim;
            delim += '  ';
        }

        result += tmp.join(";" + delim);
        return result;
    }
    
    getHeaderName(reportOnly=false) {
        let headerName = "Content-Security-Policy";
        if (this.reportOnly || reportOnly) {
            headerName += "-Report-Only";
        }
        return headerName;
    }

    getDirectiveByName(directiveName) {
        for (let i=0; i<this.directives.length; i++) {
            if (this.directives[i].name.toLowerCase() == directiveName.toLowerCase()) {
                return this.directives[i];
            }
        }
        return null;
    }
   
    /**
     * Find all vulnerabilities in all directives
     */
    findIssues() {
        let issues = [];

        this.directives.forEach((d, i, arr) => {
            let dIssues = d.findIssues();
            if (dIssues.length > 0) {
                issues.push(...dIssues);
            }
        }, this);
        
        // Check if report-uri exists
        if (this.reportNoReportUri && ! this.getReportUri()) {
            issues.push(new Issue(this.__("issueNoReportUri"), Severity.LOW, 'report_uri_required', 'report-uri'));
        }

        // Check directives which does not fall back to the default sources
        let notFallbackDirectives = ['frame-ancestors', 'form-action', 'base-uri'];
        if (this.reportNotFallback) {
            notFallbackDirectives.forEach((d, i, arr) => {
                if (!this.getDirectiveByName(d)) {
                        let issue = new Issue(this.__("issueRequired", d), Severity.MEDIUM, 'required', d);
                    issues.push(issue);
                }
            }, this);
        }

        // Check default-src
        if (!this.getDirectiveByName('default-src')) {
            let issue = new Issue(this.__("issueDefault"), Severity.MEDIUM, 'default_required', 'default-src');
            issues.push(issue);
        }

        issues.push(...this.syntaxErrors);
        return sortIssues(issues);
    }

    findIssuesByDirective(directiveName) {
        let result = [];
        let issues = this.findIssues();

        issues.forEach((v, i, arr) => {
            if (v.directive == directiveName) {
                result.push(v);
            }
        }, this);

        return result;
    }

    getReportUri() {
        let reportUri = this.getDirectiveByName('report-uri');
        if (reportUri) {
            return reportUri.value;
        } else {
            return null;
        }
    }
    
    getNonces() {
        let result = [];
        this.directives.forEach((d, i, arr) => {
            result.push(...d.getNoncesHashes(true, false));
        }, this);
        return result;
    }

    isUnsafeInlineEnabled() {
        let result = false;
        let directiveNames = [...Policy.getScriptDirectiveNames(), 'style-src'];

        directiveNames.forEach((dName, i, arr) => {
            let d = this.getDirectiveByName(dName);
            if (d && d.isUnsafeInlineEnabled()) {
                result = true;
            }
        }, this);

        return result;
    }

    /**
     * Check if policy protects against XSS.
     * See also https://www.w3.org/TR/CSP2/#directives
     */
    protectsAgainstXss() {
        if (!this.directives || this.reportOnly) {
            return false;
        }
       
        let riskyDirectives = [];
        let defaultSrc = this.getDirectiveByName('default-src');
        ['script-src', 'script-src-elem', 'object-src'].forEach((n, i, arr) => {
            riskyDirectives.push(this.getDirectiveByName(n));
        }, this);
        
        // must be enabled defaultSrc or **all** risky directives
        if (!(defaultSrc || riskyDirectives.reduce((x, y)=>{return (!!x && !!y)})
        )) {
            return false;
        }

        let result = true;

        riskyDirectives.forEach((rd, i, arr) => {
            let d = null;
            if (rd) {
                d = rd;
            } else {
                d = defaultSrc;
            }
            let issues = d.findIssues();
            issues.forEach((issue, i, arr) => {
                if (issue.severity instanceof HighSeverity) {
                    result = false;
                }
            });
        
        }, this);

        return result;
    }
}

class FetcherError extends Error {

}

class Fetcher {
    constructor(trustedHosts = []) {
        this.trustedHosts = trustedHosts;
        this.trustedPorts = ['80', '443'];
        this.trustedSchemes = ['http:', 'https:'];
    }

    static getPolicyFromMetaTags(htmlBody) {
        let result = [];
        let marker = '<meta http-equiv="Content-Security-Policy" content="';
        let marketPos = htmlBody.indexOf(marker);

        if (marketPos == -1) {
            return result;
        }

        let endPos = htmlBody.indexOf('"', marketPos + marker.length);
        result.push(htmlBody.substring(marketPos + marker.length, endPos));
        return result;
    }

    static getPolicyFromHeaders(headers) {
        // prioritize CSP over CSP in report only mode
        let csp = headers["content-security-policy"] || headers["content-security-policy-report-only"];
        if (csp) {
            return [csp];
        }
        return [];
    }

    getPolicy(cspUrl) {
        return new Promise((resolve, reject) => {
            let o = url.parse(cspUrl, false, true);

            if (!o.hostname) {
                reject(new FetcherError("Can't get CSP from target URL1"));
                return;
            }

            let tmp = this.trustedSchemes.filter((item) => {return item == o.protocol});

            if (tmp.length == 0) {
                reject(new FetcherError("Can't get CSP from target URL"));
                return;
            }

            tmp = this.trustedPorts.filter((item) => {return item == o.port});

            if (o.port != null && tmp.length == 0) {
                reject(new FetcherError("Can't get CSP from target URL"));
                return;
            }
            // We allow only trusted hosts or subdomains of trusted hosts
            tmp = this.trustedHosts.filter((item) => {
                return o.host.endsWith('.' + item) || o.host == item;
            });

            if (this.trustedHosts.length > 0 && tmp.length == 0) {
                reject(new FetcherError("Can't get CSP from target URL"));
                return;
            }

            let options = {
                "timeout": 3000,
                "followRedirect": false,
            };

            got(cspUrl, options).then((response) => {
                let cspValues = [];
                if (((response.statusCode / 100) >> 0) === 3) {
                    reject(new FetcherError("Can't get CSP from target URL. Because of redirection to: " + response.headers['location']));
                    return;
                }

                cspValues.push(...Fetcher.getPolicyFromMetaTags(response.body));
                cspValues.push(...Fetcher.getPolicyFromHeaders(response.headers));

                // FIXME
                // It is possible when we have more then one CSP header
                if (cspValues.length > 0) {
                    resolve(cspValues[0]);
                } else {
                    reject(new FetcherError("Can't get CSP from target URL"));
                    return;
                }

            }).catch((error) => {
                reject(new FetcherError("Can't get CSP from target URL. Because of: " + error.message));
            });
        });
    }
}

exports.Policy = Policy;
exports.Directive = Directive;
exports.Fetcher = Fetcher;
exports.FetcherError = FetcherError;
