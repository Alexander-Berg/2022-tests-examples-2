#include <switch.h>
#include <test/switch_test.h>
#include "../../../src/switch_jitterbuffer.c"
#include "../../../src/switch_ulp.c"

/**
 * Test JB ULPFEC functions (ties of ULP with JB).
 *
 * - re-recovery
 *
 */
	
/*------------------ TEST setup ------------------------------------------------------------------------------------------*/
	static const uint8_t L0_gk = 4;				/* Number of packets in protection level L0. */
	static const uint16_t L0_lk = 1250;				/* Number of octets protected by level L0. */
	static const uint16_t L0_mask16 = 0xf000;
	static const uint32_t L0_mask_cont = 0x00000000;

	static const uint8_t version = 2;					/* RTP version 2. */
	static const uint8_t padding = 0;					/* No padding. */
	static const uint8_t extension = 0;					/* No extension. */
	static const uint8_t csrc_count = 0;					/* No contributing sources. */
	static const uint8_t mark = 0;
	static const uint8_t payload_type = 98;

	static const uint16_t snb1 = 21;
	static const uint16_t snb2 = 23;
	static const uint16_t snb3 = 25;
	static const uint16_t seq_a = 21;
	static const uint16_t seq_b = 22;
	static const uint16_t seq_c = 23;
	static const uint16_t seq_d = 24;
	static const uint16_t seq_e = 25;
	static const uint16_t seq_f = 26;
	static const uint16_t seq_g = 27;
	static const uint16_t seq_h = 28;
	
	static const uint32_t ts_a = 223344;
	static const uint32_t ts_b = 223364;
	static const uint32_t ts_c = 223384;
	static const uint32_t ts_d = 223404;
	static const uint32_t ts_e = 223424;
	static const uint32_t ts_f = 223444;
	static const uint32_t ts_g = 223464;
	static const uint32_t ts_h = 223484;

	static const uint16_t payload_len_a = 1200;
	static const uint16_t payload_len_b = 1200;
	static const uint16_t payload_len_c = 1250;
	static const uint16_t payload_len_d = 1250;
	static const uint16_t payload_len_e = 1220;
	static const uint16_t payload_len_f = 437;
	static const uint16_t payload_len_g = 1250;
	static const uint16_t payload_len_h = 326;

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
FST_SUITE_BEGIN(switch_ulp_jb)
{
FST_SETUP_BEGIN()
{
}
FST_SETUP_END()

FST_TEARDOWN_BEGIN()
{
}
FST_TEARDOWN_END()

FST_TEST_BEGIN(test_ulp_jb_re_recovery)
{
	uint32_t ssrc = 0;
	const char *err = NULL;
	ulp_fec_pkt_t *fec = NULL, *fec2 = NULL, *fec3 = NULL;				/* FEC data. */
	switch_size_t fec_len = 0, fec_len2 = 0, fec_len3 = 0;

	ulp_policy_t *policy = NULL, *send_policy = NULL;			/* ULP context */
	switch_jb_t *jb = NULL;

	switch_rtp_packet_t packet = {0};
	switch_size_t len = 0;

	switch_red_t *entry0 = NULL;
	switch_red_t *entry1 = NULL;
	switch_red_t *entry2 = NULL;

	ulp_rtp_pkt_t *rtp_A;
	ulp_rtp_pkt_t *rtp_B;
	ulp_rtp_pkt_t *rtp_C;
	ulp_rtp_pkt_t *rtp_D;
	ulp_rtp_pkt_t *rtp_E;
	ulp_rtp_pkt_t *rtp_F;
	ulp_rtp_pkt_t *rtp_G;
	ulp_rtp_pkt_t *rtp_H;

	ulp_rtp_msg_t fecs[ULP_LVL_GROUP_SIZE_MAX];
	switch_red_t *e;
	ulp_fec_pkt_t *fec_retrieved;
	uint8_t fec_n;

	switch_rtp_packet_t new_rtp;			/* recovered packet */

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
	ulp_ok(switch_jb_has_fec(jb), "must have flag SJB_HAS_ULPFEC set by switch_jb_create()");
	switch_jb_debug_level(jb, 10);

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

	ulp_ok(ulp_test_flag(send_policy, ULP_FL_USE_ULP) == 0, "ulp_test_flag: ULP_FL_USE_ULP");

	/* Generate RTP packets. */
	rtp_A = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_a, ts_a, ssrc, payload_len_a);
	rtp_B = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_b, ts_b, ssrc, payload_len_b); 
	rtp_C = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_c, ts_c, ssrc, payload_len_c); 
	rtp_D = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_d, ts_d, ssrc, payload_len_d);
	rtp_E = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_e, ts_e, ssrc, payload_len_e);
	rtp_F = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_f, ts_f, ssrc, payload_len_f);
	rtp_G = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_g, ts_g, ssrc, payload_len_g);
	rtp_H = ulp_gen_rtp(version, padding, extension, csrc_count, mark, payload_type, seq_h, ts_h, ssrc, payload_len_h);

	ulp_ok(rtp_A && rtp_B && rtp_C && rtp_D && rtp_E && rtp_F && rtp_G && rtp_H, "get memory for testing.");

	memset((char*)rtp_A + sizeof(ulp_rtp_hdr_t), 0x34, payload_len_a);
	memset((char*)rtp_B + sizeof(ulp_rtp_hdr_t), 0xf, payload_len_b);
	memset((char*)rtp_C + sizeof(ulp_rtp_hdr_t), 0x15, payload_len_c);
	memset((char*)rtp_D + sizeof(ulp_rtp_hdr_t), 0x68, payload_len_d);
	memset((char*)rtp_E + sizeof(ulp_rtp_hdr_t), 0x28, payload_len_e);
	memset((char*)rtp_F + sizeof(ulp_rtp_hdr_t), 0xa3, payload_len_f);
	memset((char*)rtp_G + sizeof(ulp_rtp_hdr_t), 0x18, payload_len_g);
	memset((char*)rtp_H + sizeof(ulp_rtp_hdr_t), 0xc3, payload_len_h);

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

	len = payload_len_e;
	memcpy(&packet.header, &rtp_E->hdr, 12);
	memcpy(packet.body, rtp_E->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet E");

	len = payload_len_f;
	memcpy(&packet.header, &rtp_F->hdr, 12);
	memcpy(packet.body, rtp_F->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet F");

	len = payload_len_g;
	memcpy(&packet.header, &rtp_G->hdr, 12);
	memcpy(packet.body, rtp_G->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet G");

	len = payload_len_h;
	memcpy(&packet.header, &rtp_H->hdr, 12);
	memcpy(packet.body, rtp_H->b, len);
	ulp_ok(switch_rtp_put_rtp_for_fec(rtp_session, &packet, len, 96, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet H");

	/* fec_n == 1 so this should succeed. */
	fec = ulp_gen_fec(send_policy, 1, snb1);
	ulp_ok(fec != NULL, "FEC generation should succeed, ulp_gen_fec");
	assert(fec);

	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + L0_lk, "FEC length (1)");
	fec_len = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec_len, 10 + 4 + L0_lk, "FEC length (2)");
	printf("fec_len = %" SWITCH_SIZE_T_FMT "\n", fec_len);

	fec2 = ulp_gen_fec(send_policy, 1, snb2);
	ulp_ok(fec2 != NULL, "FEC generation should succeed, ulp_gen_fec");
	assert(fec2);

	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + L0_lk, "FEC length (1)");
	fec_len2 = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec_len2, 10 + 4 + L0_lk, "FEC length (2)");
	printf("fec_len2 = %" SWITCH_SIZE_T_FMT  "\n", fec_len2);

	fec3 = ulp_gen_fec(send_policy, 1, snb3);
	ulp_ok(fec3 != NULL, "FEC generation should succeed, ulp_gen_fec");
	assert(fec3);

	cmp_ulp_ok(ulp_fec_last_len(send_policy), 10 + 4 + L0_lk, "FEC length (1)");
	fec_len3 = ulp_fec_last_len(send_policy);
	cmp_ulp_ok(fec_len3, 10 + 4 + L0_lk, "FEC length (2)");
	printf("fec_len3 = %" SWITCH_SIZE_T_FMT "\n", fec_len3);

	/* Check FEC1 */
	cmp_ulp_ok(fec->hdr.e, 0, "E field");					/* reserved for future use */
	cmp_ulp_ok(fec->hdr.l, 0, "L field");					/* max group size is < 16 pkts */
	cmp_ulp_ok(fec->hdr.p_r, 0, "P recovery field");
	cmp_ulp_ok(fec->hdr.x_r, 0, "X recovery field");
	cmp_ulp_ok(fec->hdr.cc_r, 0, "CC recovery field");
	cmp_ulp_ok(fec->hdr.m_r, 0, "M recovery field");
	cmp_ulp_ok(fec->hdr.pt_r, 0, "PT recovery field");
	cmp_ulp_ok(ntohs(fec->hdr.snb), snb1, "SN Base field");
	cmp_ulp_ok(ntohl(fec->hdr.ts_r), ts_a ^ ts_b ^ ts_c ^ ts_d, "TS recovery field");
	cmp_ulp_ok(ntohs(fec->hdr.len_r), payload_len_a ^ payload_len_b ^ payload_len_c ^ payload_len_d, "Length recovery field");

	/* Check FEC2 */
	cmp_ulp_ok(fec2->hdr.e, 0, "E field");					/* reserved for future use */
	cmp_ulp_ok(fec2->hdr.l, 0, "L field");					/* max group size is < 16 pkts */
	cmp_ulp_ok(fec2->hdr.p_r, 0, "P recovery field");
	cmp_ulp_ok(fec2->hdr.x_r, 0, "X recovery field");
	cmp_ulp_ok(fec2->hdr.cc_r, 0, "CC recovery field");
	cmp_ulp_ok(fec2->hdr.m_r, 0, "M recovery field");
	cmp_ulp_ok(fec2->hdr.pt_r, 0, "PT recovery field");
	cmp_ulp_ok(ntohs(fec2->hdr.snb), snb2, "SN Base field");
	cmp_ulp_ok(ntohl(fec2->hdr.ts_r), ts_c ^ ts_d ^ ts_e ^ ts_f, "TS recovery field");
	cmp_ulp_ok(ntohs(fec2->hdr.len_r), payload_len_c ^ payload_len_d ^ payload_len_e ^ payload_len_f, "Length recovery field");

	cmp_ulp_ok(ntohs(fec->lvl[0].lk), L0_lk, "level L0 length");
	cmp_ulp_ok(ntohs(fec->lvl[0].mask16), L0_mask16, "level L0 mask");

	len = payload_len_a;
	memcpy(&packet.header, &rtp_A->hdr, 12);
	memcpy(packet.body, rtp_A->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet A");
	
	/* don't put packet B into JB - it will be marked as missing. */

	/* don't put packet C into JB - it will be marked as missing. */

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

	/* don't put packet G into JB - it will be marked as missing. */

	len = payload_len_h;
	memcpy(&packet.header, &rtp_H->hdr, 12);
	memcpy(packet.body, rtp_H->b, len);
	ulp_ok(switch_jb_put_packet(jb, &packet, len + 12, 0) == SWITCH_STATUS_SUCCESS, "put RTP packet H");

	ulp_ok(switch_jb_get_packet_by_seq(jb, htons(seq_b), &new_rtp, &len) == SWITCH_STATUS_NOTFOUND,
			"retrieving packet from JB should fail - SEQ B ");

	ulp_ok(switch_jb_get_packet_by_seq(jb, htons(seq_c), &new_rtp, &len) == SWITCH_STATUS_NOTFOUND,
			"retrieving packet from JB should fail - SEQ C");

	ulp_ok(switch_jb_get_packet_by_seq(jb, htons(seq_g), &new_rtp, &len) == SWITCH_STATUS_NOTFOUND,
			"retrieving packet from JB should fail - SEQ G");

	/* submit FEC 1 */
	ulp_ok(switch_red_ulpfec_parse(policy, fec, fec_len) == SWITCH_STATUS_SUCCESS, "parsing of FEC packet should succeed");
	switch_malloc(entry0, sizeof(switch_red_t));
	memset(entry0, 0, sizeof(switch_red_t));
	entry0->redundancy = (switch_rtp_packet_t *)fec;
	entry0->redundancy_len = fec_len;
	entry0->next = NULL;
	entry0->n = 1;
	entry0->up = NULL;
	switch_core_inthash_insert(jb->redundancy_hash, htons(snb1), (void *) entry0);

	/* submit FEC 2 */
	ulp_ok(switch_red_ulpfec_parse(policy, fec2, fec_len2) == SWITCH_STATUS_SUCCESS, "parsing of FEC packet should succeed");
	switch_malloc(entry1, sizeof(switch_red_t));
	memset(entry1, 0, sizeof(switch_red_t));
	entry1->redundancy = (switch_rtp_packet_t *)fec2;
	entry1->redundancy_len = fec_len2;
	entry1->next = NULL;
	entry1->n = 1;
	entry1->up = entry0;
	switch_core_inthash_insert(jb->redundancy_hash, htons(snb2), (void *) entry1);

	/* submit FEC 3 */
	ulp_ok(switch_red_ulpfec_parse(policy, fec3, fec_len3) == SWITCH_STATUS_SUCCESS, "parsing of FEC packet should succeed");
	switch_malloc(entry2, sizeof(switch_red_t));
	memset(entry2, 0, sizeof(switch_red_t));
	entry2->redundancy = (switch_rtp_packet_t *)fec3;
	entry2->redundancy_len = fec_len3;
	entry2->next = NULL;
	entry2->n = 1;
	entry2->up = entry1;
	switch_core_inthash_insert(jb->redundancy_hash, htons(snb3), (void *) entry2);
	jb->redundancy_first = entry2;

	e = switch_core_inthash_find(jb->redundancy_hash, htons(snb1));
	assert(e);
	fec_retrieved = (ulp_fec_pkt_t *) e->redundancy;
	cmp_ulp_ok(ntohs(fec_retrieved->hdr.snb), snb1, "SN Base field");

	e = switch_core_inthash_find(jb->redundancy_hash, htons(snb2));
	assert(e);
	fec_retrieved = (ulp_fec_pkt_t *) e->redundancy;
	cmp_ulp_ok(ntohs(fec_retrieved->hdr.snb), snb2, "SN Base field");

	e = switch_core_inthash_find(jb->redundancy_hash, htons(snb3));
	assert(e);
	fec_retrieved = (ulp_fec_pkt_t *) e->redundancy;
	cmp_ulp_ok(ntohs(fec_retrieved->hdr.snb), snb3, "SN Base field");

	fec_n = jb_ulp_cb_find_fecs_for_seq_on_lvl(policy, seq_b, 0, fecs);
	ulp_ok(fec_n != 0, "should have FEC for SEQ B")
	ulp_rtp_free(fecs, fec_n);

	fec_n = jb_ulp_cb_find_fecs_for_seq_on_lvl(policy, seq_c, 0, fecs);
	ulp_ok(fec_n != 0, "should have FEC for SEQ C")
	ulp_rtp_free(fecs, fec_n);

	fec_n = jb_ulp_cb_find_fecs_for_seq_on_lvl(policy, seq_g, 0, fecs);
	ulp_ok(fec_n != 0, "should have FEC for SEQ G")
	ulp_rtp_free(fecs, fec_n);

	/* should trigger re-recovery - seq B, seq C and seq G should be recovered*/
	switch_jb_recover_any_packets(fec3, policy, ssrc);

	ulp_ok(switch_jb_get_packet_by_seq(jb, htons(seq_b), &new_rtp, &len) == SWITCH_STATUS_SUCCESS, 
			"retrieving recovered packet from JB should succeed - SEQ B"); 
	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_B->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_B->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_B->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_B->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_B->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_B->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_B->hdr.ts, "ulp_recover (header->ts)");
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_B->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_B, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_B + sizeof(switch_rtp_hdr_t), payload_len_b), 0, "ulp_recover: payload");

	ulp_ok(switch_jb_get_packet_by_seq(jb, htons(seq_c), &new_rtp, &len) == SWITCH_STATUS_SUCCESS, 
			"retrieving recovered packet from JB should succeed - SEQ C"); 

	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_C->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_C->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_C->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_C->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_C->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_C->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_C->hdr.ts, "ulp_recover (header->ts)");
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_C->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_C, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_C + sizeof(switch_rtp_hdr_t), payload_len_c), 0, "ulp_recover: payload");

	ulp_ok(switch_jb_get_packet_by_seq(jb, htons(seq_g), &new_rtp, &len) == SWITCH_STATUS_SUCCESS, 
			"retrieving recovered packet from JB should succeed - SEQ G"); 

	cmp_ulp_ok(new_rtp.header.version, 2, "ulp_recover (header->version)");
	cmp_ulp_ok(new_rtp.header.p, rtp_G->hdr.p, "ulp_recover (header->p)");
	cmp_ulp_ok(new_rtp.header.x, rtp_G->hdr.x, "ulp_recover (header->x)");
	cmp_ulp_ok(new_rtp.header.cc, rtp_G->hdr.cc, "ulp_recover header->cc)");
	cmp_ulp_ok(new_rtp.header.m, rtp_G->hdr.m, "ulp_recover (header->m)");
	cmp_ulp_ok(new_rtp.header.pt, rtp_G->hdr.pt, "ulp_recover (header->pt)");
	cmp_ulp_ok(new_rtp.header.seq, rtp_G->hdr.seq, "ulp_recover (header->seq)");
	cmp_ulp_ok(new_rtp.header.ts, rtp_G->hdr.ts, "ulp_recover (header->ts)");
	cmp_ulp_ok(new_rtp.header.ssrc, rtp_G->hdr.ssrc, "ulp_recover (header->ssrc)");
	cmp_ulp_ok(memcmp((char*)&new_rtp, rtp_G, sizeof(switch_rtp_hdr_t)), 0, "ulp_recover: header");
	cmp_ulp_ok(memcmp((char*)&new_rtp + sizeof(switch_rtp_hdr_t), (char*)rtp_G + sizeof(switch_rtp_hdr_t), payload_len_g), 0, "ulp_recover: payload");

	/*last recovered packet is seq G*/
	ulp_ok(ulp_rtp_last_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_g, "ulp_rtp_last_len");
	ulp_ok(ulp_rtp_last_recover_len(policy) == sizeof(switch_rtp_hdr_t) + payload_len_g, "ulp_rtp_last_recover_len");

	/* Cleanup. */
	free(rtp_A);
	free(rtp_B);
	free(rtp_C);
	free(rtp_D);
	free(rtp_E);
	free(rtp_F);
	free(rtp_G);
	free(rtp_H);
	
	switch_jb_destroy(&jb);
	switch_rtp_destroy_rtp_for_fec_hash(rtp_session);
	switch_core_destroy_memory_pool(&pool);
}
FST_TEST_END()
}
FST_SUITE_END()
}
FST_CORE_END()

