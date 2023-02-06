#include <switch.h>
#include <test/switch_test.h>


/**
 * Test complete recovery with callbacks to external buffer. Two levels of protection.
 * Maximum size of the RTP packet is more than L0_lk, so 2 levels must be recovered.
 * Test protection as in RFC5109: 10.1 An Example Offers Similar Protection as RFC 2733
 *
 * Procedure
 *
 * There is many more small tests done in this test, the listed below are the most important points.
 *
 * 1. Generate RTP packets (A, B, C, D, E, F).
 * 2. Setup ULP for two levels of protection:
 *		 L0, of size 340 octets, group size 2 packets.
 *		 L1, of size 200 octets, group size 4 packets.
 * 3. Submit all RTP packets to the jitter buffer.
 * 4. Generate FEC packet.
 * 5. Compare generated FEC packet with RFC 5109 10.1.
 * 6. Generate FECs with SNB of packet A and packet B - they both cover packet D on L0.
 * 7. Reset jitter buffer.
 * 8. Insert packets A, B, C, E, F to the jitter buffer.
 * 9. Insert FEC with SNB = packet A into jb's redundancy hash.
 * 10. Recover D packet and compare recovered packet with the original packet D.
 * 11. Reset redundancy hash.
 * 12. Insert FEC with SNB = packet B into jb's redundancy hash.
 * 13. Recover D packet and compare recovered packet with the original packet D.
 */
	
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/
	static const uint8_t L0_gk = 2;				/* Number of packets in protection level L0. */
	#define  L0_lk  340						/* Number of octets protected by level L0. */
	static const uint8_t L1_gk = 4;				/* Number of packets in protection level L1. */
	static uint16_t L1_lk = 200;				/* Number of octets protected by level L1. */
	static const uint16_t L0_mask16 = 0xC000;
	static const uint16_t L1_mask16 = 0xF000;

	static const uint8_t version = 2;					/* RTP version 2. */
	static const uint8_t padding = 0;					/* No padding. */
	static const uint8_t extension = 0;					/* No extension. */
	static const uint8_t csrc_count = 0;				/* No contributing sources. */

	static const uint16_t seq_a = 8;
	static const uint16_t seq_b = 9;
	static const uint16_t seq_c = 10;
	static const uint16_t seq_d = 11;
	static const uint16_t seq_e = 12;
	static const uint16_t seq_f = 13;
	
	static const uint32_t ts_a = 3;
	static const uint32_t ts_b = 5;
	static const uint32_t ts_c = 7;
	static const uint32_t ts_d = 9;
	static const uint32_t ts_e = 10;
	static const uint32_t ts_f = 11;

	static const uint16_t payload_len_a = 0.5 * L0_lk;
	static const uint16_t payload_len_b = 0.8 * L0_lk;
	static const uint16_t payload_len_c = 0.1 * L0_lk;
	static const uint16_t payload_len_d = L0_lk;
	static const uint16_t payload_len_e = L0_lk + 10;
	static const uint16_t payload_len_f = L0_lk + 2;
	static const uint16_t payload_len_g = 400;
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/

static switch_memory_pool_t *pool = NULL;
static switch_rtp_t *rtp_session = NULL;
static switch_rtp_flag_t flags[SWITCH_RTP_FLAG_INVALID] = {0};
static const char *rx_host = "127.0.0.1";
static switch_port_t rx_port = 1314;
static const char *tx_host = "127.0.0.1";
static switch_port_t tx_port = 1318;

#define ulp_ok(x, s) fst_xcheck(!!(x), (s));
#define cmp_ulp_ok(x, y, s) fst_xcheck((x) == (y), (s));

FST_CORE_BEGIN("./conf")
{
FST_SUITE_BEGIN(switch_ulp_recover1)
{
FST_SETUP_BEGIN()
{
}
FST_SETUP_END()

FST_TEARDOWN_BEGIN()
{
}
FST_TEARDOWN_END()

FST_TEST_BEGIN(test_ulp_recover3)
{
	uint32_t ssrc = 0;
	const char *err = NULL;
	ulp_fec_pkt_t *fec = NULL, *fec2 = NULL, *fec3 = NULL, *fec4 = NULL;				/* FEC data. */
	switch_size_t fec_len = 0;
	switch_size_t fec2_len = 0;
	switch_size_t fec3_len = 0;
	switch_size_t fec4_len = 0;

	ulp_policy_t *policy = NULL, *send_policy = NULL;			/* sender's context */
	switch_jb_t *jb = NULL;

	switch_rtp_packet_t packet = {0};
	switch_size_t len = 0;

	switch_rtp_packet_t new_rtp;			/* recovered packet */
	uint8_t res = 0;
	ulp_status_t ulp_err = ulp_status_fail;	/* after call to _recover contains additional information about recovery result */

	ulp_rtp_pkt_t *rtp_A;
	ulp_rtp_pkt_t *rtp_B;
	ulp_rtp_pkt_t *rtp_C;
	ulp_rtp_pkt_t *rtp_D;
	ulp_rtp_pkt_t *rtp_E;
	ulp_rtp_pkt_t *rtp_F;

	memset(&packet, 0, sizeof(packet));
	
	switch_core_new_memory_pool(&pool);
	
	rtp_session = switch_rtp_new(rx_host, rx_port, tx_host, tx_port, 8, 8000, 20 * 1000, flags, "soft", &err, pool, 0, 0);
	fst_xcheck(rtp_session != NULL, "get RTP session");
	fst_requires(rtp_session);

	switch_rtp_ulpfec_init(rtp_session);

	policy = switch_rtp_get_ulp_policy(rtp_session);			/* Associated with jb. */
	send_policy = switch_rtp_get_ulp_send_policy(rtp_session);	/* Associated with rtp session. */

	ulp_ok(policy != NULL, "get ULP policy");
	ulp_ok(send_policy != NULL, "get ULP send policy");

	ulp_ok(ulp_get_user_data(policy) == jb, "get jitter buffer from receiver policy");
	ulp_ok(ulp_get_user_data(send_policy) == rtp_session, "get RTP session from sender policy");

	ssrc = switch_rtp_get_ssrc(rtp_session);
	
	ulp_ok(switch_jb_create(&jb, SJB_VIDEO, 0, 10, pool, SJB_NONE, policy) == SWITCH_STATUS_SUCCESS, "Creating Jitter Buffer");

	/* Test sender's and receiver's policies. */
	ulp_ok(ulp_get_user_data(policy) == jb, "get jitter buffer from receiver policy");
	ulp_ok(ulp_get_user_data(send_policy) == rtp_session, "get RTP session from sender policy");

	/* Check default settings worked. */

	ulp_ok(ulp_lvl_group_size(send_policy, 0) == SWITCH_ULP_L0_GK, "correct group size of level L0, ulp_lvl_group_size (L0)");
	ulp_ok(ulp_lvl_protection_len(send_policy, 0) == SWITCH_ULP_L0_LK, "correct protection length of level L0, ulp_lvl_protection_len (L0)");
	ulp_ok(ulp_lvl_protection_mask16(send_policy, 0) == SWITCH_ULP_L0_MASK16, "ulp_set_lvl_protection_mask16: L0");
	ulp_ok(ulp_lvl_group_size(send_policy, 1) == SWITCH_ULP_L1_GK, "correct group size of level L1, ulp_lvl_group_size (L1)");
	ulp_ok(ulp_lvl_protection_len(send_policy, 1) == SWITCH_ULP_L1_LK, "correct protection length of level L1, ulp_lvl_protection_len (L1)");
	ulp_ok(ulp_lvl_protection_mask16(send_policy, 1) == SWITCH_ULP_L1_MASK16, "ulp_set_lvl_protection_mask16: L0");


	/* Set ULP policies to test values. */
	ulp_ok(ulp_set_lvl_group_size(send_policy, 0, L0_gk) == ulp_status_ok, "ulp_set_lvl_group_size (sender)");
	ulp_ok(ulp_set_lvl_protection_len(send_policy, 0, L0_lk) == ulp_status_ok, "ulp_set_lvl_protection_len (sender)");
	ulp_ok(ulp_set_lvl_protection_mask16(send_policy, 0, L0_mask16) == ulp_status_ok, "ulp_set_lvl_protection_mask16: L0");
	
	ulp_ok(ulp_set_lvl_group_size(send_policy, 1, L1_gk) == ulp_status_ok, "ulp_set_lvl_group_size (sender)");
	ulp_ok(ulp_set_lvl_protection_len(send_policy, 1, L1_lk) == ulp_status_ok, "ulp_set_lvl_protection_len (sender)");
	ulp_ok(ulp_set_lvl_protection_mask16(send_policy, 1, L1_mask16) == ulp_status_ok, "ulp_set_lvl_protection_mask16: L1");

	/* Generate RTP packets. */

	rtp_A = ulp_gen_rtp(version, padding, extension, csrc_count, 1, 96, seq_a, ts_a, ssrc, payload_len_a);
	rtp_B = ulp_gen_rtp(version, padding, extension, csrc_count, 0, 96, seq_b, ts_b, ssrc, payload_len_b); 
	rtp_C = ulp_gen_rtp(version, padding, extension, csrc_count, 1, 96, seq_c, ts_c, ssrc, payload_len_c); 
	rtp_D = ulp_gen_rtp(version, padding, extension, csrc_count, 0, 96, seq_d, ts_d, ssrc, payload_len_d);
	rtp_E = ulp_gen_rtp(version, padding, extension, csrc_count, 1, 96, seq_e, ts_e, ssrc, payload_len_e);
	rtp_F = ulp_gen_rtp(version, padding, extension, csrc_count, 1, 96, seq_f, ts_f, ssrc, payload_len_f);

	ulp_ok(rtp_A && rtp_B && rtp_C && rtp_D, "get memory for testing.");	
	
	/* Should fail - no RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	/* Submit packets to the jitter buffer and generate FEC. */

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	/* Recover packet D - should fail, no FEC and not enough media. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 0, "XFAIL: RTP recovery should fail");

	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "FEC length");

	free(fec); fec = NULL;
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	/* Should fail - not enough RTP packets in the buf. */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "FEC length");

	free(fec); fec = NULL;
	
	fec = ulp_gen_fec(send_policy, 0, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");
	
	/* Should fail - levels > max level configured (1). */
	fec = ulp_gen_fec(send_policy, 100, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, seq_a);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	free(fec); fec = NULL;
	
	/* Test FEC generation for single level of protection. */

	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "FEC length");

	free(fec); fec = NULL;
	
	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, seq_b);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(L0_lk, ulp_max(payload_len_b, payload_len_c)), "FEC length");

	free(fec); fec = NULL;
	
	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, seq_c);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + ulp_min(L0_lk, ulp_max(payload_len_c, payload_len_d)), "FEC length");
	fec_len = ulp_fec_last_len(send_policy);

	free(fec); fec = NULL;
	
	/* not enough data for packet D, so this should fail. */
	fec = ulp_gen_fec(send_policy, 1, seq_d);
	ulp_ok(fec == NULL, "FEC generation should fail, ulp_gen_fec");
	
	cmp_ulp_ok(ulp_fec_last_len(send_policy), fec_len, "FEC length indicates length of last successful FEC generation");
	
	/* Test FEC generation for 2 levels of protection. */
	
	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec, "FEC generation should succeed, ulp_gen_fec");

	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 * 2 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)) + ulp_min(L1_lk, ulp_max(payload_len_a, ulp_max(payload_len_b, ulp_max(payload_len_c, payload_len_d)))), "FEC length");
	fec_len = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec_len, 490, "FEC packet length");

	/* Check. */
	cmp_ulp_ok(fec->hdr.e, 0, "E field");					/* reserved for future use */
	cmp_ulp_ok(fec->hdr.l, 0, "L field");					/* max group size is < 16 pkts */
	cmp_ulp_ok(fec->hdr.p_r, 0, "P recovery field");
	cmp_ulp_ok(fec->hdr.x_r, 0, "X recovery field");
	cmp_ulp_ok(fec->hdr.cc_r, 0, "CC recovery field");
	cmp_ulp_ok(fec->hdr.m_r, 0 ^ 1, "M recovery field");												/* Only L0_gk packets are XORed in FEC header. */
	cmp_ulp_ok(fec->hdr.pt_r, 96 ^ 96, "PT recovery field");											/* Only L0_gk packets are XORed in FEC header. */
	cmp_ulp_ok(ntohs(fec->hdr.snb), seq_a, "SN Base field");											/* SNB indicates the least seq needed for any of the protection levels. */ 
	cmp_ulp_ok(ntohl(fec->hdr.ts_r), htonl(rtp_A->hdr.ts) ^ htonl(rtp_B->hdr.ts), "TS recovery field");	/* Only L0_gk packets are XORed in FEC header. */
	cmp_ulp_ok(ntohs(fec->hdr.len_r), payload_len_a ^ payload_len_b, "Len recovery field");				/* Only L0_gk packets are XORed in FEC header. */
	
	/* Check L0 */
	cmp_ulp_ok(ntohs(fec->lvl[0].lk), ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "level L0 length");
	cmp_ulp_ok(ntohs(fec->lvl[0].mask16), L0_mask16, "level L0 mask");
	
	/* Check L1 */
	cmp_ulp_ok(ntohs(((ulp_fec_lvl_32_t*) ((char*)&fec->lvl[0] + 4 + ntohs(fec->lvl[0].lk)))->lk), ulp_min(L1_lk, ulp_max(payload_len_a, ulp_max(payload_len_b, ulp_max(payload_len_c, payload_len_d)))) , "FEC: level L1 length");
	cmp_ulp_ok(ntohs(((ulp_fec_lvl_32_t*) ((char*)&fec->lvl[0] + 4 + ntohs(fec->lvl[0].lk)))->mask16), L1_mask16, "FEC: level L1 mask");

	/* Reset jitter. */

	switch_jb_reset(jb);

	/* Submit packets less packet D to the jitter buffer. */

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	
	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");
	
	/* Need also C in the buf to generate FEC with SNB = seq_b (L0 necessary). */
	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");
	
	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	/* Recover packet D  - should fail: no FEC protecting D on L0 in the jb. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 0, "XFAIL: RTP recovery should fail");
	
	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");
	
	/* Recover packet D - should succeed: return from the jb buffer. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 1, "RTP recovery should succeed, from jb buffer");
	cmp_ulp_ok(ulp_err, ulp_status_ok, "ulp_recover (partial)");
	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_D->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_D->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_D->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_D->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_D->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_D->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_D->hdr.ts, "ulp_recover (header->ts)");
	new_rtp.header.ssrc = rtp_D->hdr.ssrc;
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_D->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(ulp_err, ulp_status_ok, "ulp_recover (partial)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_D, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_D + sizeof(switch_rtp_hdr_t), payload_len_d), 0, "ulp_recover: payload");

	ulp_ok(ulp_rtp_last_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_d, "ulp_rtp_last_len");
	ulp_ok(ulp_rtp_last_recover_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_d, "ulp_rtp_last_recover_len");

	free(fec);

	/* Now, put needed FEC to the jb. FEC needed may be generated either with SNB = seq_a (L0 for A, B) or SNB = seq_b (L0 for B, C). */
	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec, "FEC generation should succeed, ulp_gen_fec");
	fec_len = ulp_fec_last_len(send_policy);

	/* Submit FEC packet with SNB = seq_a to the jitter buffer (protects L0 { A, B }, L1 { A, B, C, D }. */
	fst_requires(fec);
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec, fec_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC packet");

	/* Generate FEC with SNB = seq_b. */
	
	/* First add E packet, it's not there yet. */
	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");

	fec2 = ulp_gen_fec(send_policy, 2, seq_b);
	ulp_ok(fec2, "FEC generation should succeed, ulp_gen_fec FEC 2");
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 * 2 + ulp_min(L0_lk, ulp_max(payload_len_b, payload_len_c)) + ulp_min(L1_lk, ulp_max(payload_len_e, ulp_max(payload_len_b, ulp_max(payload_len_c, payload_len_d)))), "FEC length");
	fec2_len = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec2_len, 490, "FEC packet length");
	
	/* Generate FEC with SNB = seq_a but only single level of protection, it will protect A and B on L0, and nothing more. */

	fec3 = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec3, "FEC generation should succeed, ulp_gen_fec FEC 3");
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 * 1 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "FEC 3 length");	/* There is only 1 level so 1 ULP header. */
	fec3_len = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec3_len, 286, "FEC packet length");

	/* Now reset jb & hash to simulate missing B. */
	switch_jb_reset(jb);
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_rtp_reset_rtp_for_fec_hash(rtp_session);

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");

	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");

	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");

	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec, "FEC generation should succeed, ulp_gen_fec");
	fec_len = ulp_fec_last_len(send_policy);

	/* First, test with SNB = seq_a. Packets used: L0: {A, B},  L1: {A, B, C, D } */
	/* Submit FEC packet with SNB = seq_a to the jitter buffer (protects L0 { A, B }, L1 { A, B, C, D }. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec, fec_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC packet");

	/* Check FEC SNB = seq_b. */
	cmp_ulp_ok(fec2->hdr.e, 0, "E field");					/* reserved for future use */
	cmp_ulp_ok(fec2->hdr.l, 0, "L field");					/* max group size is < 16 pkts */
	cmp_ulp_ok(fec2->hdr.p_r, 0, "P recovery field");
	cmp_ulp_ok(fec2->hdr.x_r, 0, "X recovery field");
	cmp_ulp_ok(fec2->hdr.cc_r, 0, "CC recovery field");
	cmp_ulp_ok(fec2->hdr.m_r, 0 ^ 1, "M recovery field");												/* Only L0_gk packets are XORed in FEC header. */
	cmp_ulp_ok(fec2->hdr.pt_r, 96 ^ 96, "PT recovery field");											/* Only L0_gk packets are XORed in FEC header. */
	cmp_ulp_ok(ntohs(fec2->hdr.snb), seq_b, "SN Base field");											/* SNB indicates the least seq needed for any of the protection levels, it is smallest seq of the highest group, here L1. */ 
	cmp_ulp_ok(ntohl(fec2->hdr.ts_r), htonl(rtp_B->hdr.ts) ^ htonl(rtp_C->hdr.ts), "TS recovery field");	/* Only L0_gk packets are XORed in FEC header. */
	cmp_ulp_ok(ntohs(fec2->hdr.len_r), payload_len_b ^ payload_len_c, "Len recovery field");				/* Only L0_gk packets are XORed in FEC header. */
	
	/* Check L0. */
	cmp_ulp_ok(ntohs(fec2->lvl[0].lk), ulp_min(L0_lk, ulp_max(payload_len_b, payload_len_c)), "level L0 length");
	cmp_ulp_ok(ntohs(fec2->lvl[0].mask16), L0_mask16, "level L0 mask");

	/* Check L1 */
	cmp_ulp_ok(ntohs(((ulp_fec_lvl_32_t*) ((char*)&fec2->lvl[0] + 4 + ntohs(fec2->lvl[0].lk)))->lk), ulp_min(L1_lk, ulp_max(payload_len_e, ulp_max(payload_len_b, ulp_max(payload_len_c, payload_len_d)))) , "FEC: level L1 length");
	cmp_ulp_ok(ntohs(((ulp_fec_lvl_32_t*) ((char*)&fec2->lvl[0] + 4 + ntohs(fec2->lvl[0].lk)))->mask16), L1_mask16, "FEC: level L1 mask");

/* Now */	
	
	/* Submit packets less packet B to jb. */

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");
	
	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");
	
	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	/* Recover packet B - should succeed using FEC 1 (SNB = seq_a) and L0 (L0_lk > L1_lk). */
	res = switch_rtp_recover(policy, seq_b, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 1, "RTP recovery should succeed");

	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_B->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_B->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_B->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_B->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_B->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_B->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_B->hdr.ts, "ulp_recover (header->ts)");
	new_rtp.header.ssrc = rtp_B->hdr.ssrc;
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_B->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(ulp_err, (payload_len_b > L0_lk ? ulp_status_recovery_partial : ulp_status_ok), "ulp_recover (partial)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_B, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_B + sizeof(switch_rtp_hdr_t), payload_len_b), 0, "ulp_recover: payload");

	ulp_ok(ulp_rtp_last_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_len");
	ulp_ok(ulp_rtp_last_recover_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_recover_len");

	free(fec2);
/* Now */
	/* Submit FEC with SNB = seq_b to the jitter buffer. FEC with SNB = seq_a is already there. */
	fec2 = ulp_gen_fec(send_policy, 2, seq_b);
	ulp_ok(fec2, "FEC generation should succeed, ulp_gen_fec FEC 2");
	fec2_len = ulp_fec_last_len(send_policy);

	fst_requires(fec2);
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec2, fec2_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 2 packet");
	
	/* Recover packet B again - should succeed again... */
	res = switch_rtp_recover(policy, seq_b, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 1, "RTP recovery should succeed");

	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_B->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_B->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_B->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_B->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_B->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_B->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_B->hdr.ts, "ulp_recover (header->ts)");
	new_rtp.header.ssrc = rtp_B->hdr.ssrc;
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_B->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(ulp_err, (payload_len_b > ulp_max(L0_lk, L1_lk) ? ulp_status_recovery_partial : ulp_status_ok), "ulp_recover (partial)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_B, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_B + sizeof(switch_rtp_hdr_t), payload_len_b), 0, "ulp_recover: payload");

	ulp_ok(ulp_rtp_last_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_len");
	ulp_ok(ulp_rtp_last_recover_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_recover_len");

	/* Remove all FECs from hash. */
	switch_jb_reset_redundancy_hash(jb);
	
	fec2 = ulp_gen_fec(send_policy, 2, seq_b);
	ulp_ok(fec2, "FEC generation should succeed, ulp_gen_fec FEC 2");
	fec2_len = ulp_fec_last_len(send_policy);

	fst_requires(fec2);
	/* And submit FEC with SNB = seq_b to the jitter buffer. Only FEC 2 (SNB = seq_b) in the jb. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec2, fec2_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 2 packet");
	
	/* Recover packet B again - should succeed again... */
	res = switch_rtp_recover(policy, seq_b, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 1, "RTP recovery should succeed");
	
	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_B->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_B->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_B->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_B->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_B->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_B->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_B->hdr.ts, "ulp_recover (header->ts)");
	new_rtp.header.ssrc = rtp_B->hdr.ssrc;
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_B->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(ulp_err, (payload_len_b > ulp_max(L0_lk, L1_lk) ? ulp_status_recovery_partial : ulp_status_ok), "ulp_recover (partial)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_B, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_B + sizeof(switch_rtp_hdr_t), payload_len_b), 0, "ulp_recover: payload");

	ulp_ok(ulp_rtp_last_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_len");
	ulp_ok(ulp_rtp_last_recover_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_recover_len");

	/* Remove all FECs from hash and reset jb & RTP hash. */
	switch_jb_reset(jb);
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_rtp_reset_rtp_for_fec_hash(rtp_session);
	
	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");

	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");

	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");

	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");


	free(fec3);
	fec3 = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec3, "FEC generation should succeed, ulp_gen_fec FEC 3");
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 * 1 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "FEC 3 length");	/* There is only 1 level so 1 ULP header. */
	fec3_len = ulp_fec_last_len(send_policy);

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec, "FEC generation should succeed, ulp_gen_fec");
	fec_len = ulp_fec_last_len(send_policy);

	fec2 = ulp_gen_fec(send_policy, 2, seq_b);
	ulp_ok(fec2, "FEC generation should succeed, ulp_gen_fec FEC 2");
	fec2_len = ulp_fec_last_len(send_policy);

	/* Submit packets less packet D to the jitter buffer. */

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");
	
	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");
	
	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");
	
	/* Recover packet D  - should fail: no FEC protecting D on L0 in the jb. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 0, "XFAIL: RTP recovery should fail");
	
	/* Submit FEC packet with SNB = seq_a to the jitter buffer (protects L0 { A, B }, L1 { A, B, C, D }. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec, fec_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC packet");
	
	/* Recover packet D  - should fail: no FEC protecting D on L0 in the jb. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 0, "XFAIL: RTP recovery should fail");
	
	/* And submit FEC with SNB = seq_a but only single level of protection (so it doesn't protect D) to the jitter buffer. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec3, fec3_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 3 packet");
	
	/* Recover packet D  - should fail: no FEC protecting D on L0 in the jb. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 0, "XFAIL: RTP recovery should fail");
	
	/* Submit FEC packet with SNB = seq_b to the jitter buffer (protects L0 { B, C }, L1 { B, C, D, E }. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec2, fec2_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 2 packet");
	
	/* Recover packet D  - should fail: no FEC protecting D on L0 in the jb. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 0, "XFAIL: RTP recovery should fail");
	
	/* Remove all FECs from hash & reset RTP hash. */
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_rtp_reset_rtp_for_fec_hash(rtp_session);
	
	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");

	len = payload_len_b;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");

	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");

	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	/* And submit all FECs to jb. */
	fec3 = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec3, "FEC generation should succeed, ulp_gen_fec FEC 3");
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 * 1 + ulp_min(L0_lk, ulp_max(payload_len_a, payload_len_b)), "FEC 3 length");	/* There is only 1 level so 1 ULP header. */
	fec3_len = ulp_fec_last_len(send_policy);

	fec = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec, "FEC generation should succeed, ulp_gen_fec");
	fec_len = ulp_fec_last_len(send_policy);

	fec2 = ulp_gen_fec(send_policy, 2, seq_b);
	ulp_ok(fec2, "FEC generation should succeed, ulp_gen_fec FEC 2");
	fec2_len = ulp_fec_last_len(send_policy);

	/* Submit FEC packet with SNB = seq_a to the jitter buffer (protects L0 { A, B }, L1 { A, B, C, D }. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec, fec_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC packet");
	
	/* And submit FEC with SNB = seq_b to the jitter buffer. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec2, fec2_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 2 packet");

	/* Submit FEC with SNB = seq_a but only single level of protection (so it doesn't protect D on L0) to the jitter buffer. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec3, fec3_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 3 packet");
	
	/* Submit packets less packet B to the jitter buffer. */

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");
	
	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");
	
	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");
	
	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");
	
	/* Recover packet B again - should succeed using best FEC possibility. */
	res = switch_rtp_recover(policy, seq_b, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 1, "RTP recovery should succeed");
	
	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_B->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_B->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_B->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_B->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_B->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_B->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_B->hdr.ts, "ulp_recover (header->ts)");
	new_rtp.header.ssrc = rtp_B->hdr.ssrc;
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_B->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(ulp_err, (payload_len_b > ulp_max(L0_lk, L1_lk) ? ulp_status_recovery_partial : ulp_status_ok), "ulp_recover (partial)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_B, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_B + sizeof(switch_rtp_hdr_t), payload_len_b), 0, "ulp_recover: payload");

	ulp_ok(ulp_rtp_last_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_len");
	ulp_ok(ulp_rtp_last_recover_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_b, "ulp_rtp_last_recover_len");

	switch_jb_destroy(&jb);
	ulp_ok(switch_jb_create(&jb, SJB_VIDEO, 0, 10, pool, SJB_NONE, policy) == SWITCH_STATUS_SUCCESS, "Creating Jitter Buffer");

	L1_lk = 300; 

	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_rtp_reset_rtp_for_fec_hash(rtp_session);

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");

	free(rtp_B);
	rtp_B = ulp_gen_rtp(version, padding, extension, csrc_count, 0, 96, seq_b, ts_b, ssrc, payload_len_g);
	len = payload_len_g;
	memcpy(&packet.header, &rtp_B->hdr, 12);
	memcpy(packet.body, rtp_B->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet B");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D");

	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");

	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");

	len = payload_len_c;
	memcpy(&packet.header, &rtp_C->hdr, 12);
	memcpy(packet.body, rtp_C->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet C");

	len = payload_len_d;
	memcpy(&packet.header, &rtp_D->hdr, 12);
	memcpy(packet.body, rtp_D->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet D"); 

	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");
	
	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	ulp_ok(ulp_set_lvl_protection_len(send_policy, 0, L0_lk) == ulp_status_ok, "ulp_set_lvl_protection_len (sender)");

	ulp_ok(ulp_set_lvl_protection_len(send_policy, 1, L1_lk) == ulp_status_ok, "ulp_set_lvl_protection_len (sender)");
	fec3 = ulp_gen_fec(send_policy, 1, seq_a);
	ulp_ok(fec3, "FEC generation should succeed, ulp_gen_fec");

	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec3, fec3_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 3 packet");

	fec4 = ulp_gen_fec(send_policy, 2, seq_a);
	ulp_ok(fec4, "FEC generation should succeed, ulp_gen_fec");

	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec4, fec4_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC 4 packet");

	res = switch_rtp_recover(policy, seq_b, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res != 1, "RTP recovery should fail");

	/* Cleanup. */
	free(rtp_A);
	free(rtp_B);
	free(rtp_C);
	free(rtp_D);
	free(rtp_E);
	free(rtp_F);
	
	switch_jb_destroy(&jb);
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_core_destroy_memory_pool(&pool);
}
FST_TEST_END()
}
FST_SUITE_END()
}
FST_CORE_END()

