#include <switch.h>
#include <test/switch_test.h>

/* before adding a pcap file: tcprewrite --dstipmap=X.X.X.X/32:192.168.0.1/32 --srcipmap=X.X.X.X/32:192.168.0.2/32 -i in.pcap -o out.pcap */

#include <pcap.h>

#ifndef MSG_CONFIRM
#define MSG_CONFIRM 0
#endif

static const char *rx_host = "127.0.0.1";
static switch_port_t rx_port = 12346;
static const char *tx_host = "127.0.0.1";
static switch_port_t tx_port = 54320;
static switch_rtp_t *rtp_session = NULL;
static switch_rtp_flag_t flags[SWITCH_RTP_FLAG_INVALID] = {0};
const char *err = NULL;
static const switch_payload_t TEST_PT = 124;
static const switch_payload_t VIDEO_TEST_PT = 102;
switch_rtp_packet_t rtp_packet;
switch_io_flag_t io_flags;
switch_payload_t read_pt;

#define EST_LOSS 0
#define EST_JITTER 1
#define EST_RTT 2

#define MAXVALS 10

#define NTP_TIME_OFFSET 2208988800UL

//#define USE_RTCP_PCAP 

/* https://www.tcpdump.org/pcap.html */
/* IP header */
struct sniff_ip {
	u_char ip_vhl;		/* version << 4 | header length >> 2 */
	u_char ip_tos;		/* type of service */
	u_short ip_len;		/* total length */
	u_short ip_id;		/* identification */
	u_short ip_off;		/* fragment offset field */
#define IP_RF 0x8000		/* reserved fragment flag */
#define IP_DF 0x4000		/* dont fragment flag */
#define IP_MF 0x2000		/* more fragments flag */
#define IP_OFFMASK 0x1fff	/* mask for fragmenting bits */
	u_char ip_ttl;		/* time to live */
	u_char ip_p;		/* protocol */
	u_short ip_sum;		/* checksum */
	struct in_addr ip_src,ip_dst; /* source and dest address */
};

#define IP_HL(ip)		(((ip)->ip_vhl) & 0x0f)

/* switch_rtp.c - calc_local_lsr_now()  */
static inline uint32_t test_calc_local_lsr_now(switch_time_t now, uint32_t past /*milliseconds*/) 
{
//	switch_time_t now;
	uint32_t ntp_sec, ntp_usec, lsr_now, sec;
//	now = switch_micro_time_now() - (past * 1000);
	now = now - (past * 1000);
	sec = (uint32_t)(now/1000000);        /* convert to seconds     */
	ntp_sec = sec+NTP_TIME_OFFSET;  /* convert to NTP seconds */
	ntp_usec = (uint32_t)(now - ((switch_time_t) sec*1000000)); /* remove seconds to keep only the microseconds */
	 
	lsr_now = (uint32_t)(ntp_usec*0.065536) | (ntp_sec&0x0000ffff)<<16; /* 0.065536 is used for convertion from useconds to fraction of     65536 (x65536/1000000) */
	return lsr_now;
}

static void test_prepare_rtcp(void *rtcp_packet, float est_last, uint32_t rtt, uint8_t loss) 
{
	/* taken from switch_rtp.c, rtcp_generate_sender_info() */
	/* === */
	char *rtcp_sr_trigger = rtcp_packet;
	switch_time_t now;
	uint32_t sec, ntp_sec, ntp_usec;
	uint32_t ntp_msw;
	uint32_t ntp_lsw;
	uint32_t *ptr_msw;
	uint32_t *ptr_lsw;
	uint32_t lsr;
	uint32_t *ptr_lsr;
	uint32_t dlsr = 0;
	uint32_t *ptr_dlsr;
	uint8_t *ptr_loss;

	now = switch_micro_time_now();
	sec = (uint32_t)(now/1000000);        /* convert to seconds     */
	ntp_sec = sec+NTP_TIME_OFFSET;  /* convert to NTP seconds */
	ntp_msw = htonl(ntp_sec);   /* store result in "most significant word" */
	ntp_usec = (uint32_t)(now - (sec*1000000)); /* remove seconds to keep only the microseconds */
	ntp_lsw = htonl((u_long)(ntp_usec*(double)(((uint64_t)1)<<32)*1.0e-6)); 

	/* === */

	/*patch the RTCP payload to set the RTT we want */

	ptr_msw = (uint32_t *)rtcp_sr_trigger + 2;
	*ptr_msw = ntp_msw;
	
	ptr_lsw = (uint32_t *)rtcp_sr_trigger + 3;
	*ptr_lsw = ntp_lsw;

	lsr = test_calc_local_lsr_now(now, est_last * 1000 + rtt /*ms*/);

	ptr_lsr = (uint32_t *)rtcp_sr_trigger + 11;
	*ptr_lsr  = htonl(lsr);

	ptr_dlsr = (uint32_t *)rtcp_sr_trigger + 12;
	*ptr_dlsr  = htonl(dlsr);

	ptr_loss = (uint8_t *)rtcp_sr_trigger + 32;
	*ptr_loss  = loss;
}


FST_CORE_BEGIN("./conf_estimators")

{
FST_SUITE_BEGIN(switch_estimators)
{
FST_SETUP_BEGIN()
{
	fst_requires_module("mod_loopback");
}
FST_SETUP_END()

FST_TEARDOWN_BEGIN()
{
}
FST_TEARDOWN_END()
	FST_TEST_BEGIN(test_estimators_and_cusum_detectors)
	{
		switch_core_session_t *session = NULL;
		switch_channel_t *channel = NULL;
		switch_status_t status;
		switch_call_cause_t cause;
		switch_frame_flag_t frameflags = { 0 };
		switch_io_flag_t io_flags = { 0 };
		switch_payload_t pt = { 0 };
		switch_stream_handle_t stream = { 0 };
		static char rtp_packet[] = "\x80\x7c\x03\x48\x00\x0c\x55\x80\x78\x9d\xac\x45\x78\x8b\xc3\x86\x74"
			"\x66\x35\x79\x8a\x6d\xb0\x04\x5d\x81\x27\xb3\xe2\xb2\xc5\xe6\x34\x82\x73\x97\xe0\x6e"
			"\xfd\x00\xe2\x93\xcb\xdc\x55\x2e\x96\x51\x43\xe8\x84\xab\x32\xd6\xa3\xec\x12\x3f\x58";
		struct sockaddr_in     servaddr_rtp; 
		struct sockaddr_in     servaddr_rtcp;
		int sockfd_rtp, sockfd_rtcp, ret;
		struct hostent *server;
		uint32_t datalen;
		cusum_kalman_detector_t *det_loss = NULL;
		cusum_kalman_detector_t *det_rtt = NULL;
		kalman_estimator_t * est_loss = NULL;
		kalman_estimator_t * est_rtt = NULL;
		uint8_t readvals_loss[MAXVALS] = {5, 2, 1, 25, 50, 75, 85, 20, 27, 150};
		float readvals_rtt[MAXVALS] = {0.5, 0.2, 0.1, 0.25, 0.5, 0.75, 0.85, 0.2, 0.27, 0.15};
		int  k = 0, sudden_change_loss = 0, sudden_change_rtt = 0;
		struct sockaddr_in sin;
		socklen_t len = sizeof(sin);
                int16_t *seq;

		status = switch_ivr_originate(NULL, &session, &cause, "null/+15553334444", 2, NULL, NULL, NULL, NULL, NULL, SOF_NONE, NULL, NULL);
		fst_requires(session);
		fst_check(status == SWITCH_STATUS_SUCCESS);

		flags[SWITCH_RTP_FLAG_USE_TIMER] = 1;
		flags[SWITCH_RTP_FLAG_ADJ_BITRATE_CAP] = 1;
		flags[SWITCH_RTP_FLAG_ESTIMATORS] = 1;
		flags[SWITCH_RTP_FLAG_ENABLE_RTCP] = 1;
		flags[SWITCH_RTP_FLAG_NOBLOCK] = 1;
		rtp_session = switch_rtp_new(rx_host, rx_port, tx_host, tx_port, TEST_PT, 8000, 20 * 1000, flags, "soft", &err, switch_core_session_get_pool(session), 0, 0);
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "switch_rtp_new() returned: %s\n", err);
		fst_xcheck(rtp_session != NULL, "switch_rtp_new()");
		fst_requires(switch_rtp_ready(rtp_session));
		switch_rtp_activate_rtcp(rtp_session, 5000, tx_port + 1, 0);
		switch_rtp_set_default_payload(rtp_session, TEST_PT);
		switch_core_media_set_rtp_session(session, SWITCH_MEDIA_TYPE_AUDIO, rtp_session);
		channel = switch_core_session_get_channel(session);
		fst_requires(channel);
		session = switch_rtp_get_core_session(rtp_session);
		fst_requires(session);
		switch_rtp_set_ssrc(rtp_session, 0xabcd);
		switch_rtp_set_remote_ssrc(rtp_session, 0x789dac45);
		switch_rtp_use_estimators(rtp_session, SWITCH_TRUE);

		status = switch_rtp_activate_jitter_buffer(rtp_session, 1, 10, 80, 8000);
		fst_check(status == SWITCH_STATUS_SUCCESS);

		SWITCH_STANDARD_STREAM(stream);
		switch_api_execute("fsctl", "debug_level 4", session, &stream);
		switch_safe_free(stream.data);

		if ( (sockfd_rtp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		}

		if ( (sockfd_rtcp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		} 

		memset(&servaddr_rtp, 0, sizeof(servaddr_rtp)); 
		                                    
		servaddr_rtp.sin_family = AF_INET; 
		servaddr_rtp.sin_port = htons(rx_port); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtp.sin_addr.s_addr, server->h_length);

		servaddr_rtcp.sin_family = AF_INET; 
		servaddr_rtcp.sin_port = htons(rx_port + 1); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtcp.sin_addr.s_addr, server->h_length);

		/*get local UDP port (tx side) to trick FS into accepting our packets*/
#ifdef MSG_CONFIRM
		ret = sendto(sockfd_rtp, NULL, 0, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp));
#else
		ret = sendto(sockfd_rtp, NULL, 0, 0, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp));
#endif		
		if (ret < 0){
			perror("sendto");
			exit(1);
		}

		len = sizeof(sin);
		if (getsockname(sockfd_rtp, (struct sockaddr *)&sin, &len) == -1) {
			perror("getsockname");
			exit(1);
		} else {
			switch_rtp_set_remote_address(rtp_session, tx_host, ntohs(sin.sin_port), 0, SWITCH_FALSE, &err);
		}

		seq =  (int16_t *)&rtp_packet + 1;
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "Sent RTP. Seq = %d\n", htons(*seq));
#ifdef MSG_CONFIRM
		ret = sendto(sockfd_rtp, (const char *) &rtp_packet, sizeof(rtp_packet), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
#else
		ret = sendto(sockfd_rtp, (const char *) &rtp_packet, sizeof(rtp_packet), 0, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
#endif
		if (ret < 0){
			perror("sendto");
			exit(1);
		}

		do {
			status = switch_rtp_read(rtp_session, (void *)&rtp_packet, &datalen, &pt, &frameflags, io_flags);
			fst_requires(status == SWITCH_STATUS_SUCCESS);
		}  while (pt != TEST_PT /*PT of RTP packet, skip CNG*/); 


		for (k = 0; k < MAXVALS; k++) {
			// estimators and detectors are initialized , feed them some (fake) data, eg: as if we get more RTCP
			if (!est_loss) { // gets initialized with first RTP packet
				est_loss = (kalman_estimator_t *)switch_rtp_kalman_estimator_get_by_index(rtp_session, EST_LOSS);
			} else {
				switch_kalman_estimate(est_loss, readvals_loss[k], EST_LOSS);
			}
			if (!est_rtt) { // gets initialized with first RTP packet
				est_rtt = (kalman_estimator_t *)switch_rtp_kalman_estimator_get_by_index(rtp_session, EST_RTT);
			} else {
				switch_kalman_estimate(est_rtt, readvals_rtt[k], EST_RTT);
			}

			if (!det_loss) { // gets initialized with first RTP packet
				det_loss = (cusum_kalman_detector_t *)switch_rtp_kalman_detector_get_by_index(rtp_session, EST_LOSS);
			} else {
				if (switch_kalman_cusum_detect_change(det_loss, readvals_loss[k], est_loss->val_estimate_last)) {
					sudden_change_loss++;
				}
			}

			if (!det_rtt) { // gets initialized with first RTP packet
				det_rtt = (cusum_kalman_detector_t *)switch_rtp_kalman_detector_get_by_index(rtp_session, EST_RTT);
			} else {
				if (switch_kalman_cusum_detect_change(det_rtt, readvals_rtt[k], est_rtt->val_estimate_last)) {
					sudden_change_rtt++;
				}
			}
		}

		fst_check(sudden_change_loss == 3);
		fst_check(sudden_change_rtt == 3);


		close(sockfd_rtp);
		switch_channel_hangup(channel, SWITCH_CAUSE_NORMAL_CLEARING);
		switch_rtp_destroy(&rtp_session);
		switch_core_session_rwunlock(session);
	}
	FST_TEST_END()

	FST_TEST_BEGIN(test_estimator_cusum_for_audio)
	{
		switch_core_session_t *session = NULL;
		switch_channel_t *channel = NULL;
		switch_status_t status;
		switch_call_cause_t cause;
		switch_frame_flag_t frameflags = { 0 };
		switch_io_flag_t io_flags = { 0 };
		switch_payload_t pt = { 0 };
		switch_stream_handle_t stream = { 0 };
		switch_frame_t *read_frame, *write_frame;
		pcap_t *pcap;
		const unsigned char *packet;
		char errbuf[PCAP_ERRBUF_SIZE];
		struct pcap_pkthdr header;
		struct sockaddr_in     servaddr_rtp; 
		struct sockaddr_in     servaddr_rtcp;
		int sockfd_rtp;
		int sockfd_rtcp;
		const struct sniff_ip *ip; /* The IP header */
		int size_ip, ret, jump_over;
		struct hostent *server;
		cusum_kalman_detector_t *det_loss = NULL;
		cusum_kalman_detector_t *det_rtt = NULL;
		kalman_estimator_t * est_loss = NULL;
		kalman_estimator_t * est_rtt = NULL;
		uint8_t readvals_loss[MAXVALS] = {5, 2, 1, 25, 50, 75, 85, 20, 27, 90};
		float readvals_rtt[MAXVALS] = {0.5, 0.6, 0.7, 0.65, 0.8, 0.75, 0.85, 0.4, 0.57, 0.65};
		char rtcp_sr_trigger[] = "\x81\xc8\x00\x0c\x78\x9d\xac\x45\xe2\x67\xa5\x74\x30\x60\x56\x81\x00\x19"
			"\xaa\x00\x00\x00\x06\xd7\x00\x01\x2c\x03\x5e\xbd\x2f\x0b\x00"
			"\x00\x00\x00\x00\x00\x57\xc4\x00\x00\x00\x39\xa5\x73\xfe\x90\x00\x00\x2c\x87"
			"\x81\xca\x00\x0c\x78\x9d\xac\x45\x01\x18\x73\x69\x70\x3a\x64\x72\x40\x31\x39\x32\x2e"
			"\x31\x36\x38\x2e\x30\x2e\x31\x33\x3a\x37\x30\x36\x30\x06\x0e\x4c\x69\x6e\x70\x68\x6f"
			"\x6e\x65\x2d\x33\x2e\x36\x2e\x31\x00\x00";
		switch_media_handle_t *media_handle;
		switch_core_media_params_t *mparams;
		uint32_t add_rtt;

		int count = 0, k = 0, sudden_loss = 0, sudden_rtt = 0;
		char *r_sdp;
		uint8_t match = 0, p = 0;
		struct sockaddr_in sin;
		socklen_t len = sizeof(sin);

		rx_port = rx_port + 2;
		tx_port = tx_port + 2;
		status = switch_ivr_originate(NULL, &session, &cause, "null/+15553334444", 2, NULL, NULL, NULL, NULL, NULL, SOF_NONE, NULL, NULL);
		fst_requires(session);
		fst_check(status == SWITCH_STATUS_SUCCESS);

		flags[SWITCH_RTP_FLAG_USE_TIMER] = 1;
		flags[SWITCH_RTP_FLAG_ADJ_BITRATE_CAP] = 1;
		flags[SWITCH_RTP_FLAG_ESTIMATORS] = 1;
		flags[SWITCH_RTP_FLAG_ENABLE_RTCP] = 1;
		flags[SWITCH_RTP_FLAG_NOBLOCK] = 1;
		rtp_session = switch_rtp_new(rx_host, rx_port, tx_host, tx_port, TEST_PT, 8000, 20 * 1000, flags, "soft", &err, switch_core_session_get_pool(session), 0, 0);
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "switch_rtp_new() returned: %s\n", err);
		fst_xcheck(rtp_session != NULL, "switch_rtp_new()");
		fst_requires(switch_rtp_ready(rtp_session));
		switch_rtp_activate_rtcp(rtp_session, 5000, tx_port + 1, 0);
		switch_rtp_set_default_payload(rtp_session, TEST_PT);
		channel = switch_core_session_get_channel(session);
		fst_requires(channel);
		session = switch_rtp_get_core_session(rtp_session);
		fst_requires(session);
		switch_rtp_set_ssrc(rtp_session, 0xabcd);
		switch_rtp_set_remote_ssrc(rtp_session, 0x789dac45);
		switch_rtp_use_estimators(rtp_session, SWITCH_TRUE);

		status = switch_rtp_activate_jitter_buffer(rtp_session, 1, 10, 80, 8000);
		fst_check(status == SWITCH_STATUS_SUCCESS);

		// set media handle for codec control.
		mparams  = switch_core_session_alloc(session, sizeof(switch_core_media_params_t));
		mparams->num_codecs = 1;
		mparams->inbound_codec_string = switch_core_session_strdup(session, "opus");
		mparams->outbound_codec_string = switch_core_session_strdup(session, "opus");
		mparams->rtpip = switch_core_session_strdup(session, (char *)rx_host);

		status = switch_media_handle_create(&media_handle, session, mparams);
		fst_requires(status == SWITCH_STATUS_SUCCESS);

		switch_channel_set_variable(channel, "absolute_codec_string", "opus");

		switch_channel_set_variable(channel, SWITCH_LOCAL_MEDIA_IP_VARIABLE, rx_host);
		switch_channel_set_variable_printf(channel, SWITCH_LOCAL_MEDIA_PORT_VARIABLE, "%d", rx_port);

		/* need to use SDP - core media - codec control  */
		r_sdp = switch_core_session_sprintf(session,
		"v=0\n"
		"o=FreeSWITCH 1234567890 1234567890 IN IP4 %s\n"
		"s=FreeSWITCH\n"
		"c=IN IP4 %s\n"
		"t=0 0\n"
		"m=audio %u RTP/AVP %d\n"
		"a=ptime:20\n"
		"a=sendrecv\n"
		"a=rtpmap:%d OPUS/48000/2\n",
		tx_host, tx_host, tx_port, TEST_PT, TEST_PT);
		 
		switch_core_media_prepare_codecs(session, SWITCH_FALSE);
		   
		match = switch_core_media_negotiate_sdp(session, r_sdp, &p, SDP_TYPE_REQUEST);
		fst_requires(match == 1);

		status = switch_core_media_choose_ports(session, SWITCH_TRUE, SWITCH_FALSE);
		fst_requires(status == SWITCH_STATUS_SUCCESS);

		status = switch_core_media_activate_rtp(session);
		fst_requires(status == SWITCH_STATUS_SUCCESS);
		switch_rtp_reset(rtp_session);

		pcap = pcap_open_offline("pcap/rtp-opus-beep.pcap", errbuf);
		fst_requires(pcap);

		SWITCH_STANDARD_STREAM(stream);
		switch_api_execute("fsctl", "debug_level 2", session, &stream);
		switch_api_execute("opus_debug", "on", session, &stream);
		switch_safe_free(stream.data);

		switch_frame_alloc(&write_frame, SWITCH_RECOMMENDED_BUFFER_SIZE);
		write_frame->codec = switch_core_session_get_write_codec(session);

		if ( (sockfd_rtp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		}

		if ( (sockfd_rtcp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		} 

		memset(&servaddr_rtp, 0, sizeof(servaddr_rtp)); 
		                                    
		servaddr_rtp.sin_family = AF_INET; 
		servaddr_rtp.sin_port = htons(rx_port); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtp.sin_addr.s_addr, server->h_length);

		servaddr_rtcp.sin_family = AF_INET; 
		servaddr_rtcp.sin_port = htons(rx_port + 1); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtcp.sin_addr.s_addr, server->h_length);

		/*get local UDP port (tx side) to trick FS into accepting our packets*/
		ret = sendto(sockfd_rtp, NULL, 0, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
		if (ret < 0){
			perror("sendto");
			exit(1);
		}

		len = sizeof(sin);
		if (getsockname(sockfd_rtp, (struct sockaddr *)&sin, &len) == -1) {
			perror("getsockname");
			exit(1);
		} else {
			switch_rtp_set_remote_address(rtp_session, tx_host, ntohs(sin.sin_port), 0, SWITCH_FALSE, &err);
		}

		while ((packet = pcap_next(pcap, &header))) {
			/*assume only UDP/RTP packets in the pcap*/
			uint32_t datalen = header.caplen;
			size_t len;
			uint32_t *codec_bitrate;

			len = header.caplen;

			ip = (struct sniff_ip*)(packet + 14);
			size_ip = IP_HL(ip) * 4;

			jump_over = 14 /*SIZE_ETHERNET*/ + size_ip + 8 /*UDP HDR SIZE */;
			packet += jump_over;

			if (packet[0] == 0x80) {
				int16_t *seq =  (int16_t *)packet + 1;
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "Sent RTP from pcap. Seq = %d\n", htons(*seq));
				ret = sendto(sockfd_rtp, (const char *) packet, len - jump_over, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}
			} 
#ifdef USE_RTCP_PCAP
			else if (packet[0] == 0x81) {
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "Sent RTCP\n");
				ret = sendto(sockfd_rtcp, (const char *) packet, len - jump_over, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}
			}
#endif 

			status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
			fst_requires(status == SWITCH_STATUS_SUCCESS);
			if (pt == SWITCH_RTP_CNG_PAYLOAD /*timeout*/) continue;

			count++;

			if (count % 10) {
				if (k == MAXVALS - 1) k = 0;
				// estimators and detectors are initialized , feed them some (fake) data, as if we get more RTCP
				if (!est_loss) { // gets initialized with first RTP packet
					est_loss = (kalman_estimator_t *)switch_rtp_kalman_estimator_get_by_index(rtp_session, EST_LOSS);
				} else {
					switch_kalman_estimate(est_loss, readvals_loss[k], EST_LOSS);
				}
				if (!est_rtt) { // gets initialized with first RTP packet
					est_rtt = (kalman_estimator_t *)switch_rtp_kalman_estimator_get_by_index(rtp_session, EST_RTT);
				} else {
					switch_kalman_estimate(est_rtt, readvals_rtt[k], EST_RTT);
				}
			}

			if (!det_loss) { // gets initialized with first RTP packet
				det_loss = (cusum_kalman_detector_t *)switch_rtp_kalman_detector_get_by_index(rtp_session, EST_LOSS);
			} else {
				if (switch_kalman_cusum_detect_change(det_loss, readvals_loss[k], est_loss->val_estimate_last)) {
					sudden_loss++;
					switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Sudden change in the mean value of packet loss ! %u:%f \n", readvals_loss[k], est_loss->val_estimate_last);
				}
			}

			if (!det_rtt) { // gets initialized with first RTP packet
				det_rtt = (cusum_kalman_detector_t *)switch_rtp_kalman_detector_get_by_index(rtp_session, EST_RTT);
			} else {
				if (switch_kalman_cusum_detect_change(det_rtt, readvals_rtt[k], est_rtt->val_estimate_last)) {
					sudden_rtt++;
					switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Sudden change in the mean value of rtt ! %f:%f \n", readvals_rtt[k], est_rtt->val_estimate_last);
				}
			}

			if (count % 10) {
				k++;
			}

			fst_requires(datalen <= SWITCH_RECOMMENDED_BUFFER_SIZE);
			write_frame->datalen = datalen;
			memcpy(write_frame->data, packet, datalen);

			// decode what we have in the PCAP  (mod_loopback will get L16 frames- null_channel_write_frame() )
			status = switch_core_session_write_frame(session, write_frame, frameflags, 0);
			fst_requires(status == SWITCH_STATUS_SUCCESS);

			if (count == 100) { /*2 seconds into the call*/
				uint32_t *codec_bitrate = NULL;

				add_rtt = 1200;
				fst_requires(est_rtt);
				fst_requires(est_loss);
				test_prepare_rtcp(&rtcp_sr_trigger, est_rtt->val_estimate_last, add_rtt, 0xa0);

				ret = sendto(sockfd_rtcp, (const char *) rtcp_sr_trigger, sizeof(rtcp_sr_trigger), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}

				status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
				fst_requires(status == SWITCH_STATUS_SUCCESS);
				switch_core_media_codec_control(session, SWITCH_MEDIA_TYPE_AUDIO, SWITCH_IO_WRITE, SCC_GET_BITRATE, SCCT_INT, NULL, SCCT_NONE, NULL, NULL, (void *)&codec_bitrate);
				// must have went to minimum bitrate.
				fst_requires(*codec_bitrate == 6000);
			}

			// what we get in RTCP sets the way OPUS will set bitrate and packet loss (via codec control)
			status = switch_core_session_read_frame(session, &read_frame, frameflags, 0); // will encode silence 
			fst_requires(status == SWITCH_STATUS_SUCCESS);

			switch_core_media_codec_control(session, SWITCH_MEDIA_TYPE_AUDIO, SWITCH_IO_WRITE, SCC_GET_BITRATE, SCCT_INT, NULL, SCCT_NONE, NULL, NULL, (void *)&codec_bitrate);
		}

		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "sudden_loss: %d sudden_rtt: %d\n", sudden_loss, sudden_rtt);
		fst_check(sudden_loss == 3);
		fst_check(sudden_rtt == 2);

		close(sockfd_rtp);
#ifdef USE_RTCP_PCAP
		close(sockfd_rtcp);
#endif

		pcap_close(pcap);

		if (write_frame) switch_frame_free(&write_frame);

		switch_channel_hangup(channel, SWITCH_CAUSE_NORMAL_CLEARING);

		switch_rtp_destroy(&rtp_session);

		switch_media_handle_destroy(session);

		switch_core_session_rwunlock(session);

	}

	FST_TEST_END()

	FST_TEST_BEGIN(test_estimator_cusum_for_video)
	{
		switch_core_session_t *session = NULL;
		switch_channel_t *channel = NULL;
		switch_status_t status;
		switch_call_cause_t cause;
		switch_codec_t read_codec = { 0 };
		switch_codec_t write_codec = { 0 };
		switch_codec_settings_t codec_settings = {{ 0 }};
		switch_frame_flag_t frameflags = { 0 };
		switch_io_flag_t io_flags = { 0 };
		switch_payload_t pt = { 0 };
		switch_stream_handle_t stream = { 0 };
		switch_frame_t *write_frame;
		pcap_t *pcap;
		const unsigned char *packet;
		char errbuf[PCAP_ERRBUF_SIZE];
		struct pcap_pkthdr header;
		struct sockaddr_in     servaddr_rtp; 
		struct sockaddr_in     servaddr_rtcp;
		int sockfd_rtp;
		int sockfd_rtcp;
		const struct sniff_ip *ip; /* The IP header */
		int size_ip, ret, jump_over;
		struct hostent *server;
		cusum_kalman_detector_t *det_loss = NULL;
		cusum_kalman_detector_t *det_rtt = NULL;
		kalman_estimator_t * est_loss = NULL;
		kalman_estimator_t * est_rtt = NULL;

		uint8_t readvals_loss[MAXVALS] = {5, 2, 1, 25, 50, 75, 85, 20, 27, 90};
		float readvals_rtt[MAXVALS] = {0.5, 0.6, 0.7, 0.65, 0.8, 0.75, 0.85, 0.4, 0.57, 0.65};

		char rtcp_sr_trigger[] = "\x81\xc8\x00\x0c\x78\x9d\xac\x45\xe2\x67\xa5\x74\x30\x60\x56\x81\x00\x19"
			"\xaa\x00\x00\x00\x06\xd7\x00\x01\x2c\x03\x5e\xbd\x2f\x0b\x00"
			"\x00\x00\x00\x00\x00\x57\xc4\x00\x00\x00\x39\xa5\x73\xfe\x90\x00\x00\x2c\x87"
			"\x81\xca\x00\x0c\x78\x9d\xac\x45\x01\x18\x73\x69\x70\x3a\x64\x72\x40\x31\x39\x32\x2e"
			"\x31\x36\x38\x2e\x30\x2e\x31\x33\x3a\x37\x30\x36\x30\x06\x0e\x4c\x69\x6e\x70\x68\x6f"
			"\x6e\x65\x2d\x33\x2e\x36\x2e\x31\x00\x00";
		switch_media_handle_t *media_handle;
		switch_core_media_params_t *mparams;
		uint32_t add_rtt;
		int count = 0, k = 0, sudden_loss = 0, sudden_rtt = 0;
                switch_jb_t *vb;
                char *r_sdp;
		uint8_t match = 0, p = 0;
		struct sockaddr_in sin;
		socklen_t len = sizeof(sin);

		rx_port = rx_port + 2;
		tx_port = tx_port + 2;

		status = switch_ivr_originate(NULL, &session, &cause, "null/+15553334444", 2, NULL, NULL, NULL, NULL, NULL, SOF_NONE, NULL, NULL);
		fst_requires(session);
		fst_check(status == SWITCH_STATUS_SUCCESS);

		channel = switch_core_session_get_channel(session);
		fst_requires(channel);

		switch_channel_set_flag_recursive(channel, CF_VIDEO_DECODED_READ);

		flags[SWITCH_RTP_FLAG_USE_TIMER] = 0;
		flags[SWITCH_RTP_FLAG_ADJ_BITRATE_CAP] = 1;
		flags[SWITCH_RTP_FLAG_ESTIMATORS] = 1;
		flags[SWITCH_RTP_FLAG_ENABLE_RTCP] = 1;
		flags[SWITCH_RTP_FLAG_NOBLOCK] = 0;
		flags[SWITCH_RTP_FLAG_VIDEO] = 1;
		flags[SWITCH_RTP_FLAG_DATAWAIT] = 1;
		flags[SWITCH_RTP_FLAG_RAW_WRITE] = 1;
		flags[SWITCH_RTP_FLAG_DEBUG_RTP_READ] = 1;
		rtp_session = switch_rtp_new(rx_host, rx_port, tx_host, tx_port, VIDEO_TEST_PT, 1, 90, flags, "soft", &err, switch_core_session_get_pool(session), 0, 0);
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "switch_rtp_new() returned: %s\n", err);
		fst_xcheck(rtp_session != NULL, "switch_rtp_new()");
		fst_requires(switch_rtp_ready(rtp_session));
		switch_rtp_activate_rtcp(rtp_session, 5000, tx_port + 1, 0);
		switch_rtp_set_default_payload(rtp_session, VIDEO_TEST_PT);
		switch_core_media_set_rtp_session(session, SWITCH_MEDIA_TYPE_VIDEO, rtp_session);
		channel = switch_core_session_get_channel(session);
		fst_requires(channel);
		session = switch_rtp_get_core_session(rtp_session);
		fst_requires(session);
		switch_rtp_set_ssrc(rtp_session, 0xabcd);
		switch_rtp_set_remote_ssrc(rtp_session, 0x789dac45);
		switch_rtp_use_estimators(rtp_session, SWITCH_TRUE);

		status = switch_core_codec_init(&read_codec,
		"VP8",
		NULL,
		NULL,
		0,
		0,
		1, SWITCH_CODEC_FLAG_ENCODE | SWITCH_CODEC_FLAG_DECODE,
		&codec_settings, switch_core_session_get_pool(session));
		fst_check(status == SWITCH_STATUS_SUCCESS);

		status = switch_core_codec_init(&write_codec,
		"VP8",
		NULL,
		NULL,
		0,
		0,
		1, SWITCH_CODEC_FLAG_ENCODE | SWITCH_CODEC_FLAG_DECODE,
		&codec_settings, switch_core_session_get_pool(session));
		fst_check(status == SWITCH_STATUS_SUCCESS);

		switch_core_session_set_read_codec(session, &read_codec);
		switch_core_session_set_write_codec(session, &write_codec);

		status = switch_rtp_set_video_buffer_size(rtp_session, 5, 10);
		fst_requires(status == SWITCH_STATUS_SUCCESS);
		vb = switch_rtp_get_jitter_buffer(rtp_session);
		fst_requires(vb);
		switch_jb_debug_level(vb, 10);

		mparams  = switch_core_session_alloc(session, sizeof(switch_core_media_params_t));
		mparams->num_codecs = 1;
		mparams->inbound_codec_string = switch_core_session_strdup(session, "vp8");
		mparams->outbound_codec_string = switch_core_session_strdup(session, "vp8");
		mparams->rtpip = switch_core_session_strdup(session, (char *)rx_host);

		status = switch_media_handle_create(&media_handle, session, mparams);
		fst_requires(status == SWITCH_STATUS_SUCCESS);

		switch_channel_set_variable(channel, "absolute_codec_string", "vp8");

		switch_channel_set_variable(channel, SWITCH_LOCAL_MEDIA_IP_VARIABLE, rx_host);
		switch_channel_set_variable_printf(channel, SWITCH_LOCAL_MEDIA_PORT_VARIABLE, "%d", rx_port);

		/* need to use SDP - core media - codec control  */
		r_sdp = switch_core_session_sprintf(session,
		"v=0\n"
		"o=FreeSWITCH 1234567890 1234567890 IN IP4 %s\n"
		"s=FreeSWITCH\n"
		"c=IN IP4 %s\n"
		"t=0 0\n"
		"m=video %u RTP/AVP %d\n"
		"a=ptime:20\n"
		"a=sendrecv\n"
		"a=rtpmap:%d VP8/90000\n",
		tx_host, tx_host, tx_port, VIDEO_TEST_PT, VIDEO_TEST_PT);
		 
		switch_core_media_prepare_codecs(session, SWITCH_FALSE);
		   
		match = switch_core_media_negotiate_sdp(session, r_sdp, &p, SDP_TYPE_REQUEST);
		fst_requires(match == 1);

		status = switch_core_media_choose_ports(session, SWITCH_TRUE, SWITCH_FALSE);
		fst_requires(status == SWITCH_STATUS_SUCCESS);

		switch_rtp_reset(rtp_session);

		pcap = pcap_open_offline("pcap/video-vp8-100pkts.pcap", errbuf);
		fst_requires(pcap);

		SWITCH_STANDARD_STREAM(stream);
		switch_api_execute("fsctl", "debug_level 4", session, &stream);
		switch_api_execute("opus_debug", "on", session, &stream);
		switch_safe_free(stream.data);

		switch_frame_alloc(&write_frame, SWITCH_RECOMMENDED_BUFFER_SIZE);
		write_frame->codec = &write_codec;

		if ( (sockfd_rtp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		}

		if ( (sockfd_rtcp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		} 

		memset(&servaddr_rtp, 0, sizeof(servaddr_rtp)); 
		                                    
		servaddr_rtp.sin_family = AF_INET; 
		servaddr_rtp.sin_port = htons(rx_port); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtp.sin_addr.s_addr, server->h_length);

		servaddr_rtcp.sin_family = AF_INET; 
		servaddr_rtcp.sin_port = htons(rx_port + 1); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtcp.sin_addr.s_addr, server->h_length);

		/*get local UDP port (tx side) to trick FS into accepting our packets*/
		ret = sendto(sockfd_rtp, NULL, 0, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
		if (ret < 0){
			perror("sendto");
			exit(1);
		}

		len = sizeof(sin);
		if (getsockname(sockfd_rtp, (struct sockaddr *)&sin, &len) == -1) {
			perror("getsockname");
			exit(1);
		} else {
			switch_rtp_set_remote_address(rtp_session, tx_host, ntohs(sin.sin_port), 0, SWITCH_FALSE, &err);
		}

		while ((packet = pcap_next(pcap, &header))) {
			/*assume only UDP/RTP packets in the pcap*/
			uint32_t datalen = header.caplen;
			size_t len;

			len = header.caplen;

			ip = (struct sniff_ip*)(packet + 14);
			size_ip = IP_HL(ip) * 4;

			jump_over = 14 /*SIZE_ETHERNET*/ + size_ip + 8 /*UDP HDR SIZE */;
			packet += jump_over;

			if (packet[0] == 0x80 && packet[1] == VIDEO_TEST_PT) {
				int16_t *seq =  (int16_t *)packet + 1;
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "Sent RTP from pcap. Seq = %d\n", htons(*seq));
				ret = sendto(sockfd_rtp, (const char *) packet, len - jump_over, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}
			} 
#ifdef USE_RTCP_PCAP
			else if (packet[0] == 0x81) {
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "Sent RTCP\n");
				ret = sendto(sockfd_rtcp, (const char *) packet, len - jump_over, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}
			}
#endif 

			status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
			fst_requires(status == SWITCH_STATUS_SUCCESS);
			if (pt == SWITCH_RTP_CNG_PAYLOAD /*timeout*/) continue;

			count++;

			if (count % 10) {
				if (k == MAXVALS - 1) k = 0;
				// estimators and detectors are initialized , feed them some (fake) data, as if we get more RTCP
				if (!est_loss) { // gets initialized with first RTP packet
					est_loss = (kalman_estimator_t *)switch_rtp_kalman_estimator_get_by_index(rtp_session, EST_LOSS);
				} else {
					switch_kalman_estimate(est_loss, readvals_loss[k], EST_LOSS);
				}
				if (!est_rtt) { // gets initialized with first RTP packet
					est_rtt = (kalman_estimator_t *)switch_rtp_kalman_estimator_get_by_index(rtp_session, EST_RTT);
					switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO,"est_rtt: %p\n", (void*)est_rtt);
				} else {
					switch_kalman_estimate(est_rtt, readvals_rtt[k], EST_RTT);
				}
			}

			if (!det_loss) { // gets initialized with first RTP packet
				det_loss = (cusum_kalman_detector_t *)switch_rtp_kalman_detector_get_by_index(rtp_session, EST_LOSS);
			} else {
				if (switch_kalman_cusum_detect_change(det_loss, readvals_loss[k], est_loss->val_estimate_last)) {
					sudden_loss++;
					switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Sudden change in the mean value of packet loss ! %u:%f \n", readvals_loss[k], est_loss->val_estimate_last);
				}
			}

			if (!det_rtt) { // gets initialized with first RTP packet
				det_rtt = (cusum_kalman_detector_t *)switch_rtp_kalman_detector_get_by_index(rtp_session, EST_RTT);
			} else {
				if (switch_kalman_cusum_detect_change(det_rtt, readvals_rtt[k], est_rtt->val_estimate_last)) {
					sudden_rtt++;
					switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Sudden change in the mean value of rtt ! %f:%f \n", readvals_rtt[k], est_rtt->val_estimate_last);
				}
			}

			if (count % 10) {
				k++;
			}

			if (est_loss) {
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "est_loss->val_estimate_last: [%f]\n", est_loss->val_estimate_last);
			}

			if (est_rtt) {
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "est_rtt->val_estimate_last: [%f]\n", est_rtt->val_estimate_last);
			}

			fst_requires(datalen <= SWITCH_RECOMMENDED_BUFFER_SIZE);
			write_frame->datalen = datalen;
			memcpy(write_frame->data, packet, datalen);

			// decode what we have in the PCAP
			status = switch_core_session_write_frame(session, write_frame, frameflags, 0);
			fst_requires(status == SWITCH_STATUS_SUCCESS);

			switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "pkt count = %d\n", count);

			if (count == 35) {
				switch_rtp_stats_t *s;
                                const char *current_state;

				/* go to "mild_loss" state*/
				add_rtt = 100;
				fst_requires(est_rtt);
				test_prepare_rtcp(&rtcp_sr_trigger, est_rtt->val_estimate_last, add_rtt, 0x05);

				ret = sendto(sockfd_rtcp, (const char *) rtcp_sr_trigger, sizeof(rtcp_sr_trigger), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}

				status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
				fst_requires(status == SWITCH_STATUS_SUCCESS);

				s = switch_rtp_get_stats(rtp_session, switch_core_session_get_pool(session));
				current_state = switch_bandwidth_estimation_name(s->estimation_state); 
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Est State: [%s]\n", current_state);
				fst_requires(!strcasecmp("mild_loss", current_state));
			}

			if (count == 40) {
				switch_rtp_stats_t *s;
				const char *current_state;

				/* go to "slow_link" state*/
				add_rtt = 1200;
				fst_requires(est_rtt);
				test_prepare_rtcp(&rtcp_sr_trigger, est_rtt->val_estimate_last, add_rtt, 0xa0);

				ret = sendto(sockfd_rtcp, (const char *) rtcp_sr_trigger, sizeof(rtcp_sr_trigger), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}

				status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
				fst_requires(status == SWITCH_STATUS_SUCCESS);
				s = switch_rtp_get_stats(rtp_session, switch_core_session_get_pool(session));
				current_state = switch_bandwidth_estimation_name(s->estimation_state); 
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Est State: [%s]\n", current_state);
				fst_requires(!strcasecmp("slow_link", current_state));
			}

			if (count == 45) {
				switch_rtp_stats_t *s;
				const char *current_state;

				/* go to "mild_loss" state*/
				add_rtt = 100;
				fst_requires(est_rtt);
				test_prepare_rtcp(&rtcp_sr_trigger, est_rtt->val_estimate_last, add_rtt, 0x00);

				ret = sendto(sockfd_rtcp, (const char *) rtcp_sr_trigger, sizeof(rtcp_sr_trigger), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}

				status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
				fst_requires(status == SWITCH_STATUS_SUCCESS);
				s = switch_rtp_get_stats(rtp_session, switch_core_session_get_pool(session));
				current_state = switch_bandwidth_estimation_name(s->estimation_state); 
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Est State: [%s]\n", current_state);
				fst_requires(!strcasecmp("mild_loss", current_state));
			}

			if (count == 50) {
				switch_rtp_stats_t *s;
				const char *current_state;

				/* go to "normal" state*/
				add_rtt = 100;
				fst_requires(est_rtt);
				test_prepare_rtcp(&rtcp_sr_trigger, est_rtt->val_estimate_last, add_rtt, 0x05);

				ret = sendto(sockfd_rtcp, (const char *) rtcp_sr_trigger, sizeof(rtcp_sr_trigger), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}

				status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
				fst_requires(status == SWITCH_STATUS_SUCCESS);

				ret = sendto(sockfd_rtcp, (const char *) rtcp_sr_trigger, sizeof(rtcp_sr_trigger), MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtcp, sizeof(servaddr_rtcp)); 
				if (ret < 0){
					perror("sendto");
					exit(1);
				}

				status = switch_rtp_read(rtp_session, (void *)packet, &datalen, &pt, &frameflags, io_flags);
				fst_requires(status == SWITCH_STATUS_SUCCESS);

				s = switch_rtp_get_stats(rtp_session, switch_core_session_get_pool(session));
				current_state = switch_bandwidth_estimation_name(s->estimation_state); 
				switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "Est State: [%s]\n", current_state);
				fst_requires(!strcasecmp("normal", current_state));
			}

		}

		fst_check(sudden_loss == 3);
		fst_check(sudden_rtt == 2);
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_DEBUG, "sudden_rtt: %d sudden_loss: %d\n", sudden_rtt, sudden_loss);

		close(sockfd_rtp);
#ifdef USE_RTCP_PCAP
		close(sockfd_rtcp);
#endif
		pcap_close(pcap);

		if (write_frame) switch_frame_free(&write_frame);

		switch_channel_hangup(channel, SWITCH_CAUSE_NORMAL_CLEARING);

		switch_rtp_destroy(&rtp_session);

		switch_media_handle_destroy(session);

		switch_core_session_rwunlock(session);
	}
	FST_TEST_END()

	FST_TEST_BEGIN(test_ulpfec_tx)
	{
		switch_core_session_t *session = NULL;
		switch_channel_t *channel = NULL;
		switch_status_t status;
		switch_call_cause_t cause;
		switch_codec_t read_codec = { 0 };
		switch_codec_t write_codec = { 0 };
		switch_codec_settings_t codec_settings = {{ 0 }};
		switch_stream_handle_t stream = { 0 };
		switch_frame_t *write_frame = NULL;
		pcap_t *pcap;
		const unsigned char *packet;
		char errbuf[PCAP_ERRBUF_SIZE];
		struct pcap_pkthdr header;
		struct sockaddr_in     servaddr_rtp; 
		struct sockaddr_in     servaddr_rtcp;
		int sockfd_rtp;
		int sockfd_rtcp;
		const struct sniff_ip *ip; /* The IP header */
		int size_ip, ret, jump_over;
		struct hostent *server;

		switch_media_handle_t *media_handle;
		switch_core_media_params_t *mparams;
                switch_jb_t *vb;
		char *r_sdp;
		uint8_t match = 0, p = 0;
		struct sockaddr_in sin;
		socklen_t len = sizeof(sin);

		rx_port = rx_port + 2;
		tx_port = tx_port + 2;

		status = switch_ivr_originate(NULL, &session, &cause, "null/+15553334444", 2, NULL, NULL, NULL, NULL, NULL, SOF_NONE, NULL, NULL);
		fst_requires(session);
		fst_check(status == SWITCH_STATUS_SUCCESS);

		channel = switch_core_session_get_channel(session);
		fst_requires(channel);

		switch_channel_set_flag_recursive(channel, CF_VIDEO_DECODED_READ);
	
		flags[SWITCH_RTP_FLAG_USE_TIMER] = 0;
		flags[SWITCH_RTP_FLAG_ADJ_BITRATE_CAP] = 1;
		flags[SWITCH_RTP_FLAG_ESTIMATORS] = 1;
		flags[SWITCH_RTP_FLAG_ENABLE_RTCP] = 1;
		flags[SWITCH_RTP_FLAG_NOBLOCK] = 0;
		flags[SWITCH_RTP_FLAG_VIDEO] = 1;
		flags[SWITCH_RTP_FLAG_DATAWAIT] = 1;
		flags[SWITCH_RTP_FLAG_RAW_WRITE] = 1;
		flags[SWITCH_RTP_FLAG_DEBUG_RTP_READ] = 1;
		rtp_session = switch_rtp_new(rx_host, rx_port, tx_host, tx_port, VIDEO_TEST_PT, 1, 90, flags, "soft", &err, switch_core_session_get_pool(session), 0, 0);
		switch_log_printf(SWITCH_CHANNEL_SESSION_LOG(session), SWITCH_LOG_INFO, "switch_rtp_new() returned: %s\n", err);
		fst_xcheck(rtp_session != NULL, "switch_rtp_new()");
		fst_requires(switch_rtp_ready(rtp_session));
		switch_rtp_activate_rtcp(rtp_session, 5000, tx_port + 1, 0);
		switch_rtp_set_default_payload(rtp_session, VIDEO_TEST_PT);
		switch_core_media_set_rtp_session(session, SWITCH_MEDIA_TYPE_VIDEO, rtp_session);
		channel = switch_core_session_get_channel(session);
		fst_requires(channel);
		session = switch_rtp_get_core_session(rtp_session);
		fst_requires(session);
		switch_rtp_set_ssrc(rtp_session, 0xabcd);
		switch_rtp_set_remote_ssrc(rtp_session, 0x789dac45);
		switch_rtp_activate_red_ulpfec(rtp_session);
		switch_rtp_set_fec_enforce(rtp_session, SWITCH_TRUE);

		status = switch_core_codec_init(&read_codec,
		"VP8",
		NULL,
		NULL,
		0,
		0,
		1, SWITCH_CODEC_FLAG_ENCODE | SWITCH_CODEC_FLAG_DECODE,
		&codec_settings, switch_core_session_get_pool(session));
		fst_check(status == SWITCH_STATUS_SUCCESS);

		status = switch_core_codec_init(&write_codec,
		"VP8",
		NULL,
		NULL,
		0,
		0,
		1, SWITCH_CODEC_FLAG_ENCODE | SWITCH_CODEC_FLAG_DECODE,
		&codec_settings, switch_core_session_get_pool(session));
		fst_check(status == SWITCH_STATUS_SUCCESS);

		switch_core_session_set_read_codec(session, &read_codec);
		switch_core_session_set_write_codec(session, &write_codec);

		status = switch_rtp_set_video_buffer_size(rtp_session, 5, 10);
		fst_requires(status == SWITCH_STATUS_SUCCESS);
		vb = switch_rtp_get_jitter_buffer(rtp_session);
		fst_requires(vb);
		switch_jb_debug_level(vb, 10);

		mparams  = switch_core_session_alloc(session, sizeof(switch_core_media_params_t));
		mparams->num_codecs = 3;
		mparams->inbound_codec_string = switch_core_session_strdup(session, "vp8,red,ulpfec");
		mparams->outbound_codec_string = switch_core_session_strdup(session, "vp8,red,ulpfec");

		mparams->rtpip = switch_core_session_strdup(session, (char *)rx_host);

		status = switch_media_handle_create(&media_handle, session, mparams);
		fst_requires(status == SWITCH_STATUS_SUCCESS);

		switch_channel_set_variable(channel, "absolute_codec_string", "vp8,red,ulpfec");

		switch_channel_set_variable(channel, SWITCH_LOCAL_MEDIA_IP_VARIABLE, rx_host);
		switch_channel_set_variable_printf(channel, SWITCH_LOCAL_MEDIA_PORT_VARIABLE, "%d", rx_port);

		r_sdp = switch_core_session_sprintf(session,
		"v=0\n"
		"o=FreeSWITCH 1234567890 1234567890 IN IP4 %s\n"
		"s=FreeSWITCH\n"
		"c=IN IP4 %s\n"
		"t=0 0\n"
		"m=video %u RTP/AVP %d 103 104\n"
		"a=ptime:20\n"
		"a=sendrecv\n"
		"a=rtpmap:%d VP8/90000\n"
		"a=rtpmap:103 red/90000\n"
		"a=rtpmap:104 ulpfec/90000\n",
		tx_host, tx_host, tx_port, VIDEO_TEST_PT, VIDEO_TEST_PT);
		 
		switch_core_media_prepare_codecs(session, SWITCH_FALSE);
		   
		match = switch_core_media_negotiate_sdp(session, r_sdp, &p, SDP_TYPE_REQUEST);
		fst_requires(match == 1);

		status = switch_core_media_choose_ports(session, SWITCH_TRUE, SWITCH_FALSE);
		fst_requires(status == SWITCH_STATUS_SUCCESS);

		switch_rtp_reset(rtp_session);

		pcap = pcap_open_offline("pcap/video-vp8-100pkts.pcap", errbuf);
		fst_requires(pcap);

		SWITCH_STANDARD_STREAM(stream);
		switch_api_execute("fsctl", "debug_level 4", session, &stream);
		switch_safe_free(stream.data);

		switch_frame_alloc(&write_frame, SWITCH_RECOMMENDED_BUFFER_SIZE);
		write_frame->codec = &write_codec;
		switch_set_flag(write_frame, SFF_RAW_RTP_PARSE_FRAME);

		if ( (sockfd_rtp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		}

		if ( (sockfd_rtcp = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
			perror("socket creation failed"); 
			exit(1); 
		} 

		memset(&servaddr_rtp, 0, sizeof(servaddr_rtp)); 
		                                    
		servaddr_rtp.sin_family = AF_INET; 
		servaddr_rtp.sin_port = htons(rx_port); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtp.sin_addr.s_addr, server->h_length);

		servaddr_rtcp.sin_family = AF_INET; 
		servaddr_rtcp.sin_port = htons(rx_port + 1); 
		server = gethostbyname(rx_host);
		bcopy((char *)server->h_addr, (char *)&servaddr_rtcp.sin_addr.s_addr, server->h_length);

		/*get local UDP port (tx side) to trick FS into accepting our packets*/
		ret = sendto(sockfd_rtp, NULL, 0, MSG_CONFIRM, (const struct sockaddr *) &servaddr_rtp, sizeof(servaddr_rtp)); 
		if (ret < 0){
			perror("sendto");
			exit(1);
		}

		len = sizeof(sin);
		if (getsockname(sockfd_rtp, (struct sockaddr *)&sin, &len) == -1) {
			perror("getsockname");
			exit(1);
		} else {
			switch_rtp_set_remote_address(rtp_session, tx_host, ntohs(sin.sin_port), 0, SWITCH_FALSE, &err);
		}

		while ((packet = pcap_next(pcap, &header))) {
			uint8_t byte;
			int m;
			/*assume only UDP/RTP packets in the pcap*/
			uint32_t datalen = header.caplen;

			ip = (struct sniff_ip*)(packet + 14);
			size_ip = IP_HL(ip) * 4;

			jump_over = 14 /*SIZE_ETHERNET*/ + size_ip + 8 /*UDP HDR SIZE */;
			packet += jump_over;

			/* read packets from the pcap file - they will be sent back to the test socket together with the FEC TX packets
			 * which were created from the video packets in the pcap.*/
			byte = packet[1];
			m = (1 << 7) & byte;
			if (packet[0] == 0x80) {
				int w;

				datalen = datalen - jump_over;

				fst_requires(datalen <= SWITCH_RECOMMENDED_BUFFER_SIZE);
				write_frame->datalen = datalen;
				memcpy(write_frame->data, packet, datalen);
				write_frame->packetlen = datalen;
				write_frame->packet = write_frame->data;

				if (m) {
					write_frame->m = 1;
				} else {
					write_frame->m = 0;
				}

				w = switch_rtp_write_frame(rtp_session, write_frame);
				fst_requires(w == datalen + 1 /*RED*/);
			} 
		}

		/* will produce 18 FEC packets from the 100 packets in the pcap file (containing various video frame sizes) */
		fst_requires(switch_rtp_get_redundancy_fec_count(rtp_session) == 18);

		close(sockfd_rtp);
#ifdef USE_RTCP_PCAP
		close(sockfd_rtcp);
#endif
		pcap_close(pcap);

		if (write_frame) switch_frame_free(&write_frame);

		switch_channel_hangup(channel, SWITCH_CAUSE_NORMAL_CLEARING);

		switch_rtp_destroy(&rtp_session);

		switch_media_handle_destroy(session);

		switch_core_session_rwunlock(session);
	}
	FST_TEST_END()
}
FST_SUITE_END()
}
FST_CORE_END()

