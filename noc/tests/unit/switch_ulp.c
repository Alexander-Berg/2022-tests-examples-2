#include <switch.h>
#include <test/switch_test.h>


/**
 * Test with callbacks to external buffer.
 * Test protection as in RFC5109: 10.1 An Example Offers Similar Protection as RFC 2733
 *
 * Procedure
 * 1. Generate four RTP packets (A, B, C, D) with data as in RFC 5109 10.1.
 * 2. Setup ULP for single level of protection L0, of size 340 octets, group size 4 packets.
 * 3. Submit all RTP packets to the jitter buffer.
 * 4. Generate FEC packet.
 * 5. Compare generated FEC packet with RFC 5109 10.1.
 */
	
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/
	static const uint8_t v = 2;					/* RTP version 2. */
	static const uint8_t p = 0;					/* No padding. */
	static const uint8_t x = 0;					/* No extension. */
	static const uint8_t cc = 0;					/* No contributing sources. */

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
FST_SUITE_BEGIN(switch_ulp)
{
FST_SETUP_BEGIN()
{
}
FST_SETUP_END()

FST_TEARDOWN_BEGIN()
{
}
FST_TEARDOWN_END()

FST_TEST_BEGIN(test_ulp)
{
	const char *err = NULL;
	ulp_fec_pkt_t *fec = NULL;				/* FEC data. */

	ulp_policy_t *send_policy = NULL;
	switch_rtp_packet_t packet = {0};
	switch_size_t len = 0;

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
	send_policy = switch_rtp_get_ulp_send_policy(rtp_session);	/* Associated with rtp session. */
	fst_xcheck(send_policy != NULL, "get ULP send policy from RTP session");
	fst_requires(send_policy);

	fst_xcheck(ulp_lvl_group_size(send_policy, 0) == SWITCH_ULP_L0_GK, "group size of level L0, ulp_lvl_group_size (L0)");
	fst_xcheck(ulp_lvl_protection_len(send_policy, 0) == SWITCH_ULP_L0_LK, "protection length of level L0, ulp_lvl_protection_len (L0)");
	fst_xcheck(ulp_lvl_protection_mask16(send_policy, 0) == SWITCH_ULP_L0_MASK16, "ulp_set_lvl_protection_mask16 failed: L0");
	fst_xcheck(ulp_lvl_group_size(send_policy, 1) == SWITCH_ULP_L1_GK, "group size of level L1, ulp_lvl_group_size (L1)");
	fst_xcheck(ulp_lvl_protection_len(send_policy, 1) == SWITCH_ULP_L1_LK, "protection length of level L1, ulp_lvl_protection_len (L1)");
	fst_xcheck(ulp_lvl_protection_mask16(send_policy, 1) == SWITCH_ULP_L1_MASK16, "ulp_set_lvl_protection_mask16 failed: L0");

	/* Generate RTP packets. */
	rtp_A = ulp_gen_rtp(v, p, x, cc, 1, 11, seq_a, ts_a, ssrc, payload_len_a);
	rtp_B = ulp_gen_rtp(v, p, x, cc, 0, 18, seq_b, ts_b, ssrc, payload_len_b); 
	rtp_C = ulp_gen_rtp(v, p, x, cc, 1, 11, seq_c, ts_c, ssrc, payload_len_c); 
	rtp_D = ulp_gen_rtp(v, p, x, cc, 0, 18, seq_d, ts_d, ssrc, payload_len_d);

	fst_xcheck(rtp_A && rtp_B && rtp_C && rtp_D, "get memory for testing.");	
	
	/* Should fail - no RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	/* Submit packets to jitter buffer. */
	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");
	
	/* Should fail - levels > max level configured (1). */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	fst_xcheck(!fec, "FEC generation should fail, ulp_gen_fec");
	
	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	fst_xcheck(fec != NULL, "FEC generation should succeed, ulp_gen_fec");

	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(SWITCH_ULP_L0_LK, ulp_max(payload_len_a, ulp_max(payload_len_b, ulp_max(payload_len_c, payload_len_d)))), "FEC length");

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

