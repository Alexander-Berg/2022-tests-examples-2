limiter_agent = require 'rate-limiter'

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
    -- return'request('..tbl2string(reqParams, {'method','path','query','headers','body'})..')'
end

local function str2codes(s)
    local codes = ''
    for c in s:gmatch'.' do
        if codes ~= '' then
            codes = codes .. ','    -- separator
        end
        codes = codes ..string.byte(c)
    end
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

---------------------------------------------------------------
-- test set configs
local plush_http = {
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

local ok, err = limiter_agent.update_configs(plush_http)
assert(ok == limiter_agent.codes.OK)
local configs = limiter_agent.get_configs()
assert(configs and configs.TVM_ID == '123' and configs.TVM_ENABLED == '1')

---------------------------------------------------------------
-- test update_limits err result
local plush_http = {
    request = response_method,
    read_body = read_body_method,
    response = nil,
}

local ok, err = limiter_agent.update_limits(plush_http)
assert(ok == limiter_agent.codes.ERR)
assert(err == 'HTTP 503')
assert(plush_http.log == 'request({headers={Connection=keep-alive},method=GET,path=/limits})',
    'Test sync_limits err failed, log:' .. plush_http.log)


---------------------------------------------------------------
-- test rate_access (while no limits loaded)
local ret = limiter_agent.rate_access('client.1', 'resource.5', 10)
assert(ret == limiter_agent.codes.OK)
local ret = limiter_agent.rate_access('some.client', 'some.resource', 1)
assert(ret == limiter_agent.codes.OK)

---------------------------------------------------------------
-- test update_counters
local plush_http = {
    request = response_method,
    read_body = read_body_method,
    response = {
        body = '', -- empty counters update from server
        status = 200
    },
}

local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.OK)

local expectedPayload = '\16\0\0\0\0\0\10\0\20\0\4\0\0\0\8\0\10\0\0\0\16\0\0\0'..
        '\1\0\0\0\0\0\0\0\0\0\0\0\2\0\0\0\100\0\0\0\4\0\0\0\172\255\255\255\16'..
        '\0\0\0\4\0\0\0\1\0\0\0\32\0\0\0\13\0\0\0\115\111\109\101\46\114\101'..
        '\115\111\117\114\99\101\0\0\0\8\0\20\0\4\0\8\0\8\0\0\0\16\0\0\0\1\0\0'..
        '\0\0\0\0\0\0\0\0\0\11\0\0\0\115\111\109\101\46\99\108\105\101\110\116'..
        '\0\8\0\12\0\4\0\8\0\8\0\0\0\16\0\0\0\4\0\0\0\1\0\0\0\28\0\0\0\10\0\0'..
        '\0\114\101\115\111\117\114\99\101\46\53\0\0\8\0\16\0\4\0\8\0\8\0\0\0'..
        '\12\0\0\0\10\0\0\0\0\0\0\0\8\0\0\0\99\108\105\101\110\116\46\49\0\0\0\0'
-- pre-serialized counters message {
-- {'some.resource', {{ 'some.client', 1 }}}
-- {'resource.5', {{'client.1', 10 }}}
-- }
-- limits version: 0, lamport: 1
local body = string.match(plush_http.log, 'request%(%{body=(.*),headers=%{'..
        'Connection=keep%-alive,Content%-Type=application/flatbuffer%},'..
        'method=POST,path=/sync,query=%{shard=worker1%}%}%)')
-- NB: no version parameter 'cause no limits set yet
local ok, err = limiter_agent.compare_counters(expectedPayload, body)
assert(ok == limiter_agent.codes.OK)

---------------------------------------------------------------
-- test update_limits success
local plush_http = {
    request = response_method,
    read_body = read_body_method,
    response = {
    -- pre-serialized 'any client' limits {
    -- {resource = 'resource.1', rps=10, burst=5, unit=1},
    -- {resource = 'resource.forbidden', rps=0, burst=0, unit=1}},
    -- version = 1 }
        body = '\16\0\0\0\0\0\0\0\8\0\20\0\4\0\8\0\8\0\0\0\16\0\0\0\1\0\0\0\0'..
                '\0\0\0\0\0\0\0\2\0\0\0\80\0\0\0\20\0\0\0\0\0\14\0\24\0\4\0\8'..
                '\0\12\0\16\0\20\0\14\0\0\0\20\0\0\0\88\0\0\0\10\0\0\0\5\0\0'..
                '\0\1\0\0\0\10\0\0\0\114\101\115\111\117\114\99\101\46\49\0\0'..
                '\0\0\14\0\16\0\4\0\8\0\0\0\0\0\12\0\14\0\0\0\12\0\0\0\32\0\0'..
                '\0\1\0\0\0\18\0\0\0\114\101\115\111\117\114\99\101\46\102\111'..
                '\114\98\105\100\100\101\110\0\0\0\0\0\0\0\0\0\0',
        status = 200
    },
}

local ok, err = limiter_agent.update_limits(plush_http)
assert(plush_http.log ==
        'request({headers={Connection=keep-alive},method=GET,path=/limits})',
        'Test failed, log:' .. plush_http.log)
assert(ok == limiter_agent.codes.OK)
assert(not err)

---------------------------------------------------------------
-- test rate_access
local ret = limiter_agent.rate_access('client.1', 'resource.1', 1)
assert(ret == limiter_agent.codes.OK)

local ret = limiter_agent.rate_access('client.1', 'resource.1', 2)
assert(ret == limiter_agent.codes.OK)

local ret = limiter_agent.rate_access('client.1', 'resource.1', 5)
assert(ret == limiter_agent.codes.LIMIT_EXCEEDED)

local ret = limiter_agent.rate_access('client.2', 'resource.1', 5)
assert(ret == limiter_agent.codes.OK)

local ret = limiter_agent.rate_access('client.2', 'resource.not.defined', 1)
assert(ret == limiter_agent.codes.OK)

local ret = limiter_agent.rate_access('client.1', 'resource.forbidden', 1)
assert(ret == limiter_agent.codes.FORBIDDEN)

---------------------------------------------------------------
-- test update_counters success
local plush_http = {
    request = response_method,
    read_body = read_body_method,
    response = {
        body = '', -- empty counters update from server
        status = 200
    },
}

local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.OK)
-- pre-serialized counters {
--  {'resource.1', {{ 'client.1', 3 }, {'client.2', 5}}
--  {'some.resource', {{ 'some.client', 1 }}}
--  {'resource.5', {'client.1', 10 }}
-- }
-- limits version: 1, lamport: 2
local expectedPayload = '\16\0\0\0\0\0\10\0\24\0\4\0\8\0\16\0\10\0\0\0\20\0\0'..
        '\0\1\0\0\0\0\0\0\0\2\0\0\0\0\0\0\0\3\0\0\0\156\0\0\0\92\0\0\0\4\0\0\0'..
        '\120\255\255\255\16\0\0\0\4\0\0\0\1\0\0\0\32\0\0\0\13\0\0\0\115\111'..
        '\109\101\46\114\101\115\111\117\114\99\101\0\0\0\8\0\20\0\4\0\8\0\8\0'..
        '\0\0\16\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0\11\0\0\0\115\111\109\101\46\99'..
        '\108\105\101\110\116\0\204\255\255\255\16\0\0\0\4\0\0\0\1\0\0\0\20\0'..
        '\0\0\10\0\0\0\114\101\115\111\117\114\99\101\46\53\0\0\160\255\255'..
        '\255\76\0\0\0\10\0\0\0\0\0\0\0\8\0\12\0\4\0\8\0\8\0\0\0\20\0\0\0\4\0'..
        '\0\0\2\0\0\0\64\0\0\0\20\0\0\0\10\0\0\0\114\101\115\111\117\114\99'..
        '\101\46\49\0\0\224\255\255\255\12\0\0\0\3\0\0\0\0\0\0\0\8\0\0\0\99'..
        '\108\105\101\110\116\46\49\0\0\0\0\8\0\16\0\4\0\8\0\8\0\0\0\12\0\0'..
        '\0\5\0\0\0\0\0\0\0\8\0\0\0\99\108\105\101\110\116\46\50\0\0\0\0'
local body = string.match(plush_http.log, 'request%(%{body=(.*),headers=%{'..
        'Connection=keep%-alive,Content%-Type=application/flatbuffer%},'..
        'method=POST,path=/sync,query=%{shard=worker1%}%}%)')
local ok, err = limiter_agent.compare_counters(expectedPayload, body)
assert(ok == limiter_agent.codes.OK)


---------------------------------------------------------------
-- test garbage collect counters
local ok = limiter_agent.garbage_collect_counters()
assert(ok == limiter_agent.codes.OK)
-- check no counters left (by calling update_counters)
local plush_http = {
    request = response_method,
    read_body = read_body_method,
    response = { body = '',  status = 200 },
}
local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.OK)
-- pre-serialized counters {
--   {"resource.1", {}},
--   {"some.resource", {}},
--   {"resource.5", {}},
-- }
-- limits version: 1, lamport: 3
local expectedPayload = '\16\0\0\0\0\0\10\0\28\0\4\0\8\0\16\0\10\0\0\0\24\0\0'..
        '\0\1\0\0\0\0\0\0\0\3\0\0\0\0\0\0\0\0\0\0\0\3\0\0\0\88\0\0\0\44\0\0\0'..
        '\4\0\0\0\188\255\255\255\12\0\0\0\4\0\0\0\0\0\0\0\13\0\0\0\115\111'..
        '\109\101\46\114\101\115\111\117\114\99\101\0\0\0\224\255\255\255\12'..
        '\0\0\0\4\0\0\0\0\0\0\0\10\0\0\0\114\101\115\111\117\114\99\101\46\53'..
        '\0\0\8\0\12\0\4\0\8\0\8\0\0\0\12\0\0\0\4\0\0\0\0\0\0\0\10\0\0\0\114'..
        '\101\115\111\117\114\99\101\46\49\0\0'
-- pre-serialized empty resource entries
local body = string.match(plush_http.log, 'request%(%{body=(.*),headers=%{'..
        'Connection=keep%-alive,Content%-Type=application/flatbuffer%},'..
        'method=POST,path=/sync,query=%{shard=worker1%}%}%)')
-- NB: no version parameter 'cause no limits set yet
local ok, err = limiter_agent.compare_counters(expectedPayload, body)
assert(ok == limiter_agent.codes.OK)


---------------------------------------------------------------
-- test update_counters server err
local plush_http = {
    request = response_method,
    response = nil,
}
local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.ERR)
assert(err == 'HTTP 503')
-- pre-serialized counters {
--   {"resource.1", {}},
--   {"some.resource", {}},
--   {"resource.5", {}},
-- }
-- limits version: 1, lamport: 4
local expectedPayload = '\16\0\0\0\0\0\10\0\28\0\4\0\8\0\16\0\10\0\0\0\24\0\0'..
        '\0\1\0\0\0\0\0\0\0\4\0\0\0\0\0\0\0\0\0\0\0\3\0\0\0\88\0\0\0\44\0\0\0'..
        '\4\0\0\0\188\255\255\255\12\0\0\0\4\0\0\0\0\0\0\0\13\0\0\0\115\111'..
        '\109\101\46\114\101\115\111\117\114\99\101\0\0\0\224\255\255\255\12'..
        '\0\0\0\4\0\0\0\0\0\0\0\10\0\0\0\114\101\115\111\117\114\99\101\46\53'..
        '\0\0\8\0\12\0\4\0\8\0\8\0\0\0\12\0\0\0\4\0\0\0\0\0\0\0\10\0\0\0\114'..
        '\101\115\111\117\114\99\101\46\49\0\0'
local body = string.match(plush_http.log, 'request%(%{body=(.*),headers=%{'..
        'Connection=keep%-alive,Content%-Type=application/flatbuffer%},'..
        'method=POST,path=/sync,query=%{shard=worker1%}%}%)')
-- NB: no version parameter 'cause no limits set yet
local ok, err = limiter_agent.compare_counters(expectedPayload, body)
assert(ok == limiter_agent.codes.OK)

---------------------------------------------------------------
-- test limits update on 409 from server /sync
local plush_http = {
    log = '',
    request = function(self, params)
        self.log = self.log .. req2string(params)
        if params.path == '/sync' then
            self.status = 409
        else
            self.status = 200
        end
        return self
    end,
    -- serialized limitsVersion = 42
    read_body = function(self) return '\12\0\0\0\8\0\8\0\0\0\4\0\8\0\0\0\42\0\0\0' end,
}
local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.LIMITS_CONFLICT)

---------------------------------------------------------------
-- test lamport

local plush_http = {
    log = '',
    request = function(self, params)
        self.log = self.log .. req2string(params)
        self.status = 200
        return self
    end,
    -- serialized lamport 123
    read_body = function(self) return '\20\0\0\0\0\0\0\0\0\0\10\0\20\0\0\0\4\0'..
            '\12\0\10\0\0\0\1\0\0\0\0\0\0\0\123\0\0\0\0\0\0\0' end,
}

-- agent gets new lamport, and next time sends incremented
local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.OK)

plush_http.request = function(self, params)
    self.log = self.log .. req2string(params)
    -- pre-serialized empty resource entries with limitsVersion = 1, lamport = 124
    local expectedPayload = '\16\0\0\0\0\0\10\0\28\0\4\0\8\0\16\0\10\0\0\0\24'..
            '\0\0\0\1\0\0\0\0\0\0\0\124\0\0\0\0\0\0\0\0\0\0\0\3\0\0\0\88\0\0\0'..
            '\44\0\0\0\4\0\0\0\188\255\255\255\12\0\0\0\4\0\0\0\0\0\0\0\13\0\0'..
            '\0\115\111\109\101\46\114\101\115\111\117\114\99\101\0\0\0\224\255'..
            '\255\255\12\0\0\0\4\0\0\0\0\0\0\0\10\0\0\0\114\101\115\111\117'..
            '\114\99\101\46\53\0\0\8\0\12\0\4\0\8\0\8\0\0\0\12\0\0\0\4\0\0\0'..
            '\0\0\0\0\10\0\0\0\114\101\115\111\117\114\99\101\46\49\0\0'
    local ok, err = limiter_agent.compare_counters(expectedPayload, params.body)
    assert(ok == limiter_agent.codes.OK)
    self.status = 200
    -- ratelimiter proxy accepted incremented lamport
    self.read_body = function(self) return '\20\0\0\0\0\0\0\0\0\0\10\0\20\0\0'..
            '\0\4\0\12\0\10\0\0\0\1\0\0\0\0\0\0\0\124\0\0\0\0\0\0\0' end
    return self
end

local ok, err = limiter_agent.update_counters(plush_http)
assert(ok == limiter_agent.codes.OK)
