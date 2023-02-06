
#include <switch.h>
#include <test/switch_test.h>

/**
 * Test with callbacks to external buffer.
 * Test protection as in RFC5109: 10.1 An Example Offers Similar Protection as RFC 2733
 *
 * Procedure
 * 1. Generate four RTP packets (A, B, C, D) with data as in RFC 5109 10.1.
 * 2. Setup ULP policy.
 * 3. Submit all RTP packets to the jitter buffer.
 * 4. Generate FEC packet.
 * 5. Generate RED packet.
 * 6. Check RED packet.
 * 7. Depaketize RED packet.
 * 8. Check Primary and Redundant encodings.
 */
	
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/
	
	static const uint8_t version = 2;					/* RTP version 2. */
	static const uint8_t padding = 0;					/* No padding. */
	static const uint8_t extension = 0;					/* No extension. */
	static const uint8_t csrc_count = 0;					/* No contributing sources. */

	static const uint16_t seq_a = 8;
	static const uint16_t seq_b = 9;
	static const uint16_t seq_c = 10;
	static const uint16_t seq_d = 11;
	
	static const uint32_t ts_a = 3;
	static const uint32_t ts_b = 5;
	static const uint32_t ts_c = 7;
	static const uint32_t ts_d = 9;

	static const uint32_t ssrc = 2;				/* Assuming SSRC == 2. */

	static const uint16_t payload_len_a = 200;
	static const uint16_t payload_len_b = 140;
	static const uint16_t payload_len_c = 100;
	static const uint16_t payload_len_d = 340;
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/

static switch_memory_pool_t *pool = NULL;
static switch_rtp_t *rtp_session = NULL;
static switch_rtp_flag_t flags[SWITCH_RTP_FLAG_INVALID] = {0};
static const char *rx_host = "127.0.0.1";
static switch_port_t rx_port = 1314;
static const char *tx_host = "127.0.0.1";
static switch_port_t tx_port = 1318;

#define ulp_ok(x, s) fst_xcheck(!!(x), (s)); ulp_test((x), (s));
#define cmp_ulp_ok(x, y, s) fst_xcheck((x) == (y), (s)); ulp_test((x) == (y), (s));



FST_CORE_BEGIN("./conf")
{
FST_SUITE_BEGIN(switch_red)
{
FST_SETUP_BEGIN()
{
}
FST_SETUP_END()

FST_TEARDOWN_BEGIN()
{
}
FST_TEARDOWN_END()

FST_TEST_BEGIN(test_red)
{
	const char *err = NULL;
	ulp_fec_pkt_t *fec = NULL;				/* FEC data. */
	uint16_t fec_len = 0;

	ulp_policy_t *send_policy = NULL;

	switch_rtp_packet_t packet = {0};
	switch_size_t len = 0;

	switch_core_session_t *session = NULL;
	
	switch_rtp_packet_t *red = NULL;
	uint16_t red_len = 0;
	uint16_t red_fec_ts_diff_offset = 0;
	uint16_t red_fec_len = 0;
	ulp_red_encoding_block_hdr_t *en = NULL;
	switch_rtp_packet_t rtp_data;
	switch_rtp_packet_t rtp_data2;
	switch_rtp_packet_t fec_data;
	
	switch_rtp_packet_t *rtp = NULL;		/* Depaketized Primary Encoding. */
	uint16_t rtp_len = 0;					/* Depaketized Primary Encoding's length. */
	ulp_fec_pkt_t *fec2 = NULL;				/* Depaketized FEC's data. */
	uint16_t fec2_len = 0;					/* Depaketized FEC's length. */
	uint16_t fec2_ts_diff_offset = 0;		/* Depaketized FEC's timestamp offset. */

	ulp_rtp_pkt_t *rtp_A;
	ulp_rtp_pkt_t *rtp_B;
	ulp_rtp_pkt_t *rtp_C;
	ulp_rtp_pkt_t *rtp_D;
	memset(&packet, 0, sizeof(packet));

	switch_core_new_memory_pool(&pool);
	
	rtp_session = switch_rtp_new(rx_host, rx_port, tx_host, tx_port, 8, 8000, 20 * 1000, flags, "soft", &err, pool, 0, 0);
	fst_xcheck(rtp_session != NULL, "get RTP session");
	fst_requires(rtp_session);

	switch_rtp_ulpfec_init(rtp_session);

	send_policy = switch_rtp_get_ulp_send_policy(rtp_session);
	fst_xcheck(send_policy != NULL, "get ULP send policy from RTP session");
	fst_requires(send_policy);

	fst_xcheck(ulp_lvl_group_size(send_policy, 0) == SWITCH_ULP_L0_GK, "correct group size of level L0, ulp_lvl_group_size (L0)");
	fst_xcheck(ulp_lvl_protection_len(send_policy, 0) == SWITCH_ULP_L0_LK, "correct protection length of level L0, ulp_lvl_protection_len (L0)");
	fst_xcheck(ulp_lvl_group_size(send_policy, 1) == SWITCH_ULP_L1_GK, "correct group size of level L1, ulp_lvl_group_size (L1)");
	fst_xcheck(ulp_lvl_protection_len(send_policy, 1) == SWITCH_ULP_L1_LK, "correct protection length of level L1, switch_lvl_protection_len (L1)");

	/* Generate RTP packets. */
	rtp_A = ulp_gen_rtp(version, padding, extension, csrc_count, 1, 11, seq_a, ts_a, ssrc, payload_len_a);
	rtp_B = ulp_gen_rtp(version, padding, extension, csrc_count, 0, 18, seq_b, ts_b, ssrc, payload_len_b); 
	rtp_C = ulp_gen_rtp(version, padding, extension, csrc_count, 1, 11, seq_c, ts_c, ssrc, payload_len_c); 
	rtp_D = ulp_gen_rtp(version, padding, extension, csrc_count, 0, 18, seq_d, ts_d, ssrc, payload_len_d);

	fst_xcheck(rtp_A && rtp_B && rtp_C && rtp_D, "get memory for testing.");
	/* Should fail - no RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	/* Submit packets to the jitter buffer. */
	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");
	
	/* Should fail - levels > max level configured (1). */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, switch_gen_fec");
	
	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(fec != NULL, "FEC generation should succeed, switch_gen_fec");

	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(SWITCH_ULP_L0_LK, ulp_max(payload_len_a, ulp_max(payload_len_b, ulp_max(payload_len_c, payload_len_d)))), "FEC length");
	
	fec_len = ulp_fec_last_len(send_policy);

	/* Check. */
	cmp_ulp_ok(fec->hdr.e, 0, "E field");					/* reserved for future use */
	cmp_ulp_ok(fec->hdr.l, 0, "L field");					/* max group size is < 16 pkts */
	cmp_ulp_ok(fec->hdr.p_r, 0, "P recovery field");
	cmp_ulp_ok(fec->hdr.x_r, 0, "X recovery field");
	cmp_ulp_ok(fec->hdr.cc_r, 0, "CC recovery field");
	cmp_ulp_ok(fec->hdr.m_r, 0, "M recovery field");
	cmp_ulp_ok(fec->hdr.pt_r, 0, "PT recovery field");
	cmp_ulp_ok(ntohs(fec->hdr.snb), 8, "SN Base field");
	cmp_ulp_ok(ntohl(fec->hdr.ts_r), 8, "TS recovery field");
	cmp_ulp_ok(ntohs(fec->hdr.len_r), 372, "Len recovery field");		/* 200 XOR 140 XOR 100 XOR 340 */
	
	cmp_ulp_ok(ntohs(fec->lvl[0].lk), ulp_min(340, SWITCH_ULP_L0_LK), "level L0 length");
	cmp_ulp_ok(ntohs(fec->lvl[0].mask16), 61440, "level L0 mask");	/* Bits 0, 1, 2, 3 set (for A, B, C, D) */

	/* RED */

	/* With primary encoding only. */
	/* switch_red allocates memory and copies RTP media. */
	red = switch_red_gen_pkt(rtp_session, &rtp_A->hdr, payload_len_a, rtp_A->hdr.pt, 0, NULL, 0, SWITCH_ULPFEC_PT, 0, &red_len, SWITCH_RED_PT, (void*) &rtp_data);
	fst_xcheck(red != NULL, "switch_gen_red_pkt");
	
	/* Check RED packet length. */
	fst_xcheck(red_len == sizeof(switch_rtp_hdr_t) + 1 + payload_len_a, "RED: length");

	/* RED header should be same as media, with only PT and M changed. */
	cmp_ulp_ok(red->header.version, rtp_A->hdr.v, "RED: V field");
	cmp_ulp_ok(red->header.p, rtp_A->hdr.p, "RED: P field");
	cmp_ulp_ok(red->header.x, rtp_A->hdr.x, "RED: X field");
	cmp_ulp_ok(red->header.cc, rtp_A->hdr.cc, "RED: CC field");
	cmp_ulp_ok(red->header.m, rtp_A->hdr.m, "RED: M field");
	cmp_ulp_ok(red->header.pt, SWITCH_RED_PT, "RED: PT field");
	cmp_ulp_ok(red->header.seq, rtp_A->hdr.seq, "RED: CC field");
	cmp_ulp_ok(red->header.ts, rtp_A->hdr.ts, "RED: CC field");
	cmp_ulp_ok(red->header.ssrc, rtp_A->hdr.ssrc, "RED: CC field");
	
	en = (void *) red->body;
	cmp_ulp_ok(en->f, 0, "RED: Primary Encoding F field");								/* Should be 0 as this is primary encoding, i.e. RTP media packet. */
	cmp_ulp_ok(en->pt, rtp_A->hdr.pt, "RED: Primary Encoding PT field");				/* Should be same as PT of the RTP media packet. */

	/* Check payload. */
	cmp_ulp_ok(memcmp((char *) en + 1, &rtp_A->b, payload_len_a), 0, "RED: Primary Encoding payload");
	
	/* Depaketize RED packet. */
	memset(&rtp_data2, 0, sizeof(rtp_data2));
	rtp_len = red_len - sizeof(switch_rtp_hdr_t);
	rtp = switch_red_depacketize(session, send_policy, (void*) red, &rtp_len, (void*) &fec2, &fec2_len, &fec2_ts_diff_offset, (void *) &rtp_data2, SWITCH_ULPFEC_PT);
	fst_xcheck(rtp != NULL, "switch_red_depacketize: Primary Encoding");
	fst_xcheck(fec2 == NULL, "switch_red_depacketize: XTEST Redundant Encoding");
	cmp_ulp_ok(fec2_len, 0, "switch_red_depacketize: XTEST Redundant Encoding length");
	cmp_ulp_ok(fec2_ts_diff_offset, 0, "switch_red_depacketize XTEST: Redundant Encoding timestamp diff offset");
	
	/* Check Primary Encoding is extracted properly. Note, PT should be same as PT used to encode the media, but M is always zero, so it is lost if original packet had M=1. */
	cmp_ulp_ok(rtp->header.version, rtp_A->hdr.v, "RED depacketize: Primary Encoding V field");
	cmp_ulp_ok(rtp->header.p, rtp_A->hdr.p, "RED depacketize: Primary Encoding P field");
	cmp_ulp_ok(rtp->header.x, rtp_A->hdr.x, "RED depacketize: Primary Encoding X field");
	cmp_ulp_ok(rtp->header.cc, rtp_A->hdr.cc, "RED depacketize: Primary Encoding CC field");
	cmp_ulp_ok(rtp->header.m, rtp_A->hdr.m, "RED depacketize: Primary Encoding M field");						/* Note: Original RTP packet had M=1. */
	cmp_ulp_ok(rtp->header.pt, rtp_A->hdr.pt, "RED depacketize: Primary Encoding PT field");
	cmp_ulp_ok(rtp->header.seq, rtp_A->hdr.seq, "RED depacketize: Primary Encoding CC field");
	cmp_ulp_ok(rtp->header.ts, rtp_A->hdr.ts, "RED depacketize: Primary Encoding CC field");
	cmp_ulp_ok(rtp->header.ssrc, rtp_A->hdr.ssrc, "RED depacketize: Primary Encoding CC field");
	/* Note: we can't do
	 *		cmp_ulp_ok(memcmp(rtp, rtp_A, sizeof(switch_rtp_hdr_t)), "==", 0, "RED depacketize : Primary Encoding header");
	 * as the M bit is always 0 for RED header, so it gets lost in RED encoding if original packet got M=1. */
	cmp_ulp_ok(memcmp((char*) rtp + sizeof(switch_rtp_hdr_t), (char *) rtp_A + sizeof(switch_rtp_hdr_t), payload_len_a), 0, "RED depacketize: Primary Encoding payload");

	rtp = NULL; rtp_len = 0; 
	red = NULL;
	
	/* With both primary and redundant encoding. */
	/* switch_red allocates memory and copies RTP media. */
	memset(&rtp_data, 0, sizeof(rtp_data));
	red = switch_red_gen_pkt(rtp_session, &rtp_A->hdr, payload_len_a, rtp_A->hdr.pt, 0, fec, fec_len, SWITCH_ULPFEC_PT, 0, &red_len, SWITCH_RED_PT, (void *) &rtp_data);
	fst_xcheck(red != NULL, "switch_gen_red_pkt");
	
	/* Check RED packet length. */
	cmp_ulp_ok(red_len, sizeof(switch_rtp_hdr_t) + sizeof(ulp_red_encoding_block_hdr_t) + fec_len + 1 + payload_len_a, "RED: length");

	/* RED header should be same as media, with only PT and M changed. */
	cmp_ulp_ok(red->header.version, rtp_A->hdr.v, "RED: V field");
	cmp_ulp_ok(red->header.p, rtp_A->hdr.p, "RED: P field");
	cmp_ulp_ok(red->header.x, rtp_A->hdr.x, "RED: X field");
	cmp_ulp_ok(red->header.cc, rtp_A->hdr.cc, "RED: CC field");
	cmp_ulp_ok(red->header.m, rtp_A->hdr.m, "RED: M field");
	cmp_ulp_ok(red->header.pt, SWITCH_RED_PT, "RED: PT field");
	cmp_ulp_ok(red->header.seq, rtp_A->hdr.seq, "RED: CC field");
	cmp_ulp_ok(red->header.ts, rtp_A->hdr.ts, "RED: CC field");
	cmp_ulp_ok(red->header.ssrc, rtp_A->hdr.ssrc, "RED: CC field");
	
	en = (void *) red->body;
	cmp_ulp_ok(en->f, 1, "RED: Redundant Encoding F field");								/* Should be 1 as this is redundant encoding, i.e. SWITCHFEC packet. */
	cmp_ulp_ok(en->pt, SWITCH_ULPFEC_PT, "RED: Redundant Encoding PT field");				/* Should be SWITCHFEC PT indicating SWITCHFEC packet. */
	red_fec_ts_diff_offset = ulp_red_encoding_block_get_ts(en->ts_off_len);
	red_fec_len = ulp_red_encoding_block_get_len(en->ts_off_len);
	cmp_ulp_ok(red_fec_ts_diff_offset, 0, "RED: Redundant Encoding TS field");				/* Should be equal to diff between FEC ts and that from RTP media. */
	cmp_ulp_ok(red_fec_len, fec_len, "RED: Redundant Encoding LEN field");					/* Should be equal to length of SWITCHFEC packet. */
	/* Check Redundant Encoding payload. */
	cmp_ulp_ok(memcmp((char *) en + 4, fec, fec_len), 0, "RED: Redundant Encoding payload");
	en = (ulp_red_encoding_block_hdr_t *) ((char *) en + sizeof(ulp_red_encoding_block_hdr_t) + fec_len);
	cmp_ulp_ok(en->f, 0, "RED: Primary Encoding F field");									/* Should be 0 as this is primary encoding, i.e. RTP media packet. */
	cmp_ulp_ok(en->pt, rtp_A->hdr.pt, "RED: Primary Encoding PT field");						/* Should be same as PT of the RTP media packet. */
	/* Check Primary Encoding payload. */
	cmp_ulp_ok(memcmp((char *) en + 1, rtp_A->b, payload_len_a), 0, "RED: Primary Encoding payload");

	/* Depaketize RED packet. */
	memset(&rtp_data2, 0, sizeof(rtp_data2));
	rtp_len = red_len - sizeof(switch_rtp_hdr_t);
	memset(&fec_data, 0, sizeof(fec_data));
	fec2 = (void *) &fec_data;
	rtp = switch_red_depacketize(session, send_policy, (void*) red, &rtp_len, (void*) &fec2, &fec2_len, &fec2_ts_diff_offset, (void *) &rtp_data2, SWITCH_ULPFEC_PT);
	fst_xcheck(rtp != NULL, "switch_red_depacketize: Primary Encoding");
	fst_xcheck(fec2 != NULL, "switch_red_depacketize: Redundant Encoding");
	cmp_ulp_ok(fec2_len, fec_len, "switch_red_depacketize: Redundant Encoding length");
	cmp_ulp_ok(fec2_ts_diff_offset, 0, "switch_red_depacketize: Redundant Encoding timestamp diff offset");
	
	/* Check Primary Encoding is extracted properly. Note, PT should be same as PT used to encode the media, but accroding to RFC 5109 M is always lost and cannot be recovered, but it was changed in libulp, M is recoverable. */
	cmp_ulp_ok(rtp->header.version, rtp_A->hdr.v, "RED depacketize: Primary Encoding V field");
	cmp_ulp_ok(rtp->header.p, rtp_A->hdr.p, "RED depacketize: Primary Encoding P field");
	cmp_ulp_ok(rtp->header.x, rtp_A->hdr.x, "RED depacketize: Primary Encoding X field");
	cmp_ulp_ok(rtp->header.cc, rtp_A->hdr.cc, "RED depacketize: Primary Encoding CC field");
	cmp_ulp_ok(rtp->header.m, rtp_A->hdr.m, "RED depacketize: Primary Encoding M field");						/* Note: Original RTP packet had M=1. */
	cmp_ulp_ok(rtp->header.pt, rtp_A->hdr.pt, "RED depacketize: Primary Encoding PT field");
	cmp_ulp_ok(rtp->header.seq, rtp_A->hdr.seq, "RED depacketize: Primary Encoding CC field");
	cmp_ulp_ok(rtp->header.ts, rtp_A->hdr.ts, "RED depacketize: Primary Encoding CC field");
	cmp_ulp_ok(rtp->header.ssrc, rtp_A->hdr.ssrc, "RED depacketize: Primary Encoding CC field");
	/* Note: we can't do
	 *		cmp_ulp_ok(memcmp(rtp, rtp_A, sizeof(switch_rtp_hdr_t)), "==", 0, "RED depacketize : Primary Encoding header");
	 * as the M bit is always 0 for RED header, so it gets lost in RED encoding if original packet got M=1. */
	cmp_ulp_ok(memcmp((char*) rtp + sizeof(switch_rtp_hdr_t), (char *) rtp_A + sizeof(switch_rtp_hdr_t), payload_len_a), 0, "RED depacketize : Primary Encoding payload");
	
	/* Check Redundant Encoding s extracted properly. */
	cmp_ulp_ok(memcmp(fec2, fec, fec_len), 0, "RED depacketize: Redundant Encoding");

	rtp = NULL; rtp_len = 0; 
	fec2 = NULL; fec2_len = 0; 

	red = NULL;
	
	/* Should fail - no media. */
	red = switch_red_gen_pkt(rtp_session, NULL, payload_len_a, rtp_A->hdr.pt, 0, fec, fec_len, SWITCH_ULPFEC_PT, 0, &red_len, SWITCH_RED_PT, (void *) &rtp_data);
	fst_xcheck(red == NULL, "switch_gen_red_pkt XFAIL");

	/* Cleanup. */
	free(fec);
	free(rtp_A);
	free(rtp_B);
	free(rtp_C);
	free(rtp_D);
	
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_core_destroy_memory_pool(&pool);
}
FST_TEST_END()
}
FST_SUITE_END()
}
FST_CORE_END()

