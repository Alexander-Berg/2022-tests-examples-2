#include <switch.h>
#include <test/switch_test.h>

/**
 * Test recovery with long mask (48 bits). Single level o protection.
 *
 * Procedure
 * 1. Generate four RTP packets (A, B, C, D).
 * 2. Setup ULP.
 * 3. Submit all RTP packets to the jitter buffer.
 * 4. Generate FEC packet.
 * 5. Check FEC packet.
 * 6. Reset jitter buffer.
 * 7. Insert packets A, B, C to the jitter buffer.
 * 8. Insert FEC packet (from step 4).
 * 9. Recover D packet.
 * 10. Compare recovered packet with the original packet D.
 */
	
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/
	static const uint8_t L0_gk = 4;				/* Number of packets in protection level L0. */
	static const uint16_t L0_lk = 500;				/* Number of octets protected by level L0. */
	static const uint16_t L0_mask16 = 0x4800;
	static const uint32_t L0_mask_cont = 0x01100000;

	static const uint8_t version = 2;					/* RTP version 2. */
	static const uint8_t padding = 0;					/* No padding. */
	static const uint8_t extension = 0;					/* No extension. */
	static const uint8_t csrc_count = 0;					/* No contributing sources. */
	static const uint8_t mark = 0;
	static const uint8_t payload_type = 98;

	static const uint16_t snb = 1;
	static const uint16_t seq_a = 2;
	static const uint16_t seq_b = 5;
	static const uint16_t seq_c = 1 + 23;
	static const uint16_t seq_d = 1 + 27;
	
	static const uint32_t ts_a = 223344;
	static const uint32_t ts_b = 223364;
	static const uint32_t ts_c = 223384;
	static const uint32_t ts_d = 223404;

	static const uint16_t payload_len_a = 1200;
	static const uint16_t payload_len_b = 1200;
	static const uint16_t payload_len_c = 1250;
	static const uint16_t payload_len_d = 437;
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

FST_TEST_BEGIN(test_ulp_recover4)
{
	uint32_t ssrc = 0;
	const char *err = NULL;
	ulp_fec_pkt_t *fec = NULL;				/* FEC data. */
	switch_size_t fec_len = 0;

	ulp_policy_t *policy = NULL, *send_policy = NULL;			/* ULP context */
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

	ulp_fec_lvl_64_t *ulp_fec;

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
	ulp_ok(ulp_set_lvl_protection_mask_cont(send_policy, 0, L0_mask_cont) == ulp_status_ok, "ulp_set_lvl_protection_mask_cont: L0");

	ulp_ok(ulp_set_lvl_group_size(send_policy, 1, L0_gk) == ulp_status_ok, "ulp_set_lvl_group_size (sender)");
	ulp_ok(ulp_set_lvl_protection_len(send_policy, 1, L0_lk) == ulp_status_ok, "ulp_set_lvl_protection_len (sender)");
	ulp_ok(ulp_set_lvl_protection_mask16(send_policy, 1, L0_mask16) == ulp_status_ok, "ulp_set_lvl_protection_mask16: L0");
	ulp_ok(ulp_set_lvl_protection_mask_cont(send_policy, 1, L0_mask_cont) == ulp_status_ok, "ulp_set_lvl_protection_mask_cont: L0");
	
	ulp_ok(ulp_test_flag(send_policy, ULP_FL_USE_ULP) == 0, "ulp_test_flag: ULP_FL_USE_ULP");

	/* Generate RTP packets. */
	rtp_A = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_a, ts_a, ssrc, payload_len_a);
	rtp_B = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_b, ts_b, ssrc, payload_len_b); 
	rtp_C = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_c, ts_c, ssrc, payload_len_c); 
	rtp_D = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_d, ts_d, ssrc, payload_len_d);

	ulp_ok(rtp_A && rtp_B && rtp_C && rtp_D, "get memory for testing.");

	memset((char*)rtp_A + sizeof(ulp_rtp_hdr_t), 0x34, payload_len_a);
	memset((char*)rtp_B + sizeof(ulp_rtp_hdr_t), 0xf, payload_len_b);
	memset((char*)rtp_C + sizeof(ulp_rtp_hdr_t), 0x15, payload_len_c);
	memset((char*)rtp_D + sizeof(ulp_rtp_hdr_t), 0x68, payload_len_d);
	
	/* Submit packets to hash and generate FEC. */

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
	
	/* Should fail - levels > max level configured (1). */
	fec = ulp_gen_fec(send_policy, 100, snb);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");
	
	fec = ulp_gen_fec(send_policy, 3, snb);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec");

	/* Just checking. 2 levels, should succeed because both can be generated (L1 masks are same as L0). */
	fec = ulp_gen_fec(send_policy, 2, snb);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec L0 and L1 can be generated");
	free(fec);
	
	/* Just checking. 2 levels, should fail because L1 can't be generated. */
	ulp_ok(ulp_set_lvl_protection_mask16(send_policy, 1, 0xffff) == ulp_status_ok, "ulp_set_lvl_protection_mask16: L0");
	fec = ulp_gen_fec(send_policy, 2, snb);
	ulp_ok(!fec, "FEC generation should fail, ulp_gen_fec L1 can't be generated");
	
	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, snb);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");

	/* NOTE: 8 for header with long mask. */
	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 8 + L0_lk, "FEC length (1)");
	fec_len = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec_len, 10 + 8 + L0_lk, "FEC length (2)");

	/* Check. */
	cmp_ulp_ok(fec->hdr.e, 0, "E field");					/* reserved for future use */
	cmp_ulp_ok(fec->hdr.l, 1, "L field");					/* max group size is < 16 pkts */
	cmp_ulp_ok(fec->hdr.p_r, 0, "P recovery field");
	cmp_ulp_ok(fec->hdr.x_r, 0, "X recovery field");
	cmp_ulp_ok(fec->hdr.cc_r, 0, "CC recovery field");
	cmp_ulp_ok(fec->hdr.m_r, 0, "M recovery field");
	cmp_ulp_ok(fec->hdr.pt_r, 0, "PT recovery field");
	cmp_ulp_ok(ntohs(fec->hdr.snb), snb, "SN Base field");
	cmp_ulp_ok(ntohl(fec->hdr.ts_r), ts_a ^ ts_b ^ ts_c ^ ts_d, "TS recovery field");
	cmp_ulp_ok(ntohs(fec->hdr.len_r), payload_len_a ^ payload_len_b ^ payload_len_c ^ payload_len_d, "Length recovery field");
	
	cmp_ulp_ok(ntohs(fec->lvl[0].lk), L0_lk, "level L0 length");
	cmp_ulp_ok(ntohs(fec->lvl[0].mask16), L0_mask16, "level L0 mask");
	ulp_fec = (ulp_fec_lvl_64_t *)&fec->lvl[0];
	cmp_ulp_ok(ulp_fec->mask_cont, htonl(L0_mask_cont), "level L0 mask cont");

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
	
	/* Submit also FEC packet to the jitter buffer. */
	ulp_ok(switch_jb_put_redundancy((switch_rtp_packet_t *) fec, fec_len, policy, 0, ssrc) == SWITCH_STATUS_SUCCESS, "put FEC packet");

	/* Recover packet D - should succeed. */
	res = switch_rtp_recover(policy, seq_d, &ulp_err, &new_rtp, ssrc);
	ulp_ok(res == 1, "RTP recovery should succeed");
	
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

	/* Cleanup. */
	free(rtp_A);
	free(rtp_B);
	free(rtp_C);
	free(rtp_D);
	
	switch_jb_destroy(&jb);
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_core_destroy_memory_pool(&pool);
}
FST_TEST_END()
}
FST_SUITE_END()
}
FST_CORE_END()

