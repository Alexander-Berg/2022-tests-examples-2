#!/usr/bin/perl

#TESTME: t-http.t

#
use common::sense;
use strict;
use warnings;
use Time::HiRes qw( usleep );
use lib::abs;
#micresec sleep
my $yabs = q{<?xml version="1.0" encoding="windows-1251"?>
<banners linkhead="http://yabs.yandex.ru/count/7tn-9TIj82e40X00Zhj9UmW5KP6yq4ba1fE53Qxw6ZhvbxFAp0Hw0m00"><teaser><banner linknext="=K_skO9K2cmPfMcbQagtDzwQAet7tJgMM66IcD92W7mBUVGC0"><url>http://yabs.yandex.ru/count/7tn-9TSyouK40X00Zhj9UmW5KPK2cmPfMeYw-0TG0vAjpVUcfZIAet7tJge1fPOOP92W7mBUaRpGIMG6auKDGgxw6ZhvbxFAp0H-1m00</url>
<img width="120" height="90">http://yabs.yandex.ru/count/7tn-9OQU-Uu40X02Zhj9UmW5KPK2cmPfMeYw-0TG0vAjpVUcfZIAet7tJge2fPOOP92W7mBUaRpGIMG6auKDGQxw6ZhvbxFAp0H-1m00</img>
<title>ßíäåêñ.Íàâèãàòîð&amp;nbsp;&amp;mdash;</title>
<text>ãîâîðèò è ïîêàçûâàåò</text>
<alt>ßíäåêñ.Íàâèãàòîð</alt></banner></teaser><authblock><banner linknext="=WixEEvK6cm5fSsbpagLj11AAeh9s3AMHOyMcGP2W7mBUVGC0">
<img>http://yabs.yandex.ru/count/7tn-9H1GDC040X02Zhj9UmW5KPK6cm5fSuYxVmmW19AbRGGIfa6Aeh9s3Ae1fP5ZnP2W7mBUaRpGIMG6auKDGQxw6ZhvbxFAp0H-1m00</img>
<text> Çàïîëíèòå àíêåòó íà Ìîåì Êðóãå</text>
<url>http://yabs.yandex.ru/count/7tn-9K7o1gi40X00Zhj9UmW5KPK6cm5fSuYxVmmW19AbRGGIfa6Aeh9s3Ae2fP5ZnP2W7mBUaRpGIMG6auKDGgxw6ZhvbxFAp0H-1m00</url>
<wid></wid>
</banner></authblock><options><banner linknext="=Q_PWvfK7cm5kPMvbagOk2nsAhT8D4wK5fXQGe1y2tdi3"><livejournal>
<close_url>http://yabs.yandex.ru/count/814/385889197</close_url>
</livejournal></banner><banner linknext="=dBi5oPK7cm5kPMvbCfAZfKUFYgy_HZUb1QOMaA0V0jvy0m00"><money_promo>
<close_url>http://yabs.yandex.ru/count/814/386238519</close_url>
</money_promo></banner><banner linknext="=35l8pPK7cm5kPMvbCvAb62EIYg-V8Jgb1QOMaA0V0jvy0m00"><sickmailregion>
<close_url>http://yabs.yandex.ru/count/814/386248138</close_url>
</sickmailregion></banner><banner linknext="=eadhdPK7cm5kPMvbD9Ad6GiTYgtC3HEb1QOMaA0V0jvy0m00"><twitter>
<close_url>http://yabs.yandex.ru/count/814/385889194</close_url>
</twitter></banner><banner linknext="=zzqyJPK7cm5kPMvbDPAcAmiTYg3F3HEb1QOMaA0V0jvy0m00"><vkontakte>
<close_url>http://yabs.yandex.ru/count/814/385889196</close_url>
</vkontakte></banner><banner linknext="=sFbNLfK7cm5kPMvbDfAf6WiTYgFD3HEb1QOMaA0V0jvy0m00"><facebook>
<close_url>http://yabs.yandex.ru/count/814/385889195</close_url>
</facebook></banner></options><stripexml><banner linknext="=C3WKcPK8cm5jT6rqag_uiwMAhAApJQMYzBm1fZYGe1y2ta5_0m00"><alias>fx_orange_pointer </alias>
<text>Âèçóàëüíûå çàêëàäêè äëÿ Firefox: îäèí êëèê äî ëþáèìûõ ñàéòîâ</text>
<set_url>http://yabs.yandex.ru/count/7tn-9NILJ3i40X00Zhj9UmW5KPK8cm5jT8Y__KkG0vAl-BEbfZYAhAApJQe3fQBql06Ge1y2tf6yq4ba1fE53KAk-Xew-PUpoim4VmS0</set_url>
<set_cntr> testpolosok</set_cntr>
<set_title>Óñòàíîâèòü</set_title>
<close_url>http://yabs.yandex.ru/count/0/0</close_url>
<close_cntr>c0('stred/pid=132/cid=70372/path=bar.fx_green')</close_cntr>
<close_title>Çàêðûòü</close_title>
<stripe_url>http://yabs.yandex.ru/count/7tn-9RgaPvK40X00Zhj9UmW5KPK8cm5jT8Y__KkG0vAl-BEbfZYAhAApJQe8fQBql06Ge1y2tf6yq4ba1fE53KAk-Xew-PUpoim4VmS0</stripe_url>
<stripe_cntr>testpolosok1</stripe_cntr>
<close_counter>http://yabs.yandex.ru/count/7tn-9R7wG9O40X00Zhj9UmW5KPK8cm5jT8Y__KkG0vAl-BEbfZYAhAApJQeAfQBql06Ge1y2tf6yq4ba1fE53KAk-Xew-PUpoim4VmS0</close_counter>
<agreement_text></agreement_text>
<agreement_button></agreement_button>
<agreement_url></agreement_url></banner></stripexml><info>
<category></category>
<domains>1633480192,242914050,479519744,953795840</domains>
<social></social>
<gender>0,1</gender>
<age>0,1,2,3,4</age>
</info>
</banners>};

my $awaps = q{<?xml version="1.0" encoding="utf-8"?>
<banners> 
<media>
<ad>
<content_type>text/html</content_type>
<content>
<![CDATA[
<script type="text/javascript" charset="utf-8">//<!--
(new Image()).src = "http://awaps.yandex.ru/99/c1/tgFtaeLDK0ya43AvjS329vkQxTGb-gEgoXDdPkzyp8eI+1ckkEz9GWxCMp0mx_tsaP2-OlVQoJqD7QMMAHB11py2j6vEB9zICbS6TYDuSal0D8+mA2O1IYaITSM_tIBNdDTVnwEc8EvmxYxHNpqWDuzTlC5s0Gyu5ZOXGVxBegMtT7Px+EiZOIYck_tg3uyK1o8pbPGfgxN-nVR8hOxaBEcAfmCtt7e9MJF79qtbu8HUS+6yRBJ18DF_kTVy3ahpoNrScAw3G5ODxAFSrBhmrt4L-KASpqA0GYLA4rGXF_A_.gif";//--></script>
<noscript>
<img src="http://awaps.yandex.ru/99/c1/tgFtaeLDK0ya43AvjS329vkQxTGb-gEgoXDdPkzyp8eI+1ckkEz9GWxCMp0mx_tsaP2-OlVQoJqD7QMMAHB11py2j6vEB9zICbS6TYDuSal0D8+mA2O1IYaITSM_tIBNdDTVnwEc8EvmxYxHNpqWDuzTlC5s0Gyu5ZOXGVxBegMtT7Px+EiZOIYck_tg3uyK1o8pbPGfgxN-nVR8hOxaBEcAfmCtt7e9MJF79qtbu8HUS+6yRBJ18DF_kTVy3ahpoNrScAw3G5ODxAFSrBhmrt4L-KASpqA0GYLA4rGXF_A_.gif"  width="1" height="1" border="0" />
</noscript>
]]>
</content>
<ad_type>stat_pixel</ad_type>
<width>0</width>
<height>0</height>
</ad>
</media>
</banners>};

use Plack::Request;

my $app = sub {
    my $env = shift;
    my $msleep = 0;
    my $uri = $env->{REQUEST_URI};

    if( $uri =~ m/(\d+)/ ){
        $msleep = $1;
    }

    if( $msleep > 1000 ){
        $msleep = 1000;
    }
    usleep( $msleep * 1000 );
    my $response = 'ok msleep ' . $msleep;
    if( $uri =~ /awaps/ ){
        $response = $awaps;
    } elsif( $uri =~/yabs/ ){
        $response = $yabs;
    } elsif( $uri =~/post/ ){
        my $req = Plack::Request->new($env);
        if( $req->method() ~~ ["POST", "PUT"  ] ){
            #$response = $req->method() . $req->raw_body();
            
            $response = $req->raw_body();
            print STDERR $req->raw_body();
        } else {
            $response = "nonPOST";
        }
    } elsif( $uri =~/header\/(\w+)/){
        my $mod = uc($1);
        $mod =~s/-/_/g;
        $response= $env->{"HTTP_" . $mod} ;
    } elsif( $uri =~/retry\/(\d+)/ ){
        $response ="Retry: ". ($env->{HTTP_X_YANDEX_RETRY} // 'none');
        if( ($env->{HTTP_X_YANDEX_RETRY} || '') eq $1 ){
        } else {
            usleep( 100 * 1000 );
        } 
    } elsif( $uri =~/\/50(\d)\/status/){
        return [ "50$1 booboo" ,
            [ 'Content-Type' => 'text/html'],
            [ 'server made a boo boo 50' . $1 ],
        ];
    }

    
    #open(OUT, '>>', lib::abs::path( "./timeout.log" ) );
    #print OUT $response . "\n\n";
    #close OUT;
 
    return [ 
        '200', 
        [ 'Content-Type' => 'text/plain' ], 
        [ $response, ],
    ];

}
