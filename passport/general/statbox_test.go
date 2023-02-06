package logs

import (
	"testing"

	"github.com/stretchr/testify/require"
)

var testSparse = []string{
	"Apache-\x00CXF/3.3.2",
	"Apache\\-HttpClient/4.5.12 (Java/1.8.0_221)",
	"Go-http\r\t-client/1.1",
	"Mozilla/5.0",
	"Mozil==la/5.0 (Linux; Android 10; YAL-L21 Build/HUAWEIYAL-L21; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 PassportSDK/7.23.15.723152213",
	"Mozilla/5.0 (Linux; Android 11; SM-A505FN Build/RP1A.200720.012; wv) Appl\"eWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36",
	"Mozilla/5.0 (Linux; Android 11; SM-A525F Build/RP1A.200720.012; wv) App^leWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36 PassportSDK/7.23.15.723152213",
	"Mozilla/5.0 (Linux; Android 12; sdk_gphone64_x86_64 \tBuild/S2B2.211203.006; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36 PassportSDK/7.23.15.723152213",
	"Mozilla/5.0 (Linux; Android 9; SM-G975F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/97.0.4692.98 Mobile Safari/537.36 PassportSDK/7.22.1.722012081",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.\t15; rv:96.0) Gecko/20100101 Firefox/96.0",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.41 YaBrowser/21.5.0.751 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 YaBrowser/21.6.0.1108 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.0.1488 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.1.0.2499 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) App\rleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.1.0.2500 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
	"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.1.0.2505 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebK\nit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.116 YaBrowser/22.1.1.1544 Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
	"Mozilla/5.0 (Windows NT 5.1; rv:7.0.1)\x00 Gecko/20100101 Firefox/7.0.1",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/5\\37.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.1.600 (beta) Yowser/2.5 Safari/537.36",
	"Mozilla/5.0 (X11; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0",
	"Mozilla/5.0 (iPad; CPU OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.6.0.194229",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 PassportSDK/6.6.0.194217",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.6.0.193412",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.6.1.190878",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.7.1.26",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.7.1.30",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.7.2.2533",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.7.2.491",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.6.0.193412",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.6.0.191768",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 PassportSDK/6.7.1.30",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
	"YandexTaxi/194217 CFNetwork/974.2.1 Darwin/18.0.0",
	"YandexTaxi/194297 CFNetwork/1237 Darwin/20.4.0",
	"driver-login/0.0.90 (testing) userver/1.0.0",
	"python-urllib3/1.26.8",
}

var testDense = []string{
	"M\to\rz\ni=l\"l\\a\t/\\5\".\\0\r \b(\ni\rP\"hon\te\t;\t C\tP\tU\t i\tP\th\tot\ne\t O\tS\t 1\t5t_\t3\t l\tik\te M\rar\rcr\r \x00OS\x00 X====)= =A=p=p=l=e=W=e=b=K=i=t=/=6=0=5=.\"1\".\"1\"5 (K\"HTML, like Gecko) Mobile/15E148 PassportSDK/6.6.0.193637",
}

func Test_Escape(t *testing.T) {
	require.Equal(t, "asdf", escape("asdf"))
	require.Equal(t, "asdf\\t", escape("asdf\t"))
	require.Equal(t, "asdf\\t\\n\\r\\=\\\"", escape("asdf\t\n\r=\""))
	require.Equal(
		t,
		"Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
		escape("Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"),
	)
	require.Equal(
		t,
		"M\\tozilla/5.\\=0 (iPhone; CPU iPhone OS 15_2_1 like Mac \\rOS X) AppleWeb\\nKit/605.1.15 \\\"(KHTML, like Gecko\\\\) Version/15.2 Mobile/15E148\\0 Safari/604.1",
		escape("M\tozilla/5.=0 (iPhone; CPU iPhone OS 15_2_1 like Mac \rOS X) AppleWeb\nKit/605.1.15 \"(KHTML, like Gecko\\) Version/15.2 Mobile/15E148\x00 Safari/604.1"),
	)
}

func Benchmark_EscapeSparse(b *testing.B) {
	for i := 0; i < b.N; i++ {
		escape(testSparse[i%len(testSparse)])
	}
}

func Benchmark_EscapeDense(b *testing.B) {
	for i := 0; i < b.N; i++ {
		escape(testDense[i%len(testDense)])
	}
}
