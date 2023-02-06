local limiter_agent = require 'rate-limiter'
local capi = require 'libratelimiter_agent2'
local cfg = require 'rate-limiter-conf'
local utils = require 'utils'

-- test helpers

local function tbl2string(T, sortedKeys)

    if not sortedKeys then
        sortedKeys = {}
        for key in pairs(T) do table.insert(sortedKeys, key) end
        table.sort(sortedKeys)
    end

    local str = ''
    for _, key in ipairs(sortedKeys) do
        local val = T[key]
        if val then
            if str ~= '' then str = str .. ','  end -- separator

            if type(val) == 'table' then
                str = str .. key .. '=' .. tbl2string(val)
            else
                str = str .. key .. '=' .. val
            end
        end
    end
    return '{' .. str .. '}'
end

local function req2string(reqParams)
    return'request('..tbl2string(reqParams)..')'
end

local function response_method(self, params)
    if not self.log then self.log = '' end

    self.log = self.log .. req2string(params)

    if not self.response then
        return nil, 'HTTP 503'
    else
        self.status = self.response.status
        return self
    end
end

local function read_body_method(self)
    return self.response.body
end

-- set shard identifier
limiter_agent.shard_id = 'worker1'

-- mock ngx
ngx = {
    log = print
}

-------------------------------------------------------------
-- test set configs
local mock_http = {
    request = response_method,
    read_body = read_body_method,
    response = {
        -- pre-serialized configs:
        --   TVM_ID = 123
        --   TVM_ENABLED = 1
        body = '\12\0\0\0\0\0\6\0\8\0\4\0\6\0\0\0\4\0\0\0'..
                '\2\0\0\0\48\0\0\0\4\0\0\0\224\255\255\255'..
                '\16\0\0\0\4\0\0\0\3\0\0\0\49\50\51\0\6\0'..
                '\0\0\84\86\77\95\73\68\0\0\8\0\12\0\4\0'..
                '\8\0\8\0\0\0\16\0\0\0\4\0\0\0\1\0\0\0\49'..
                '\0\0\0\11\0\0\0\84\86\77\95\69\78\65\66'..
                '\76\69\68\0',
        status = 200
    }
}

local ok, err = limiter_agent.update_configs(mock_http)
assert(ok == limiter_agent.codes.OK)
local configs = limiter_agent.get_configs()
assert(configs and configs.TVM_ID == '123' and configs.TVM_ENABLED == '1')

---------------------------------------------------------------

local mock_http = {
    request = response_method,
    read_body = read_body_method,
    response = {
        body = '',
        status = 200
    },
}

local function set_mock_response(response)
    mock_http.response.body = response
    -- get fresh quota from the server
    local ret = limiter_agent.get_quota(mock_http, cfg.QUOTA_HTTP_SETTINGS, '', '')
    assert(ret == limiter_agent.codes.OK)
end

local function rate_access(client, resource, value)
    return limiter_agent.rate_access(client, resource, value)['status']
end

set_mock_response(utils.make_mock_body('client.1', 'resource.1', 10))
-- test rate_access
assert(rate_access('client.1', 'resource.1', 1) == limiter_agent.check_status.ALLOWED)
-- spend whole quota
assert(rate_access('client.1', 'resource.1', 9) == limiter_agent.check_status.ALLOWED)
-- no more quota - need to refresh
assert(rate_access('client.1', 'resource.1', 1) == limiter_agent.check_status.REQUEST_QUOTA)

set_mock_response(utils.make_mock_body('client.1', 'resource.1', 0))
-- received 0 quota, rejecting
assert(rate_access('client.1', 'resource.1', 1) == limiter_agent.check_status.LIMIT_EXCEEDED)
-- not received yet
assert(rate_access('client.2', 'resource.1', 5) == limiter_agent.check_status.REQUEST_QUOTA)

set_mock_response(utils.make_mock_body('client.2', 'resource.not.defined', -2))
assert(rate_access('client.2', 'resource.not.defined', 1) == limiter_agent.check_status.ALLOWED)

set_mock_response(utils.make_mock_body('client.2', 'resource.forbidden', -1))
assert(rate_access('client.2', 'resource.forbidden', 1) == limiter_agent.check_status.FORBIDDEN)

set_mock_response(utils.make_mock_body('client.1', [[regexp/test\\d+]], 2, true))

assert(rate_access('client.1', 'regexp/test1', 1) == limiter_agent.check_status.ALLOWED)
assert(rate_access('client.1', 'regexp/test2', 1) == limiter_agent.check_status.ALLOWED)
assert(rate_access('client.1', 'regexp/test3', 1) == limiter_agent.check_status.REQUEST_QUOTA)

-- test default path and client

set_mock_response(utils.make_mock_body('client.3', [[/test/specific[\\w]+]], 10, true))
set_mock_response(utils.make_mock_body('client.3', '', -1))
set_mock_response(utils.make_mock_body('', '/test/default', 0))

assert(rate_access('client.3', '/test/specific_test', 1) == limiter_agent.check_status.ALLOWED)
assert(rate_access('client.3', '/test/does/not/match', 1) == limiter_agent.check_status.FORBIDDEN)
-- default path has higher priority than default client
assert(rate_access('client.3', '/test/default', 1) == limiter_agent.check_status.FORBIDDEN)
assert(rate_access('client.4', '/test/default', 1) == limiter_agent.check_status.LIMIT_EXCEEDED)

-- test not existing rule is overwritten by regex rule

set_mock_response(utils.make_mock_body('client.4', '/v1/cached-value/test2', -2))
assert(rate_access('client.4', '/v1/cached-value/test2', 1) == limiter_agent.check_status.ALLOWED)

-- set regex rule now, which shall overwrite not existing resource
set_mock_response(utils.make_mock_body('client.4', [[/v1/cached-value/\\w+]], -1, true))
assert(rate_access('client.4', '/v1/cached-value/test2', 1) == limiter_agent.check_status.FORBIDDEN)

-- test handler_name
set_mock_response(utils.make_mock_body('client.5', 'resource', 1, false, 'my_handler_name'))
result = limiter_agent.rate_access('client.5', 'resource', 1)
assert(result['status'] == limiter_agent.check_status.ALLOWED)
assert(result['handler_name'] == 'my_handler_name')
