#!/usr/local/bin/perl

use common::sense;
use Test::More;
use lib::abs qw(.);

use common;

use MordaX::Logit qw(logit dumpit);

use_ok('WADM::Stats');
use_ok('WADM::StatsData');

subtest "Raw widget data" => sub {
    is( WADM::StatsData::get_raw_widget_data(), undef, 'undef on bad call' );
    is( WADM::StatsData::get_raw_widget_data( wid => 41090 ), undef, 'undef on bad call' );

    my $res = WADM::StatsData::get_raw_widget_data( wid => 41090, date => '2011-10-20' );
    ok( $res , 'some result');
    ok( $res->{all} , 'allregion presents');
    ok( $res->{ru} , 'allregion presents');
    ok( $res->{ua} , 'allregion presents');

    my $data = $res->{ru};
    for(qw/clicks_all clicks_title clicks_anchor users hits/){
        ok( $res->{ru}->{$_} , "Field: $_");
    }

    #dumpit( $res );
    my $date_pp = POSIX::strftime("%F", localtime( time + 60 * 60 * 24 ) );

    $res = WADM::StatsData::get_raw_widget_data( wid => 41090, date => $date_pp, region => 'ru' );
    ok( $res );
    #ok( $res->{ru}, "ru region present in something with no dates" );
    is( $res->{ru}, undef );
    is( $res->{all}, undef );
    is( $res->{ua} , undef );

    $res = WADM::StatsData::get_raw_widget_data( walias => '_mail', date => '2011-10-12', region => 'ru' );
    ok( $res );
    ok( $res->{ru}->{hits}, 'mail ru 2011-10-12');

 
    my $data_w = WADM::StatsData::get_raw_widget_data( wid => 41090, date => '2011-10-13', week => 1);

    #dumpit( $data_w );

    ok( $data_w , "weekly");
    ok( $data_w->{all} , 'all');
    ok( $data_w->{all}->{ret} , 'all ret');

    for(qw/hits users ret dt/){
        ok( $data_w->{ru}->{$_} , "get_raw_widget_data, RU, Field: $_");
    }

    done_testing();
};

subtest "date availability" => sub {

    my $date = '2011-10-14';
    #my $res = WADM::StatsData::get_raw_widget_data( walias => '_mail', date => '2011-10-01', region => 'ru' );
    #dumpit( $res );

    is( WADM::StatsData::is_date_hits_ok(   '2011-10-14' ), 1, ' hits on 2011-10-14 ');
    is( WADM::StatsData::is_date_clicks_ok( '2011-10-14' ), 1, 'clicks on 2011-10-14 ');
    #is( WADM::StatsData::is_date_clicks_ok( '2011-10-02' ), 0, 'bad clicks on 2011-10-02 ');
    #is( WADM::StatsData::is_date_clicks_ok( '2011-09-30' ), 0, 'bad clicks on 2011-09-30 ');

    done_testing();
};

subtest "widget week data for depricated date" => sub {
     
    my $data = WADM::StatsData::widget_week_data( wid => 41090, date => '2011-10-20', no_delta => 1 );
    ok( $data );
    ok( $data->{all} );
    ok( $data->{ru}  );
    ok( $data->{kz}  );
    
    ok( $data->{ru}->{hits}, "has hits" );
    
    ok( $data->{all}->{ret} , 'all ret');
    ok( $data->{ru}->{ret} , 'ru ret');

    done_testing();
};

subtest "widget week with delta data" => sub {
    my $data = WADM::StatsData::widget_week_data( wid => 41090, date => '2011-10-20', no_delta => 1 );
    is( $data->{ru}->{delta_users}, undef, 'no delta users, with no_delta');
    $data = WADM::StatsData::widget_week_data( wid => 41090, date => '2011-10-20');
    ok( $data->{ru}->{delta_users}, 'delta users, without no_delta');
    $data = WADM::StatsData::widget_week_data( wid => 41090, date => '2011-10-20', no_delta => 0 );
    ok( $data->{ru}->{delta_users}, 'delta users, without no_delta');

};


subtest "widget week date for yesterday " => sub  {
    my $date = POSIX::strftime("%F", localtime( time - 60 * 60 * 24 ) );
    ok($date, "DATE:". $date);

    my $data = WADM::StatsData::widget_week_data( wid => 41090, date => $date );
    ok( $data );
    ok( $data->{ru}->{hits}, "has hits" );
    ok( $data->{all}->{ret} , 'all ret');
    ok( $data->{ru}->{ret} , 'ru ret');

    for(qw/clicks_all clicks_title clicks_anchor users hits days ret  /){
        ok( $data->{ru}->{$_} , "Field: $_");
    }
};

subtest "widget dynamical data " => sub {
    my $date = POSIX::strftime("%F", localtime( time - 60 * 60 * 24 * 3 ) );
    ok ( $date , "Date: $date ");

    my $data = WADM::StatsData::widget_dyn_data( wid => 41090, date => $date );
    
    ok( $data->{ru}->{hits} ,'hits');
    ok( $data->{ru}->{delta_hits}   , 'delta hits');
    ok( $data->{ru}->{delta_users}  , 'delta users');

    dumpit($data);
    done_testing();
};
done_testing();
