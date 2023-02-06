INSERT INTO eats_robocall.calls(call_external_id, ivr_flow_id, personal_phone_id, context, status, scenario)
VALUES ('some_id', 'eats_flow', 'default_phone_id',
        '{"payload": {"abonent_name": "Sanya"}, "eater_id": "1337", "scenario_name": "scenario_1"}', 'waiting_for_call_creation',
        '{
            "start_call_actions": [
              {
                "action_body": {
                  "playback": {
                    "play": {
                      "id": "happy_music",
                      "path": "s3:/voices/happy_music.wav"
                    }
                  }
                }
              }
            ],
            "actions": [
              {
                "action_body": {
                  "originate": {
                    "phone_number": "+375445571982",
                    "timeout_sec": 15
                  }
                },
                "id": "originate_action",
                "next_action_id": "playback_action_speak"
              },
              {
                "action_body": {
                  "playback": {
                    "speak": {
                      "text": "Привет. Как дела, {user_name}?"
                    }
                  }
                },
                "id": "playback_action_speak",
                "next_action_id": "playback_action_play"
              },
              {
                "action_body": {
                  "ask": {
                    "action_after_answer": {
                      "-1": {
                        "alias": "-1 answer",
                        "next_action_id": "ask_action_dtmf"
                      },
                      "1": {
                        "alias": "1 answer",
                        "next_action_id": "ask_action_text"
                      },
                      "2": {
                        "alias": "2 answer",
                        "next_action_id": "ask_action_text"
                      },
                      "3": {
                        "alias": "3 answer",
                        "next_action_id": "ask_action_text"
                      }
                    },
                    "allowed_dtmf": "123",
                    "immediate_input": false,
                    "input_mode": "dtmf",
                    "no_input_timeout_ms": 15000,
                    "playback": {
                      "play": {
                        "id": "question1",
                        "path": "s3:/voices/question1.wav"
                      }
                    }
                  }
                },
                "id": "ask_action_dtmf",
                "next_action_id": ""
              },
              {
                "action_body": {
                  "ask": {
                    "action_after_answer": {
                      "default": {
                        "alias": "default answer",
                        "next_action_id": "ask_action_text"
                      },
                      "да": {
                        "alias": "да answer",
                        "next_action_id": "hangup_action"
                      },
                      "нет": {
                        "alias": "нет answer",
                        "next_action_id": "hold_action"
                      },
                      "я не знаю": {
                        "alias": "я не знаю answer",
                        "next_action_id": "wait_action"
                      }
                    },
                    "immediate_input": true,
                    "input_mode": "text",
                    "no_input_timeout_ms": 15000,
                    "playback": {
                      "play": {
                        "id": "question2",
                        "path": "s3:/voices/question2.wav"
                      }
                    }
                  }
                },
                "id": "ask_action_text",
                "next_action_id": ""
              },
              {
                "action_body": {
                  "hold": {
                    "cause": "Пытаемся найти свободного оператора"
                  }
                },
                "id": "hold_action",
                "next_action_id": "forward_action"
              },
              {
                "action_body": {
                  "wait": {
                    "timeout_sec": 15
                  }
                },
                "id": "wait_action",
                "next_action_id": "hangup_action"
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "forward_action",
                "next_action_id": "hangup_action"
              },
              {
                "action_body": {
                  "hangup": {
                    "cause": "normal-clearing"
                  }
                },
                "id": "hangup_action",
                "next_action_id": ""
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "cycled_action",
                "next_action_id": "cycled_action"
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "wrong_next_action_id",
                "next_action_id": "nonexistent_action_id"
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "to_empty_action_body",
                "next_action_id": "empty_action_body_action"
              },
              {
                "action_body": {},
                "id": "empty_action_body_action",
                "next_action_id": "hangup_action"
              }
            ]
          }'),
       ('random_call_external_id2', 'eats_flow', 'default_phone_id',
        '{"payload": {"abonent_name": "Sanya"}, "eater_id": "1337", "scenario_name": "scenario_1"}', 'waiting_for_call_creation',
        '{
            "start_call_actions": [
              {
                "action_body": {
                  "playback": {
                    "play": {
                      "id": "happy_music",
                      "path": "s3:/voices/happy_music.wav"
                    }
                  }
                }
              }
            ],
            "actions": [
              {
                "action_body": {
                  "originate": {
                    "phone_number": "+375445571982",
                    "timeout_sec": 15
                  }
                },
                "id": "originate_action",
                "next_action_id": "playback_action_speak"
              },
              {
                "action_body": {
                  "playback": {
                    "speak": {
                      "text": "Привет. Как дела, {user_name}?"
                    }
                  }
                },
                "id": "playback_action_speak",
                "next_action_id": "playback_action_play"
              },
              {
                "action_body": {
                  "ask": {
                    "action_after_answer": {
                      "-1": {
                        "alias": "-1 answer",
                        "next_action_id": "ask_action_dtmf"
                      },
                      "1": {
                        "alias": "1 answer",
                        "next_action_id": "ask_action_text"
                      },
                      "2": {
                        "alias": "2 answer",
                        "next_action_id": "ask_action_text"
                      },
                      "3": {
                        "alias": "3 answer",
                        "next_action_id": "ask_action_text"
                      }
                    },
                    "allowed_dtmf": "123",
                    "immediate_input": false,
                    "input_mode": "dtmf",
                    "no_input_timeout_ms": 15000,
                    "playback": {
                      "play": {
                        "id": "question1",
                        "path": "s3:/voices/question1.wav"
                      }
                    }
                  }
                },
                "id": "ask_action_dtmf",
                "next_action_id": ""
              },
              {
                "action_body": {
                  "ask": {
                    "action_after_answer": {
                      "default": {
                        "alias": "default answer",
                        "next_action_id": "ask_action_text"
                      },
                      "да": {
                        "alias": "да answer",
                        "next_action_id": "hangup_action"
                      },
                      "нет": {
                        "alias": "нет answer",
                        "next_action_id": "hold_action"
                      },
                      "я не знаю": {
                        "alias": "я не знаю answer",
                        "next_action_id": "wait_action"
                      }
                    },
                    "immediate_input": true,
                    "input_mode": "text",
                    "no_input_timeout_ms": 15000,
                    "playback": {
                      "play": {
                        "id": "question2",
                        "path": "s3:/voices/question2.wav"
                      }
                    }
                  }
                },
                "id": "ask_action_text",
                "next_action_id": ""
              },
              {
                "action_body": {
                  "hold": {
                    "cause": "Пытаемся найти свободного оператора"
                  }
                },
                "id": "hold_action",
                "next_action_id": "forward_action"
              },
              {
                "action_body": {
                  "wait": {
                    "timeout_sec": 15
                  }
                },
                "id": "wait_action",
                "next_action_id": "hangup_action"
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "forward_action",
                "next_action_id": "hangup_action"
              },
              {
                "action_body": {
                  "hangup": {
                    "cause": "normal-clearing"
                  }
                },
                "id": "hangup_action",
                "next_action_id": ""
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "cycled_action",
                "next_action_id": "cycled_action"
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "wrong_next_action_id",
                "next_action_id": "nonexistent_action_id"
              },
              {
                "action_body": {
                  "forward": {
                    "phone_number": "+79156579359",
                    "timeout_sec": 15
                  }
                },
                "id": "to_empty_action_body",
                "next_action_id": "empty_action_body_action"
              },
              {
                "action_body": {},
                "id": "empty_action_body_action",
                "next_action_id": "hangup_action"
              }
            ]
          }'),
       ('random_call_external_id3', 'eats_flow', 'default_phone_id',
        '{"payload": {"abonent_name": "Sanya"}, "eater_id": "1337", "scenario_name": "scenario_1"}', 'telephony_error',
        '{}');
