package Handler::TestHelper;
use rules;
use MP::Stopdebug;

use base qw(HandlerBase);

use TestHelper;

sub register {
   {
     "interface" => {
       "bigmorda" => {
         "uri_start" => '/test'
       },
       "embedded" => {
         "urix" => [
           qr/^\/test\/.*$/ui
         ]
       },
       "mobmorda" => {
         "urix" => [
           qr/^\/test\//ui
         ]
       },
       "yandexcom" => {
         "urix" => [
           qr/^\/test\/.*$/ui
         ]
       },
       "yaru" => {
         "urix" => [
           qr/^\/test\/.*$/ui
         ]
       }
     }
   }
}

sub handler {
    return &TestHelper::handler;
}

1;
