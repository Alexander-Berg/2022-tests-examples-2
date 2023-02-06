package Test::Smoo::Event;
use parent 'Test::Class';

use Test::Most;
use MP::Logit qw(logit dmp);
use rules;

use Smoo::Event;
use Storable qw/dclone/;
use MP::Utils;
use utf8;

my $dbh;

sub start : Test(startup) {
    $dbh = Smoo::DB::instance();
    $dbh->begin_work();
    _init_db();
}

sub _init_db {
    my $res = $dbh->do('DELETE FROM settings');

    $res = $dbh->do('INSERT INTO settings 
            (id, name, service, event_type, localize, ttl, ttv, ttp, push_approved, push_enabled, enabled )
            VALUES ("100", "test_delayed", "test", "delayed", \'{"default": {"title": "Яндекс"}}\', "10:00:00", "03:00:00", "01:00:00", 0, 1, 1)',
    );
    $res = $dbh->do('INSERT INTO settings_geos
            (settings_id, value)
            VALUES ("100", 213)', undef);
    $res = $dbh->do('INSERT INTO settings_timelines
            (settings_id, time_from, time_to)
            VALUES ("100", "09:00:00", "23:00:00")', undef);

    $res = $dbh->do("INSERT INTO settings_targetings
           SET settings_id=100, platform='appsearch_android', receivers='app_version == 3.1',
           topic_card = 'newtopic_card', topic_push = 'newtopic_push', exp='EXP-1', enabled=1",
           undef);

    $res = $dbh->do('INSERT INTO settings 
            (id, name, service, event_type, ttl, ttv, ttp, push_approved, push_enabled, enabled )
            VALUES ("101", "test2", "test", "delayed", "00:10:00", "00:20:00", "00:30:00", 1, 1, 0)',
    );

    $res = $dbh->do('INSERT INTO settings 
            (id, name, service, event_type, localize, ttl, ttv, ttp, push_approved, push_enabled, enabled )
            VALUES ("102", "test_realtime", "test_realtime", "realtime", \'{"default": {"title": "Яндекс"}}\',
            "12:00:00", "02:00:00", "00:30:00", 1, 1, 1)',
    );
    $res = $dbh->do('INSERT INTO settings_geos
            (settings_id, value)
            VALUES ("102", 213)', undef);
    $res = $dbh->do('INSERT INTO settings_timelines
            (settings_id, time_from, time_to)
            VALUES ("102", "09:00:00", "23:00:00")', undef);
}

sub end : Test(shutdown) {
    $dbh->rollback();
}

sub before : Test(setup) {
    my $res = $dbh->do('DELETE FROM master_events', undef);
    $res = $dbh->do('UPDATE settings SET push_approved=0 WHERE id=100');
}

my $REALTIME_EVENT = {
    name   => 'test_realtime',
    geo    => 213,
    locale => 'ru',
    msg    => 'Резкий рост курса доллара',
    url    => 'yandex.ru',
};

sub v1_add_realtime_check_event : Tests {
    my $res   = Smoo::Event::add(dclone $REALTIME_EVENT);
    my $me_id = $res->{res}->{master_event_id};
    my $got   = Smoo::DB::list_master_events({ id => $me_id })->{res}->[0];
    ok $got->{id} == $me_id;

    ok check_delta($got->{ctime}, $got->{expire_time}, '12:00:00');

    delete @{$got}{qw/ctime expire_time/};
    my $expected = {
        'data' => {
            'localization' => {
                'ru' => {
                    'push' => {
                        'msg'   => 'Резкий рост курса доллара',
                        'title' => 'Яндекс',
                        'url'   => 'yandex.ru'
                      }
                  }
              }
        },
        'event_type'    => 'realtime',
        'geo'           => 213,
        'hashed_key'    => 'b4bb821d2f7ce961f78ebc57962f7c35',
        'sup_content_id' => undef,
        'id'            => $me_id,
        'img'           => undef,
        'locale'        => 'all',
        'msg'           => undef,
        'name'          => 'test_realtime',
        'push_approved' => 1,
        'title'         => 'Яндекс',
        'url'           => undef
    };
    is_deeply $got, $expected or explain $got;
}

sub v1_add_realtime_check_push : Tests {
    my $res   = Smoo::Event::add(dclone $REALTIME_EVENT);
    my $me_id = $res->{res}->{master_event_id};

    my $push = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push == 1;
    $push = $push->[0];
    ok $push->{send_from} eq $push->{ctime};
    ok check_delta($push->{send_from}, $push->{send_to}, '00:30:00');

    delete @{$push}{qw/ctime send_from send_to id/};
    my $expected =
    {
        'geo'             => 213,
        'locale'          => 'all',
        'master_event_id' => $me_id,
        'name'            => 'test_realtime',
        'sent'            => 0,
        'ttl_sup'         => 7200,
        'type'            => 'push',
        'card_to'         => undef,
    };
    is_deeply $push, $expected or explain $push;
}

my $DELAYED_EVENT_V1 = {
    data => {
        localization => {
            ru => {
                push => {
                    msg     => "Переведите часы",
                    msg_ios => "Переведите часы в 00-00"
                },
            },
        },
    },
    geo         => 213,
    name        => "test_delayed",
    content_id  => 597265,
    expire_time => MP::Utils::format_epoch_for_db(time + 60 * 60 * 24),
    push_from   => MP::Utils::format_epoch_for_db(time + 60 * 60 * 1),
};

sub v1_add_delayed_check_event : Tests {
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V1);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $got = Smoo::DB::list_master_events({ id => $me_id })->{res}->[0];
    ok $got->{id} == $me_id;

    delete @{$got}{qw/ctime/};
    my $expected = {
        'data' => {
            'content_id'   => 597265,
            'localization' => {
                'ru' => {
                    'push' => {
                        'msg'     => 'Переведите часы',
                        'msg_ios' => 'Переведите часы в 00-00',
                        'title'   => 'Яндекс'
                      }
                  }
              }
        },
        'event_type'    => 'delayed',
        'expire_time'   => $DELAYED_EVENT_V1->{expire_time},
        'geo'           => 213,
        'hashed_key'    => '7d9da38aac254c2d356fcfff6fdb094a',
        'sup_content_id' => undef,
        'id'            => $me_id,
        'img'           => undef,
        'locale'        => 'all',
        'msg'           => undef,
        'name'          => 'test_delayed',
        'push_approved' => 0,
        'title'         => 'Яндекс',
        'url'           => undef
    };
    is_deeply $got, $expected or explain $got;
}

sub v1_add_delayed_check_push : Tests {
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V1);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $push = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push == 1;
    $push = $push->[0];
    ok check_delta($push->{send_from}, $push->{send_to}, '01:00:00') or explain $push;

    delete @{$push}{qw/ctime send_to id/};
    my $expected = {
        'geo'             => 213,
        'locale'          => 'all',
        'master_event_id' => $me_id,
        'name'            => 'test_delayed',
        'sent'            => 0,
        'ttl_sup'         => 7200,
        'type'            => 'push',
        'send_from'       => $DELAYED_EVENT_V1->{push_from},
        'card_to'         => undef,
    };
    is_deeply $push, $expected or explain $push;
}

my $DELAYED_EVENT_V2 = {
    name        => 'test_delayed',
    geo         => 213,
    content_id  => 597265,
    expire_time => MP::Utils::format_epoch_for_db(time + 60 * 60 * 48),
    data        => {
        localization => {
            ru => {
                push => {
                    msg     => "Переведите часы",
                    msg_ios => "Переведите часы в 00-00"
                },
            },
        },
    },
    push => {
        from    => MP::Utils::format_epoch_for_db(time + 60 * 60 * 2),
        ttl_sup => 60 * 30,
    },
    v => 2,
};

sub v2_add_delayed_full_check_event : Tests {
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $got = Smoo::DB::list_master_events({ id => $me_id })->{res}->[0];
    ok $got->{id} == $me_id;
    ok $got->{expire_time} gt $got->{ctime};
    is $got->{expire_time}, $DELAYED_EVENT_V2->{expire_time};

    delete @{$got}{qw/ctime expire_time/};
    my $expected = {
        'data' => {
            'content_id'   => 597265,
            'localization' => {
                'ru' => {
                    'push' => {
                        'msg'     => 'Переведите часы',
                        'msg_ios' => 'Переведите часы в 00-00',
                        'title'   => 'Яндекс'
                      }
                  }
              }
        },
        'event_type'    => 'delayed',
        'geo'           => 213,
        'hashed_key'    => '7d9da38aac254c2d356fcfff6fdb094a',
        'sup_content_id' => undef,
        'id'            => $me_id,
        'img'           => undef,
        'locale'        => 'all',
        'msg'           => undef,
        'name'          => 'test_delayed',
        'push_approved' => 0,
        'title'         => 'Яндекс',
        'url'           => undef
    };
    is_deeply $got, $expected or explain $got;
}

sub v2_add_delayed_full_check_push : Tests {
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $push = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push == 1;
    $push = $push->[0];
    ok check_delta($push->{send_from}, $push->{send_to}, '01:00:00') or explain $push;

    delete @{$push}{qw/ctime send_to id/};
    my $expected = {
        'geo'             => 213,
        'locale'          => 'all',
        'master_event_id' => $me_id,
        'name'            => 'test_delayed',
        'sent'            => 0,
        'ttl_sup'         => $DELAYED_EVENT_V2->{push}->{ttl_sup},
        'type'            => 'push',
        'send_from'       => $DELAYED_EVENT_V2->{push}->{from},
        'card_to'         => undef,
    };
    is_deeply $push, $expected or explain $push;
}

sub v2_add_delayed_full_check_event_sup_content_id : Tests {
    my $event = dclone $DELAYED_EVENT_V2;
    $event->{sup_content_id} = 'b58d5c3d937a6a2a2ebb7e156da5aa86e68d22dd';
    my $res = Smoo::Event::add($event);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $got = Smoo::DB::list_master_events({ id => $me_id })->{res}->[0];
    ok $got->{id} == $me_id;
    ok $got->{expire_time} gt $got->{ctime};
    is $got->{expire_time}, $DELAYED_EVENT_V2->{expire_time};

    delete @{$got}{qw/ctime expire_time/};
    my $expected = {
        'data' => {
            'content_id'   => 597265,
            'localization' => {
                'ru' => {
                    'push' => {
                        'msg'     => 'Переведите часы',
                        'msg_ios' => 'Переведите часы в 00-00',
                        'title'   => 'Яндекс'
                      }
                  }
              }
        },
        'event_type'    => 'delayed',
        'geo'           => 213,
        'hashed_key'    => '7d9da38aac254c2d356fcfff6fdb094a',
        'sup_content_id' => 'b58d5c3d937a6a2a2ebb7e156da5aa86e68d22dd',
        'id'            => $me_id,
        'img'           => undef,
        'locale'        => 'all',
        'msg'           => undef,
        'name'          => 'test_delayed',
        'push_approved' => 0,
        'title'         => 'Яндекс',
        'url'           => undef
    };
    is_deeply $got, $expected or explain $got;
}

sub v2_add_delayed_onlypush_check_event : Tests {
    my $event = dclone $DELAYED_EVENT_V2;

    my $res = Smoo::Event::add($event);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $got = Smoo::DB::list_master_events({ id => $me_id })->{res}->[0];
    ok $got->{id} == $me_id;
    ok $got->{expire_time} gt $got->{ctime};
    is $got->{expire_time}, $event->{expire_time};

    delete @{$got}{qw/ctime expire_time/};
    my $expected = {
        'data' => {
            'content_id'   => 597265,
            'localization' => {
                'ru' => {
                    'push' => {
                        'msg'     => 'Переведите часы',
                        'msg_ios' => 'Переведите часы в 00-00',
                        'title'   => 'Яндекс'
                      }
                  }
              }
        },
        'event_type'    => 'delayed',
        'geo'           => 213,
        'hashed_key'    => '7d9da38aac254c2d356fcfff6fdb094a',
        'sup_content_id' => undef,
        'id'            => $me_id,
        'img'           => undef,
        'locale'        => 'all',
        'msg'           => undef,
        'name'          => 'test_delayed',
        'push_approved' => 0,
        'title'         => 'Яндекс',
        'url'           => undef
    };
    is_deeply $got, $expected or explain $got;
}

sub v2_add_delayed_onlypush_check_push : Tests {
    my $event = dclone $DELAYED_EVENT_V2;

    my $res = Smoo::Event::add($event);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $push = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push == 1;
}

sub v2_add_delayed_nonapproved_retries_check_event: Tests {
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id1 = $res->{res}->{master_event_id};
    my $got1 = Smoo::DB::list_master_events({ id => $me_id1 })->{res}->[0];

    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id2 = $res->{res}->{master_event_id};
    my $got2 = Smoo::DB::list_master_events({ id => $me_id2 })->{res}->[0];
    is_deeply $got1, $got2;

    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id3 = $res->{res}->{master_event_id};
    my $got3 = Smoo::DB::list_master_events({ id => $me_id3 })->{res}->[0];
    is_deeply $got1, $got3;
}

sub v2_add_delayed_nonapproved_retries_check_push: Tests {
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $push1 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push1 == 1; $push1 = $push1->[0];

    # обновляем несколько раз, id пуша всегда должен меняться, потому что неподтвержденное событие
    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    my $push2 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push2 == 1; $push2 = $push2->[0];

    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    my $push3 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push3 == 1; $push3 = $push3->[0];

    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    my $push4 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push4 == 1; $push4 = $push4->[0];

    ok $push1->{id} < $push2->{id};
    ok $push2->{id} < $push3->{id};
    ok $push3->{id} < $push4->{id};

    delete $push1->{id};
    delete $push4->{id};
    is_deeply $push1, $push4;
}

sub v2_add_delayed_approved_retries_check_event: Tests {
    $dbh->do('UPDATE settings SET push_approved=1 WHERE id=100');

    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id1 = $res->{res}->{master_event_id};
    my $got1 = Smoo::DB::list_master_events({ id => $me_id1 })->{res}->[0];

    # обновление не работает в этом случае
    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    is $res->{error}, 'Approved and delayed event is not updatable';
}

sub v2_add_delayed_approved_retries_check_push: Tests {
    $dbh->do('UPDATE settings SET push_approved=1 WHERE id=100');
    my $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    ok $res->{ok} or explain $res;
    my $me_id = $res->{res}->{master_event_id};

    my $push1 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push1 == 1; $push1 = $push1->[0];

    # обновляем несколько раз, id пуша всегда должен меняться, потому что неподтвержденное событие
    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    my $push2 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push2 == 1; $push2 = $push2->[0];

    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    my $push3 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push3 == 1; $push3 = $push3->[0];

    $res = Smoo::Event::add(dclone $DELAYED_EVENT_V2);
    my $push4 = Smoo::DB::get_event_push_queue({ master_event_id => $me_id })->{res};
    ok scalar @$push4 == 1; $push4 = $push4->[0];

    ok $push1->{id} == $push2->{id};
    ok $push2->{id} == $push3->{id};
    ok $push3->{id} == $push4->{id};

    is_deeply $push1, $push4;
}

sub check_delta {
    my ($from, $to, $delta) = @_;
    my $_from = MP::Utils::add_time_delta(MP::Utils::datetime_from_string($from), $delta);
    return MP::Utils::format_date_for_db($_from) eq $to;
}
1;
