bless({
        '_POST_ARGS'         => {},
        '_VIRTUAL_INTERFACE' => 'bigmorda',
        '_POST'              => bless({
                'content_length' => -1,
                'tmpdir'         => '/tmp',
                'buffer'         => '',
                'state'          => 'buffering',
                'chunk_buffer'   => '',
                'body'           => undef,
                'content_type'   => undef,
                'length'         => 0,
                'chunked'        => 1,
                'upload'         => {},
                'param'          => {},
                'cleanup'        => 0
            },
            'HTTP::Body::OctetStream'
        ),
        '_COOKIES' => {
            'yabs-frequency' => bless({
                    'value' => ['/2/d_I00F858G00/'],
                    'name'  => 'yabs-frequency',
                    'path'  => '/'
                },
                'CGI::Cookie'
            ),
            'fuid01' => bless({
                    'value' => [
                        '49904c1601f79246.EKadXr9KpkMNTn_SYEvp-uoMLrJZnLfZdaP7uTbtHcaPWoN7bI-SjgTadzAVOKSCugdSQNn6mon9NInQbtbo773Qc54LTtOX7HCythy7D3jsW3IBUdai4DpzGNA-g4CY'
                    ],
                    'name' => 'fuid01',
                    'path' => '/'
                },
                'CGI::Cookie'
            ),
            'Virtual_id' => bless({
                    'value' => ['6'],
                    'name'  => 'Virtual_id',
                    'path'  => '/'
                },
                'CGI::Cookie'
            ),
            'yandex_login' => bless({
                    'value' => ['zhx'],
                    'name'  => 'yandex_login',
                    'path'  => '/'
                },
                'CGI::Cookie'
            ),
            'my' => bless({
                    'value' => ['YzIBAScCAAEA'],
                    'name'  => 'my',
                    'path'  => '/'
                },
                'CGI::Cookie'
            ),
            'yandexuid' => bless({
                    'value' => ['8494168701267528389'],
                    'name'  => 'yandexuid',
                    'path'  => '/'
                },
                'CGI::Cookie'
            ),
            'narod_login' => bless({
                    'value' => ['zhx'],
                    'name'  => 'narod_login',
                    'path'  => '/'
                },
                'CGI::Cookie'
            ),
            'Session_id' => bless({
                    'value' => [
                        '1267697986.-248.0.434095.34:27559652.8:1267697986249:3585399416:127.24731.5321.030150342adfc631a51c2dcc14e4ba41'
                    ],
                    'name' => 'Session_id',
                    'path' => '/'
                },
                'CGI::Cookie'
            ),
            'L' => bless({
                    'value' => [
                        'O0AEBFRWeFpQcXtiQgRhYHBkX3JifQV3UCl2S1ERbmZLK0EuHkEqJ0UGYHNCQAVdUF0dciQLFV8aBEA1AywnHg==.1267697986.1920.215151.cb568027ff65750dd807f3e440ff46f9'
                    ],
                    'name' => 'L',
                    'path' => '/'
                },
                'CGI::Cookie'
            ),
            't' => bless({
                    'value' => ['p'],
                    'name'  => 't',
                    'path'  => '/'
                },
                'CGI::Cookie'
              )
        },
        '_HEADERS' => bless({
                'user-agent' =>
                  'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.1.8) Gecko/20100202 Firefox/3.5.8 (.NET CLR 3.5.30729)',
                'connection'      => 'keep-alive',
                'keep-alive'      => '300',
                'accept'          => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept-language' => 'ru,en-us;q=0.7,en;q=0.3',
                'cookie' =>
                  'yandexuid=8494168701267528389; my=YzIBAScCAAEA; yabs-frequency=/2/d_I00F858G00/; L=O0AEBFRWeFpQcXtiQgRhYHBkX3JifQV3UCl2S1ERbmZLK0EuHkEqJ0UGYHNCQAVdUF0dciQLFV8aBEA1AywnHg==.1267697986.1920.215151.cb568027ff65750dd807f3e440ff46f9; yandex_login=zhx; t=p; Virtual_id=6; Session_id=1267697986.-248.0.434095.34:27559652.8:1267697986249:3585399416:127.24731.5321.030150342adfc631a51c2dcc14e4ba41; narod_login=zhx; fuid01=49904c1601f79246.EKadXr9KpkMNTn_SYEvp-uoMLrJZnLfZdaP7uTbtHcaPWoN7bI-SjgTadzAVOKSCugdSQNn6mon9NInQbtbo773Qc54LTtOX7HCythy7D3jsW3IBUdai4DpzGNA-g4CY',
                'accept-encoding' => 'gzip,deflate',
                'host'            => 'www-dev28.yandex.ru',
                'accept-charset'  => 'windows-1251,utf-8;q=0.7,*;q=0.7'
            },
            'HTTP::Headers'
        ),
        '_GET' => bless(do { \(my $o = '/') }, 'URI::http'),
        '_GET_ARGS'        => {},
        '_TYPE'            => undef,
        '_PATH'            => '/',
        '_X-Real-IP'       => '95.108.175.188',
        '_X-Forwarded-For' => ''
    },
    'MordaX::FcgiRequest'
);
