include $(top_srcdir)/build/modmake.rulesam
noinst_PROGRAMS = switch_event switch_hash switch_ivr_originate switch_utils switch_core switch_console switch_vpx switch_ivr_play_say switch_red switch_core_codec switch_core_file \
			   switch_ulp switch_ulp_recover1 switch_ulp_recover2 switch_ulp_recover3 switch_ulp_recover4 switch_ulp_jb \
			   switch_xml switch_rtp
noinst_PROGRAMS+= switch_core_video switch_core_db switch_vad switch_jitter_buffer switch_packetizer switch_core_session test_sofia switch_ivr_async switch_core_asr switch_log
noinst_PROGRAMS+= switch_hold
AM_LDFLAGS += -avoid-version -no-undefined $(SWITCH_AM_LDFLAGS) $(openssl_LIBS)
AM_LDFLAGS += $(FREESWITCH_LIBS) $(switch_builddir)/libfreeswitch.la $(CORE_LIBS) $(APR_LIBS)

# "make check" will not run these.
examples = switch_eavesdrop

if HAVE_FVAD
AM_CFLAGS += -DSWITCH_HAVE_FVAD
endif

if HAVE_PCAP
noinst_PROGRAMS += switch_estimators
AM_LDFLAGS += $(PCAP_LIBS)
endif 

TESTS = $(noinst_PROGRAMS)

bin_PROGRAMS = $(examples)
