local app_main = function(...)
    
    local main_args = {...}
    local ARG = main_args[1]
    local APPSYSNAME = main_args[2]
    local PRIOR = main_args[3]
    
    wrlog( "LUA: APP_TEST MAIN is RUNNING ")
    print_r(main_args)
    
    return true
end

return app_main
