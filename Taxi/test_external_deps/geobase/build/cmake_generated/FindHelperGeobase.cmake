# AUTOGENERATED, DON'T CHANGE THIS FILE!

 
              
 
 

include(FindPackageHandleStandardArgs)

find_library(Geobase_LIBRARIES_geobase6 NAMES
  geobase6
  )
list(APPEND Geobase_LIBRARIES
  ${Geobase_LIBRARIES_geobase6}
)
  
find_path(Geobase_INCLUDE_DIRS_geobase6_lookup_hpp NAMES
  geobase6/lookup.hpp
  )
list(APPEND Geobase_INCLUDE_DIRS
  ${Geobase_INCLUDE_DIRS_geobase6_lookup_hpp}
)
  
 

 
 
find_package_handle_standard_args(
  Geobase
    REQUIRED_VARS
      Geobase_LIBRARIES
      Geobase_INCLUDE_DIRS
      
    FAIL_MESSAGE
      "Could not find `Geobase` package. Debian: sudo apt update && sudo apt install libgeobase6-dev MacOS: brew install geobase6"
)
mark_as_advanced(
  Geobase_LIBRARIES
  Geobase_INCLUDE_DIRS
  
)
 
if(NOT Geobase_FOUND)
  message(FATAL_ERROR "Could not find `Geobase` package. Debian: sudo apt update && sudo apt install libgeobase6-dev MacOS: brew install geobase6")
endif(NOT Geobase_FOUND)

 
if (NOT TARGET Geobase)
  add_library(Geobase INTERFACE IMPORTED GLOBAL)
   target_include_directories(Geobase INTERFACE ${Geobase_INCLUDE_DIRS})
   target_link_libraries(Geobase INTERFACE ${Geobase_LIBRARIES})
  endif(NOT TARGET Geobase)