require 'package'
local test_module = require "test_module"

assert(test_module.NS_CONST_A == "const string", "problem with exported const")
assert(test_module.NS_CONST_B == "const string_view", "problem with exported const")
assert(test_module.ns_to_lua_number("42.000") == 42,  "problem with marshaling lua_Number")
assert(test_module.ns_to_lua_integer("43") == 43,  "problem with marshaling lua_Integer")
assert(test_module.ns_to_int("44") == 44,  "problem with marshaling int")

-- table marshaling

function table_compare(tbl1, tbl2)
    for k, v in pairs(tbl1) do
        if (type(v) == "table" and type(tbl2[k]) == "table") then
            if (not table_compare(v, tbl2[k])) then return false end
        else
            if (v ~= tbl2[k]) then return false end
        end
    end
    for k, v in pairs(tbl2) do
        if (type(v) == "table" and type(tbl1[k]) == "table") then
            if (not table_compare(v, tbl1[k])) then return false end
        else
            if (v ~= tbl1[k]) then return false end
        end
    end
    return true
end

-- test invalid value type in table (expected nested table)
assert (not pcall(test_module.ns_merge_nested, { a = '153' }, {}))

assert(table_compare(test_module.ns_merge_nested({}, {}), {}),"problem with marshaling table")

assert(
    table_compare(
        test_module.ns_merge_nested({ A = {} }, { B = {} }),
        { A = {}, B = {} }
    ),
    "problem with marshaling table"
)

assert(
    table_compare(
        test_module.ns_merge_nested(
            { A = { AA = '1' }, C = { CC1 = '2', CC2 = '3' } },
            { B = { BB = '11' }, C = { CC1 = '22' }, D = {} }
        ),
        { A = { AA = '1' }, B = { BB = '11'}, C = { CC1 = '2', CC2 = '3' }, D = {} }
    ),
    "problem with marshaling table"
)

-- std::optional marshaling
local result = test_module.ns_empty_to_nil('')
assert(not result)
local result = test_module.ns_empty_to_nil('153')
assert(result == '153')

local result = test_module.ns_nil_to_empty()
assert(result == '')
local result = test_module.ns_nil_to_empty(nil)
assert(result == '')
local result = test_module.ns_nil_to_empty('531')
assert(result == '531')
