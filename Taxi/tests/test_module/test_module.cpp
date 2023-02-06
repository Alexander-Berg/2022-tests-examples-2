#include <luamarshal/include/luamarshal.h>

namespace ns {

static const std::string CONST_A = "const string";
constexpr std::string_view CONST_B = "const string_view";
lua_Number toLuaNumber(std::string x) { return std::stod(x); }
lua_Integer toLuaInteger(std::string x) { return std::stoi(x); }
int toInt(std::string x) { return std::stoi(x); }

std::optional<std::string> emptyToNil(std::string x)
{
    if (x.empty())
        return {};
    return x;
}
std::string nilToEmpty(std::optional<std::string> x)
{
    if (x)
        return *x;
    return {};
}

using NestedDict = std::unordered_map<std::string, std::unordered_map<std::string, std::string>>;
NestedDict mergeNested(NestedDict one, NestedDict two)
{
    for (auto& entry : two) {
        auto [location, inserted] = one.insert(std::move(entry));
        if (!inserted) {
            auto& targetEntry = location->second;
            for (auto& subentry : entry.second) {
                targetEntry.insert(std::move(subentry));
            }
        }
    }
    return one;
}

} // namespace ns

lua_marshal::Registry g_lua;

LUA_EXPORT_FUNC(g_lua, ns::toLuaNumber);
LUA_EXPORT_FUNC(g_lua, ns::toLuaInteger);
LUA_EXPORT_FUNC(g_lua, ns::toInt);
LUA_EXPORT_FUNC(g_lua, ns::emptyToNil);
LUA_EXPORT_FUNC(g_lua, ns::nilToEmpty);
LUA_EXPORT_FUNC(g_lua, ns::mergeNested);
LUA_EXPORT_CONST(g_lua, ns::CONST_A);
LUA_EXPORT_CONST(g_lua, ns::CONST_B);

LUA_EXPORT_LIBRARY(g_lua, test_module);
