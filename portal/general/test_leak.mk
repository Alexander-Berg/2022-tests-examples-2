# http://perldoc.perl.org/perlhacktips.html#MEMORY-DEBUGGERS
include Makefile

LEAK_T          = $(wildcard t/*.t)
TEST_LEAK_T     = $(LEAK_T:%=leaktest-%)
TEST_VALGRIND_T = $(LEAK_T:%=valgrindtest-%)
#LEAK_USE   ?= Test::LeakTrace::Script
LEAK_USE   ?= Test::Valgrind

VALGRIND      ?= valgrind
VALGRIND_ARGS += --leak-check=full

TEST_RUN = $(FULLPERLRUN) "-I$(INST_LIB)" "-I$(INST_ARCHLIB)"

.PHONY: test_leak
test_leak: $(TEST_LEAK_T)

.PHONY: test_valgrind
test_valgrind: $(TEST_VALGRIND_T)

$(TEST_VALGRIND_T):
	PERL_DESTRUCT_LEVEL=2 $(VALGRIND) $(VALGRIND_ARGS) $(TEST_RUN) "$(@:valgrindtest-%=%)"

$(TEST_LEAK_T):
	$(TEST_RUN) "-M$(LEAK_USE)" "$(@:leaktest-%=%)"

