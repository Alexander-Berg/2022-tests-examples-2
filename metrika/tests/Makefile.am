check_PROGRAMS = uatraits-tests

noinst_HEADERS = mock_iterator.hpp mock_shared.hpp mock_template.hpp \
	test_utils.hpp

uatraits_tests_SOURCES = main.cpp mock_shared.cpp \
	detector_test.cpp functors_test.cpp integer_test.cpp iterator_test.cpp \
	range_test.cpp regex_utils_test.cpp shared_ptr_test.cpp \
	static_assert_test.cpp string_match_test.cpp string_utils_test.cpp \
	type_list_test.cpp type_traits_test.cpp

uatraits_tests_LDADD = ${top_srcdir}/library/libuatraits.la
	
AM_CXXFLAGS = -pthread
AM_CPPFLAGS = -I${top_srcdir}/include -I${top_srcdir}/config \
	@BOOST_CPPFLAGS@ @XML_CPPFLAGS@ @PCRE_CFLAGS@
	
AM_LDFLAGS = @BOOST_LDFLAGS@ @BOOST_THREAD_LDFLAGS@ @BOOST_UNIT_TEST_LDFLAGS@ \
	@XML_LIBS@ @PCRE_LIBS@ @BOOST_THREAD_LIBS@

TESTS = uatraits-tests
TESTS_ENVIRONMENT = DATAFILE=${top_srcdir}/data/browser.xml

noinst_DATA = cover.xml cover.xsl cover-data.xsl
