#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "k4SimDelphes::DelphesEDM4HepConverter" for configuration "RelWithDebInfo"
set_property(TARGET k4SimDelphes::DelphesEDM4HepConverter APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(k4SimDelphes::DelphesEDM4HepConverter PROPERTIES
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib64/libDelphesEDM4HepConverter.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libDelphesEDM4HepConverter.so"
  )

list(APPEND _cmake_import_check_targets k4SimDelphes::DelphesEDM4HepConverter )
list(APPEND _cmake_import_check_files_for_k4SimDelphes::DelphesEDM4HepConverter "${_IMPORT_PREFIX}/lib64/libDelphesEDM4HepConverter.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
