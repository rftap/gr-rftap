INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_RFTAP rftap)

FIND_PATH(
    RFTAP_INCLUDE_DIRS
    NAMES rftap/api.h
    HINTS $ENV{RFTAP_DIR}/include
        ${PC_RFTAP_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    RFTAP_LIBRARIES
    NAMES gnuradio-rftap
    HINTS $ENV{RFTAP_DIR}/lib
        ${PC_RFTAP_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/rftapTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(RFTAP DEFAULT_MSG RFTAP_LIBRARIES RFTAP_INCLUDE_DIRS)
MARK_AS_ADVANCED(RFTAP_LIBRARIES RFTAP_INCLUDE_DIRS)
