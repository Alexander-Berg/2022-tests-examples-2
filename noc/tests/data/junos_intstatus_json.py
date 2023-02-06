from data.lib import Data


class Data1(Data):
    content = """
{
    "interface-information" : [
    {
        "attributes" : {"xmlns" : "http://xml.juniper.net/junos/18.2R2/junos-interface",
                        "junos:style" : "terse"
                       },
        "physical-interface" : [
        {
            "name" : [
            {
                "data" : "et-0/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "gr-0/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-0/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-0/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-0/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-0/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-0/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-0/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-0/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-0/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-0/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-0/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-0/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-0/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/13.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-0/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-0/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-0/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/17.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-0/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-0/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-1/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-1/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-1/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-1/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-1/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-1/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-1/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-1/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-1/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-1/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-1/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/12.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-1/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/14.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-1/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-1/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/17.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-1/0/17.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-1/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-1/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-2/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-2/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-2/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-2/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-2/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-2/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-2/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-2/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-2/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-2/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-2/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-2/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-2/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-2/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-2/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-2/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/17.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-2/0/17.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-2/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-2/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-3/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-3/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-3/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-3/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-3/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-3/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-3/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-3/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-3/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-3/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-3/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-3/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-3/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-3/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-3/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-3/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/17.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-3/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-3/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-4/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-4/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-4/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-4/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-4/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-4/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-4/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-4/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-4/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-4/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-4/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-4/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-4/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-4/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-4/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-4/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/17.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-4/0/17.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-4/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-4/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-5/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-5/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-5/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-5/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-5/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-5/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-5/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-5/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-5/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-5/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-5/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/12.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-5/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-5/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-5/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/16.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/17.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-5/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-5/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-6/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-6/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-6/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-6/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-6/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-6/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-6/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-6/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-6/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-6/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-6/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-6/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-6/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-6/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/15.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-6/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/17.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-6/0/17.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/20.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/27.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/28.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-6/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-6/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-7/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-7/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-7/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-7/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-7/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-7/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-7/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae7.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-7/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-7/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-7/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae5.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-7/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/8.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae3.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/9.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/10.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/11.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae1.0"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/17.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/17.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/19.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae102.3000"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/19.3666"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae102.3666"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/19.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae102.32767"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-7/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-7/0/22.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae101.3000"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/22.3666"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae101.3666"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-7/0/22.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae101.32767"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/0.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/0.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-8/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-8/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-8/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-8/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-8/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-8/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/1.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/1.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-8/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/2.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/2.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-8/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/3.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/3.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-8/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/4.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/4.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-8/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/5.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/5.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-8/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/6.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/6.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/7.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/7.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/8.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/8.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/9.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/9.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/10.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/10.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/11.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/11.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/13.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/15.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/17.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/18.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/19.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/19.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/20.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/20.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/21.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/21.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/22.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/23.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/23.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/26.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/27.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/27.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/28.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/28.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-8/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-8/0/29.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-8/0/29.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/0.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/0.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-9/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-9/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-9/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-9/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-9/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-9/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/1.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/1.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-9/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/2.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/2.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-9/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-9/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/4.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/4.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-9/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/5.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/5.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-9/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/6.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/6.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/8.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/8.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/9.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/9.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/10.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/10.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/11.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/11.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/12.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/12.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/14.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/15.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/17.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/17.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/18.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/18.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/19.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/19.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/20.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/20.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/21.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/22.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/22.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/23.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/23.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/24.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/24.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/26.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/26.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/27.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/27.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/28.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-9/0/28.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-9/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-9/0/29.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/0.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/0.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-10/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-10/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-10/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-10/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-10/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-10/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/1.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/1.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-10/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/2.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/2.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-10/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/3.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/3.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-10/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/4.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/4.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-10/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/5.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/5.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-10/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/6.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/6.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/7.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/7.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/8.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/8.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/9.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/9.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/10.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/10.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/11.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/11.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/12.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/13.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/18.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/18.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/19.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/20.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/20.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/21.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/21.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/22.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/22.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/23.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/24.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/25.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/25.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/26.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/26.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/27.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/27.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/28.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/28.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-10/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-10/0/29.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-10/0/29.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/0.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/0.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-11/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-11/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-11/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-11/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-11/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-11/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-11/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/2.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/2.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-11/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-11/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/4.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/4.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-11/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/5.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/5.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-11/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/6.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/6.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/7.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/7.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/8.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/8.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/9.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/9.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/10.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/10.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/11.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/11.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/12"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/12.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/13.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/14"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/14.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/14.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/16"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/16.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/16.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/17"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/17.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/18.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/18.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/19.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/19.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/20.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/20.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/21.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/21.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/22.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/22.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/23.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/23.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/24.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/24.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/25.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/26.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/26.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/27.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/27.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/28.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/28.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-11/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-11/0/29.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-11/0/29.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/0.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/0.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfe-12/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfe-12/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pfh-12/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "pfh-12/0/0.16383"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "pfh-12/0/0.16384"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-12/0/0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/1.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/1.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-12/0/1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/2.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/2.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-12/0/2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-12/0/3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/4.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-12/0/4"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/5.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/5.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "sxe-12/0/5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/6"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/6.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "down"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/8"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/8.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/8.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/9"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/9.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/9.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/10"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/10.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/10.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/11"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/11.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/11.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/13"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/13.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae102.3000"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/13.3666"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae102.3666"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/13.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae102.32767"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/15"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/15.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae101.3000"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/15.3666"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae101.3666"
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/15.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "aenet"
                    }
                    ],
                    "ae-bundle-name" : [
                    {
                        "data" : "ae101.32767"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/18"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/18.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/18.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/19"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/19.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/19.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/20"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/20.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/20.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/21"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/21.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/21.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/22"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/22.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/22.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/23"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/23.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/23.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/24"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/24.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/24.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/25"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/25.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/25.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/26"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/26.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/26.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/27"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/27.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/27.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/28"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/28.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/28.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "et-12/0/29"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "et-12/0/29.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "et-12/0/29.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ae1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "ae1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "87.250.239.154/31",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::2e21:31ff:fe65:f68f/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "mpls",
                        "attributes" : {"junos:emit" : "emit"}
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ae3"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "ae3.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "87.250.239.180/31",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::2e21:31ff:fe65:f690/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "mpls",
                        "attributes" : {"junos:emit" : "emit"}
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ae5"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "ae5.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "87.250.239.182/31",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::2e21:31ff:fe65:f691/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "mpls",
                        "attributes" : {"junos:emit" : "emit"}
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ae7"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "ae7.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "87.250.239.80/31",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::2e21:31ff:fe65:f692/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "mpls",
                        "attributes" : {"junos:emit" : "emit"}
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ae101"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "ae101.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "ae101.3666"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "10.1.1.254/24",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "ae101.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ae102"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "ae102.3000"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "ae102.3666"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "10.2.1.254/24",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::c1:d1/64",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "ae102.32767"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "bme0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "bme0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.1/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    },
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.4/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    },
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.63/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "bme1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "bme1.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.1/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    },
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.4/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "bme2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "bme2.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.1/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    },
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.4/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "cbp0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "dsc"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "em0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "em0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "93.158.171.209"
                        }
                        ],
                        "ifa-destination" : [
                        {
                            "data" : "0/0",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "em1"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "down"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "em2"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "em2.32768"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "192.168.1.2/24",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "esi"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "gre"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "ipip"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "irb"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "jsrv"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "jsrv.1"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "128.0.0.127/2",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "lo0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "lo0.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "95.108.237.168"
                        }
                        ],
                        "ifa-destination" : [
                        {
                            "data" : "0/0",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    },
                    {
                        "ifa-local" : [
                        {
                            "data" : "127.0.0.1"
                        }
                        ],
                        "ifa-destination" : [
                        {
                            "data" : "0/0",
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ],
                    "interface-address" : [
                    {
                        "ifa-local" : [
                        {
                            "data" : "fe80::2e21:310f:fcbb:754a"
                        }
                        ],
                        "ifa-destination" : [
                        {
                            "attributes" : {"junos:emit" : "emit"}
                        }
                        ]
                    }
                    ]
                }
                ]
            },
            {
                "name" : [
                {
                    "data" : "lo0.16385"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "lsi"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ],
            "logical-interface" : [
            {
                "name" : [
                {
                    "data" : "lsi.0"
                }
                ],
                "admin-status" : [
                {
                    "data" : "up"
                }
                ],
                "oper-status" : [
                {
                    "data" : "up"
                }
                ],
                "filter-information" : [
                {
                }
                ],
                "address-family" : [
                {
                    "address-family-name" : [
                    {
                        "data" : "inet"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "iso"
                    }
                    ]
                },
                {
                    "address-family-name" : [
                    {
                        "data" : "inet6"
                    }
                    ]
                }
                ]
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "mtun"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pimd"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pime"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "pip0"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "tap"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        },
        {
            "name" : [
            {
                "data" : "vtep"
            }
            ],
            "admin-status" : [
            {
                "data" : "up"
            }
            ],
            "oper-status" : [
            {
                "data" : "up"
            }
            ]
        }
        ]
    }
    ]
}

{master}
    """
    cmd = "show interfaces terse | display json"
    host = "vla1-1d1"
    version = """
Hostname: vla1-1d1
Model: qfx10016
Junos: 18.2R2.6
JUNOS OS Kernel 64-bit  [20181108.217da31_builder_stable_11]
JUNOS OS libs [20181108.217da31_builder_stable_11]
JUNOS OS runtime [20181108.217da31_builder_stable_11]
JUNOS OS time zone information [20181108.217da31_builder_stable_11]
JUNOS OS libs compat32 [20181108.217da31_builder_stable_11]
JUNOS OS 32-bit compatibility [20181108.217da31_builder_stable_11]
JUNOS py extensions [20181207.090423_builder_junos_182_r2]
JUNOS py base [20181207.090423_builder_junos_182_r2]
JUNOS OS vmguest [20181108.217da31_builder_stable_11]
JUNOS OS crypto [20181108.217da31_builder_stable_11]
JUNOS network stack and utilities [20181207.090423_builder_junos_182_r2]
JUNOS libs [20181207.090423_builder_junos_182_r2]
JUNOS libs compat32 [20181207.090423_builder_junos_182_r2]
JUNOS runtime [20181207.090423_builder_junos_182_r2]
JUNOS Web Management Platform Package [20181207.090423_builder_junos_182_r2]
JUNOS qfx runtime [20181207.090423_builder_junos_182_r2]
JUNOS common platform support [20181207.090423_builder_junos_182_r2]
JUNOS qfx platform support [20181207.090423_builder_junos_182_r2]
JUNOS dcp network modules [20181207.090423_builder_junos_182_r2]
JUNOS modules [20181207.090423_builder_junos_182_r2]
JUNOS qfx modules [20181207.090423_builder_junos_182_r2]
JUNOS qfx Data Plane Crypto Support [20181207.090423_builder_junos_182_r2]
JUNOS daemons [20181207.090423_builder_junos_182_r2]
JUNOS qfx daemons [20181207.090423_builder_junos_182_r2]
JUNOS Services URL Filter package [20181207.090423_builder_junos_182_r2]
JUNOS Services TLB Service PIC package [20181207.090423_builder_junos_182_r2]
JUNOS Services Telemetry [20181207.090423_builder_junos_182_r2]
JUNOS Services SSL [20181207.090423_builder_junos_182_r2]
JUNOS Services SOFTWIRE [20181207.090423_builder_junos_182_r2]
JUNOS Services Stateful Firewall [20181207.090423_builder_junos_182_r2]
JUNOS Services RPM [20181207.090423_builder_junos_182_r2]
JUNOS Services PCEF package [20181207.090423_builder_junos_182_r2]
JUNOS Services NAT [20181207.090423_builder_junos_182_r2]
JUNOS Services Mobile Subscriber Service Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services MobileNext Software package [20181207.090423_builder_junos_182_r2]
JUNOS Services Logging Report Framework package [20181207.090423_builder_junos_182_r2]
JUNOS Services LL-PDF Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services Jflow Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services Deep Packet Inspection package [20181207.090423_builder_junos_182_r2]
JUNOS Services IPSec [20181207.090423_builder_junos_182_r2]
JUNOS Services IDS [20181207.090423_builder_junos_182_r2]
JUNOS IDP Services [20181207.090423_builder_junos_182_r2]
JUNOS Services HTTP Content Management package [20181207.090423_builder_junos_182_r2]
JUNOS Services Flowd MS-MPC Software package [20181207.090423_builder_junos_182_r2]
JUNOS Services Crypto [20181207.090423_builder_junos_182_r2]
JUNOS Services Captive Portal and Content Delivery Container package [20181207.090423_builder_junos_182_r2]
JUNOS Services COS [20181207.090423_builder_junos_182_r2]
JUNOS AppId Services [20181207.090423_builder_junos_182_r2]
JUNOS Services Application Level Gateways [20181207.090423_builder_junos_182_r2]
JUNOS Services AACL Container package [20181207.090423_builder_junos_182_r2]
JUNOS SDN Software Suite [20181207.090423_builder_junos_182_r2]
JUNOS Extension Toolkit [20181207.090423_builder_junos_182_r2]
JUNOS Packet Forwarding Engine Support (DC-PFE) [20181207.090423_builder_junos_182_r2]
JUNOS Packet Forwarding Engine Support (M/T Common) [20181207.090423_builder_junos_182_r2]
JUNOS J-Insight [20181207.090423_builder_junos_182_r2]
JUNOS jfirmware [20181207.090423_builder_junos_182_r2]
JUNOS Online Documentation [20181207.090423_builder_junos_182_r2]
JUNOS jail runtime [20181108.217da31_builder_stable_11]
JUNOS FIPS mode utilities [20181207.090423_builder_junos_182_r2]
JUNOS Host Software [3.14.64-rt67-WR7.0.0.26_ovp:3.1.0]
JUNOS Host qfx-10-m platform package [18.2R2.6]
JUNOS Host qfx-10-m fabric package [18.2R2.6]
JUNOS Host qfx-10-m data-plane package [18.2R2.6]
JUNOS Host qfx-10-m base package [18.2R2.6]
JUNOS Host qfx-10-m control-plane package [18.2R2.6]

{master}
    """
    result = [{'interface': 'et-0/0/0', 'state': 'up'},
              {'interface': 'et-0/0/0.0', 'state': 'up'},
              {'interface': 'gr-0/0/0', 'state': 'up'},
              {'interface': 'pfe-0/0/0', 'state': 'up'},
              {'interface': 'pfe-0/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-0/0/0', 'state': 'up'},
              {'interface': 'pfh-0/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-0/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-0/0/0', 'state': 'up'},
              {'interface': 'et-0/0/1', 'state': 'up'},
              {'interface': 'et-0/0/1.0', 'state': 'up'},
              {'interface': 'sxe-0/0/1', 'state': 'up'},
              {'interface': 'et-0/0/2', 'state': 'up'},
              {'interface': 'et-0/0/2.0', 'state': 'up'},
              {'interface': 'sxe-0/0/2', 'state': 'up'},
              {'interface': 'et-0/0/3', 'state': 'up'},
              {'interface': 'et-0/0/3.0', 'state': 'up'},
              {'interface': 'sxe-0/0/3', 'state': 'up'},
              {'interface': 'et-0/0/4', 'state': 'up'},
              {'interface': 'et-0/0/4.0', 'state': 'up'},
              {'interface': 'sxe-0/0/4', 'state': 'up'},
              {'interface': 'et-0/0/5', 'state': 'up'},
              {'interface': 'et-0/0/5.0', 'state': 'up'},
              {'interface': 'sxe-0/0/5', 'state': 'up'},
              {'interface': 'et-0/0/6', 'state': 'up'},
              {'interface': 'et-0/0/6.0', 'state': 'up'},
              {'interface': 'et-0/0/7', 'state': 'up'},
              {'interface': 'et-0/0/7.0', 'state': 'up'},
              {'interface': 'et-0/0/8', 'state': 'up'},
              {'interface': 'et-0/0/8.0', 'state': 'up'},
              {'interface': 'et-0/0/9', 'state': 'up'},
              {'interface': 'et-0/0/9.0', 'state': 'up'},
              {'interface': 'et-0/0/10', 'state': 'up'},
              {'interface': 'et-0/0/10.0', 'state': 'up'},
              {'interface': 'et-0/0/11', 'state': 'up'},
              {'interface': 'et-0/0/11.0', 'state': 'up'},
              {'interface': 'et-0/0/12', 'state': 'up'},
              {'interface': 'et-0/0/12.3000', 'state': 'up'},
              {'interface': 'et-0/0/12.32767', 'state': 'up'},
              {'interface': 'et-0/0/13', 'state': 'down'},
              {'interface': 'et-0/0/13.0', 'state': 'down'},
              {'interface': 'et-0/0/14', 'state': 'up'},
              {'interface': 'et-0/0/14.3000', 'state': 'up'},
              {'interface': 'et-0/0/14.32767', 'state': 'up'},
              {'interface': 'et-0/0/15', 'state': 'up'},
              {'interface': 'et-0/0/15.3000', 'state': 'up'},
              {'interface': 'et-0/0/15.32767', 'state': 'up'},
              {'interface': 'et-0/0/16', 'state': 'up'},
              {'interface': 'et-0/0/16.3000', 'state': 'up'},
              {'interface': 'et-0/0/16.32767', 'state': 'up'},
              {'interface': 'et-0/0/17', 'state': 'down'},
              {'interface': 'et-0/0/17.0', 'state': 'down'},
              {'interface': 'et-0/0/18', 'state': 'up'},
              {'interface': 'et-0/0/18.0', 'state': 'up'},
              {'interface': 'et-0/0/19', 'state': 'up'},
              {'interface': 'et-0/0/19.0', 'state': 'up'},
              {'interface': 'et-0/0/20', 'state': 'up'},
              {'interface': 'et-0/0/20.0', 'state': 'up'},
              {'interface': 'et-0/0/21', 'state': 'up'},
              {'interface': 'et-0/0/21.0', 'state': 'up'},
              {'interface': 'et-0/0/22', 'state': 'up'},
              {'interface': 'et-0/0/22.0', 'state': 'up'},
              {'interface': 'et-0/0/23', 'state': 'up'},
              {'interface': 'et-0/0/23.0', 'state': 'up'},
              {'interface': 'et-0/0/24', 'state': 'up'},
              {'interface': 'et-0/0/24.0', 'state': 'up'},
              {'interface': 'et-0/0/25', 'state': 'up'},
              {'interface': 'et-0/0/25.0', 'state': 'up'},
              {'interface': 'et-0/0/26', 'state': 'up'},
              {'interface': 'et-0/0/26.0', 'state': 'up'},
              {'interface': 'et-0/0/27', 'state': 'up'},
              {'interface': 'et-0/0/27.0', 'state': 'up'},
              {'interface': 'et-0/0/28', 'state': 'up'},
              {'interface': 'et-0/0/28.0', 'state': 'up'},
              {'interface': 'et-0/0/29', 'state': 'up'},
              {'interface': 'et-0/0/29.0', 'state': 'up'},
              {'interface': 'et-1/0/0', 'state': 'up'},
              {'interface': 'et-1/0/0.0', 'state': 'up'},
              {'interface': 'pfe-1/0/0', 'state': 'up'},
              {'interface': 'pfe-1/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-1/0/0', 'state': 'up'},
              {'interface': 'pfh-1/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-1/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-1/0/0', 'state': 'up'},
              {'interface': 'et-1/0/1', 'state': 'up'},
              {'interface': 'et-1/0/1.0', 'state': 'up'},
              {'interface': 'sxe-1/0/1', 'state': 'up'},
              {'interface': 'et-1/0/2', 'state': 'up'},
              {'interface': 'et-1/0/2.0', 'state': 'up'},
              {'interface': 'sxe-1/0/2', 'state': 'up'},
              {'interface': 'et-1/0/3', 'state': 'up'},
              {'interface': 'et-1/0/3.0', 'state': 'up'},
              {'interface': 'sxe-1/0/3', 'state': 'up'},
              {'interface': 'et-1/0/4', 'state': 'up'},
              {'interface': 'et-1/0/4.0', 'state': 'up'},
              {'interface': 'sxe-1/0/4', 'state': 'up'},
              {'interface': 'et-1/0/5', 'state': 'up'},
              {'interface': 'et-1/0/5.0', 'state': 'up'},
              {'interface': 'sxe-1/0/5', 'state': 'up'},
              {'interface': 'et-1/0/6', 'state': 'up'},
              {'interface': 'et-1/0/6.0', 'state': 'up'},
              {'interface': 'et-1/0/7', 'state': 'up'},
              {'interface': 'et-1/0/7.0', 'state': 'up'},
              {'interface': 'et-1/0/8', 'state': 'up'},
              {'interface': 'et-1/0/8.0', 'state': 'up'},
              {'interface': 'et-1/0/9', 'state': 'up'},
              {'interface': 'et-1/0/9.0', 'state': 'up'},
              {'interface': 'et-1/0/10', 'state': 'up'},
              {'interface': 'et-1/0/10.0', 'state': 'up'},
              {'interface': 'et-1/0/11', 'state': 'up'},
              {'interface': 'et-1/0/11.0', 'state': 'up'},
              {'interface': 'et-1/0/12', 'state': 'down'},
              {'interface': 'et-1/0/12.0', 'state': 'down'},
              {'interface': 'et-1/0/13', 'state': 'up'},
              {'interface': 'et-1/0/13.3000', 'state': 'up'},
              {'interface': 'et-1/0/13.32767', 'state': 'up'},
              {'interface': 'et-1/0/14', 'state': 'down'},
              {'interface': 'et-1/0/14.0', 'state': 'down'},
              {'interface': 'et-1/0/15', 'state': 'down'},
              {'interface': 'et-1/0/15.3000', 'state': 'down'},
              {'interface': 'et-1/0/15.32767', 'state': 'down'},
              {'interface': 'et-1/0/16', 'state': 'up'},
              {'interface': 'et-1/0/16.3000', 'state': 'up'},
              {'interface': 'et-1/0/16.32767', 'state': 'up'},
              {'interface': 'et-1/0/17', 'state': 'up'},
              {'interface': 'et-1/0/17.3000', 'state': 'up'},
              {'interface': 'et-1/0/17.32767', 'state': 'up'},
              {'interface': 'et-1/0/18', 'state': 'up'},
              {'interface': 'et-1/0/18.0', 'state': 'up'},
              {'interface': 'et-1/0/19', 'state': 'up'},
              {'interface': 'et-1/0/19.0', 'state': 'up'},
              {'interface': 'et-1/0/20', 'state': 'up'},
              {'interface': 'et-1/0/20.0', 'state': 'up'},
              {'interface': 'et-1/0/21', 'state': 'up'},
              {'interface': 'et-1/0/21.0', 'state': 'up'},
              {'interface': 'et-1/0/22', 'state': 'up'},
              {'interface': 'et-1/0/22.0', 'state': 'up'},
              {'interface': 'et-1/0/23', 'state': 'up'},
              {'interface': 'et-1/0/23.0', 'state': 'up'},
              {'interface': 'et-1/0/24', 'state': 'up'},
              {'interface': 'et-1/0/24.0', 'state': 'up'},
              {'interface': 'et-1/0/25', 'state': 'up'},
              {'interface': 'et-1/0/25.0', 'state': 'up'},
              {'interface': 'et-1/0/26', 'state': 'up'},
              {'interface': 'et-1/0/26.0', 'state': 'up'},
              {'interface': 'et-1/0/27', 'state': 'up'},
              {'interface': 'et-1/0/27.0', 'state': 'up'},
              {'interface': 'et-1/0/28', 'state': 'up'},
              {'interface': 'et-1/0/28.0', 'state': 'up'},
              {'interface': 'et-1/0/29', 'state': 'up'},
              {'interface': 'et-1/0/29.0', 'state': 'up'},
              {'interface': 'et-2/0/0', 'state': 'up'},
              {'interface': 'et-2/0/0.0', 'state': 'up'},
              {'interface': 'pfe-2/0/0', 'state': 'up'},
              {'interface': 'pfe-2/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-2/0/0', 'state': 'up'},
              {'interface': 'pfh-2/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-2/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-2/0/0', 'state': 'up'},
              {'interface': 'et-2/0/1', 'state': 'up'},
              {'interface': 'et-2/0/1.0', 'state': 'up'},
              {'interface': 'sxe-2/0/1', 'state': 'up'},
              {'interface': 'et-2/0/2', 'state': 'up'},
              {'interface': 'et-2/0/2.0', 'state': 'up'},
              {'interface': 'sxe-2/0/2', 'state': 'up'},
              {'interface': 'et-2/0/3', 'state': 'up'},
              {'interface': 'et-2/0/3.0', 'state': 'up'},
              {'interface': 'sxe-2/0/3', 'state': 'up'},
              {'interface': 'et-2/0/4', 'state': 'up'},
              {'interface': 'et-2/0/4.0', 'state': 'up'},
              {'interface': 'sxe-2/0/4', 'state': 'up'},
              {'interface': 'et-2/0/5', 'state': 'up'},
              {'interface': 'et-2/0/5.0', 'state': 'up'},
              {'interface': 'sxe-2/0/5', 'state': 'up'},
              {'interface': 'et-2/0/6', 'state': 'up'},
              {'interface': 'et-2/0/6.0', 'state': 'up'},
              {'interface': 'et-2/0/7', 'state': 'up'},
              {'interface': 'et-2/0/7.0', 'state': 'up'},
              {'interface': 'et-2/0/8', 'state': 'up'},
              {'interface': 'et-2/0/8.0', 'state': 'up'},
              {'interface': 'et-2/0/9', 'state': 'up'},
              {'interface': 'et-2/0/9.0', 'state': 'up'},
              {'interface': 'et-2/0/10', 'state': 'up'},
              {'interface': 'et-2/0/10.0', 'state': 'up'},
              {'interface': 'et-2/0/11', 'state': 'up'},
              {'interface': 'et-2/0/11.0', 'state': 'up'},
              {'interface': 'et-2/0/12', 'state': 'up'},
              {'interface': 'et-2/0/12.3000', 'state': 'up'},
              {'interface': 'et-2/0/12.32767', 'state': 'up'},
              {'interface': 'et-2/0/13', 'state': 'up'},
              {'interface': 'et-2/0/13.3000', 'state': 'up'},
              {'interface': 'et-2/0/13.32767', 'state': 'up'},
              {'interface': 'et-2/0/14', 'state': 'up'},
              {'interface': 'et-2/0/14.3000', 'state': 'up'},
              {'interface': 'et-2/0/14.32767', 'state': 'up'},
              {'interface': 'et-2/0/15', 'state': 'up'},
              {'interface': 'et-2/0/15.3000', 'state': 'up'},
              {'interface': 'et-2/0/15.32767', 'state': 'up'},
              {'interface': 'et-2/0/16', 'state': 'up'},
              {'interface': 'et-2/0/16.3000', 'state': 'up'},
              {'interface': 'et-2/0/16.32767', 'state': 'up'},
              {'interface': 'et-2/0/17', 'state': 'up'},
              {'interface': 'et-2/0/17.3000', 'state': 'up'},
              {'interface': 'et-2/0/17.32767', 'state': 'up'},
              {'interface': 'et-2/0/18', 'state': 'up'},
              {'interface': 'et-2/0/18.0', 'state': 'up'},
              {'interface': 'et-2/0/19', 'state': 'up'},
              {'interface': 'et-2/0/19.0', 'state': 'up'},
              {'interface': 'et-2/0/20', 'state': 'up'},
              {'interface': 'et-2/0/20.0', 'state': 'up'},
              {'interface': 'et-2/0/21', 'state': 'up'},
              {'interface': 'et-2/0/21.0', 'state': 'up'},
              {'interface': 'et-2/0/22', 'state': 'up'},
              {'interface': 'et-2/0/22.0', 'state': 'up'},
              {'interface': 'et-2/0/23', 'state': 'up'},
              {'interface': 'et-2/0/23.0', 'state': 'up'},
              {'interface': 'et-2/0/24', 'state': 'up'},
              {'interface': 'et-2/0/24.0', 'state': 'up'},
              {'interface': 'et-2/0/25', 'state': 'up'},
              {'interface': 'et-2/0/25.0', 'state': 'up'},
              {'interface': 'et-2/0/26', 'state': 'up'},
              {'interface': 'et-2/0/26.0', 'state': 'up'},
              {'interface': 'et-2/0/27', 'state': 'up'},
              {'interface': 'et-2/0/27.0', 'state': 'up'},
              {'interface': 'et-2/0/28', 'state': 'up'},
              {'interface': 'et-2/0/28.0', 'state': 'up'},
              {'interface': 'et-2/0/29', 'state': 'up'},
              {'interface': 'et-2/0/29.0', 'state': 'up'},
              {'interface': 'et-3/0/0', 'state': 'up'},
              {'interface': 'et-3/0/0.0', 'state': 'up'},
              {'interface': 'pfe-3/0/0', 'state': 'up'},
              {'interface': 'pfe-3/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-3/0/0', 'state': 'up'},
              {'interface': 'pfh-3/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-3/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-3/0/0', 'state': 'up'},
              {'interface': 'et-3/0/1', 'state': 'up'},
              {'interface': 'et-3/0/1.0', 'state': 'up'},
              {'interface': 'sxe-3/0/1', 'state': 'up'},
              {'interface': 'et-3/0/2', 'state': 'up'},
              {'interface': 'et-3/0/2.0', 'state': 'up'},
              {'interface': 'sxe-3/0/2', 'state': 'up'},
              {'interface': 'et-3/0/3', 'state': 'up'},
              {'interface': 'et-3/0/3.0', 'state': 'up'},
              {'interface': 'sxe-3/0/3', 'state': 'up'},
              {'interface': 'et-3/0/4', 'state': 'up'},
              {'interface': 'et-3/0/4.0', 'state': 'up'},
              {'interface': 'sxe-3/0/4', 'state': 'up'},
              {'interface': 'et-3/0/5', 'state': 'up'},
              {'interface': 'et-3/0/5.0', 'state': 'up'},
              {'interface': 'sxe-3/0/5', 'state': 'up'},
              {'interface': 'et-3/0/6', 'state': 'up'},
              {'interface': 'et-3/0/6.0', 'state': 'up'},
              {'interface': 'et-3/0/7', 'state': 'up'},
              {'interface': 'et-3/0/7.0', 'state': 'up'},
              {'interface': 'et-3/0/8', 'state': 'up'},
              {'interface': 'et-3/0/8.0', 'state': 'up'},
              {'interface': 'et-3/0/9', 'state': 'up'},
              {'interface': 'et-3/0/9.0', 'state': 'up'},
              {'interface': 'et-3/0/10', 'state': 'up'},
              {'interface': 'et-3/0/10.0', 'state': 'up'},
              {'interface': 'et-3/0/11', 'state': 'up'},
              {'interface': 'et-3/0/11.0', 'state': 'up'},
              {'interface': 'et-3/0/12', 'state': 'up'},
              {'interface': 'et-3/0/12.3000', 'state': 'up'},
              {'interface': 'et-3/0/12.32767', 'state': 'up'},
              {'interface': 'et-3/0/13', 'state': 'up'},
              {'interface': 'et-3/0/13.3000', 'state': 'up'},
              {'interface': 'et-3/0/13.32767', 'state': 'up'},
              {'interface': 'et-3/0/14', 'state': 'up'},
              {'interface': 'et-3/0/14.3000', 'state': 'up'},
              {'interface': 'et-3/0/14.32767', 'state': 'up'},
              {'interface': 'et-3/0/15', 'state': 'up'},
              {'interface': 'et-3/0/15.3000', 'state': 'up'},
              {'interface': 'et-3/0/15.32767', 'state': 'up'},
              {'interface': 'et-3/0/16', 'state': 'up'},
              {'interface': 'et-3/0/16.3000', 'state': 'up'},
              {'interface': 'et-3/0/16.32767', 'state': 'up'},
              {'interface': 'et-3/0/17', 'state': 'down'},
              {'interface': 'et-3/0/17.0', 'state': 'down'},
              {'interface': 'et-3/0/18', 'state': 'up'},
              {'interface': 'et-3/0/18.0', 'state': 'up'},
              {'interface': 'et-3/0/19', 'state': 'up'},
              {'interface': 'et-3/0/19.0', 'state': 'up'},
              {'interface': 'et-3/0/20', 'state': 'up'},
              {'interface': 'et-3/0/20.0', 'state': 'up'},
              {'interface': 'et-3/0/21', 'state': 'up'},
              {'interface': 'et-3/0/21.0', 'state': 'up'},
              {'interface': 'et-3/0/22', 'state': 'up'},
              {'interface': 'et-3/0/22.0', 'state': 'up'},
              {'interface': 'et-3/0/23', 'state': 'up'},
              {'interface': 'et-3/0/23.0', 'state': 'up'},
              {'interface': 'et-3/0/24', 'state': 'up'},
              {'interface': 'et-3/0/24.0', 'state': 'up'},
              {'interface': 'et-3/0/25', 'state': 'up'},
              {'interface': 'et-3/0/25.0', 'state': 'up'},
              {'interface': 'et-3/0/26', 'state': 'up'},
              {'interface': 'et-3/0/26.0', 'state': 'up'},
              {'interface': 'et-3/0/27', 'state': 'up'},
              {'interface': 'et-3/0/27.0', 'state': 'up'},
              {'interface': 'et-3/0/28', 'state': 'up'},
              {'interface': 'et-3/0/28.0', 'state': 'up'},
              {'interface': 'et-3/0/29', 'state': 'up'},
              {'interface': 'et-3/0/29.0', 'state': 'up'},
              {'interface': 'et-4/0/0', 'state': 'up'},
              {'interface': 'et-4/0/0.0', 'state': 'up'},
              {'interface': 'pfe-4/0/0', 'state': 'up'},
              {'interface': 'pfe-4/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-4/0/0', 'state': 'up'},
              {'interface': 'pfh-4/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-4/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-4/0/0', 'state': 'up'},
              {'interface': 'et-4/0/1', 'state': 'up'},
              {'interface': 'et-4/0/1.0', 'state': 'up'},
              {'interface': 'sxe-4/0/1', 'state': 'up'},
              {'interface': 'et-4/0/2', 'state': 'up'},
              {'interface': 'et-4/0/2.0', 'state': 'up'},
              {'interface': 'sxe-4/0/2', 'state': 'up'},
              {'interface': 'et-4/0/3', 'state': 'up'},
              {'interface': 'et-4/0/3.0', 'state': 'up'},
              {'interface': 'sxe-4/0/3', 'state': 'up'},
              {'interface': 'et-4/0/4', 'state': 'up'},
              {'interface': 'et-4/0/4.0', 'state': 'up'},
              {'interface': 'sxe-4/0/4', 'state': 'up'},
              {'interface': 'et-4/0/5', 'state': 'up'},
              {'interface': 'et-4/0/5.0', 'state': 'up'},
              {'interface': 'sxe-4/0/5', 'state': 'up'},
              {'interface': 'et-4/0/6', 'state': 'up'},
              {'interface': 'et-4/0/6.0', 'state': 'up'},
              {'interface': 'et-4/0/7', 'state': 'up'},
              {'interface': 'et-4/0/7.0', 'state': 'up'},
              {'interface': 'et-4/0/8', 'state': 'up'},
              {'interface': 'et-4/0/8.0', 'state': 'up'},
              {'interface': 'et-4/0/9', 'state': 'up'},
              {'interface': 'et-4/0/9.0', 'state': 'up'},
              {'interface': 'et-4/0/10', 'state': 'up'},
              {'interface': 'et-4/0/10.0', 'state': 'up'},
              {'interface': 'et-4/0/11', 'state': 'up'},
              {'interface': 'et-4/0/11.0', 'state': 'up'},
              {'interface': 'et-4/0/12', 'state': 'up'},
              {'interface': 'et-4/0/12.3000', 'state': 'up'},
              {'interface': 'et-4/0/12.32767', 'state': 'up'},
              {'interface': 'et-4/0/13', 'state': 'up'},
              {'interface': 'et-4/0/13.3000', 'state': 'up'},
              {'interface': 'et-4/0/13.32767', 'state': 'up'},
              {'interface': 'et-4/0/14', 'state': 'up'},
              {'interface': 'et-4/0/14.3000', 'state': 'up'},
              {'interface': 'et-4/0/14.32767', 'state': 'up'},
              {'interface': 'et-4/0/15', 'state': 'up'},
              {'interface': 'et-4/0/15.3000', 'state': 'up'},
              {'interface': 'et-4/0/15.32767', 'state': 'up'},
              {'interface': 'et-4/0/16', 'state': 'up'},
              {'interface': 'et-4/0/16.3000', 'state': 'up'},
              {'interface': 'et-4/0/16.32767', 'state': 'up'},
              {'interface': 'et-4/0/17', 'state': 'up'},
              {'interface': 'et-4/0/17.3000', 'state': 'up'},
              {'interface': 'et-4/0/17.32767', 'state': 'up'},
              {'interface': 'et-4/0/18', 'state': 'up'},
              {'interface': 'et-4/0/18.0', 'state': 'up'},
              {'interface': 'et-4/0/19', 'state': 'up'},
              {'interface': 'et-4/0/19.0', 'state': 'up'},
              {'interface': 'et-4/0/20', 'state': 'up'},
              {'interface': 'et-4/0/20.0', 'state': 'up'},
              {'interface': 'et-4/0/21', 'state': 'up'},
              {'interface': 'et-4/0/21.0', 'state': 'up'},
              {'interface': 'et-4/0/22', 'state': 'up'},
              {'interface': 'et-4/0/22.0', 'state': 'up'},
              {'interface': 'et-4/0/23', 'state': 'up'},
              {'interface': 'et-4/0/23.0', 'state': 'up'},
              {'interface': 'et-4/0/24', 'state': 'up'},
              {'interface': 'et-4/0/24.0', 'state': 'up'},
              {'interface': 'et-4/0/25', 'state': 'up'},
              {'interface': 'et-4/0/25.0', 'state': 'up'},
              {'interface': 'et-4/0/26', 'state': 'up'},
              {'interface': 'et-4/0/26.0', 'state': 'up'},
              {'interface': 'et-4/0/27', 'state': 'up'},
              {'interface': 'et-4/0/27.0', 'state': 'up'},
              {'interface': 'et-4/0/28', 'state': 'up'},
              {'interface': 'et-4/0/28.0', 'state': 'up'},
              {'interface': 'et-4/0/29', 'state': 'up'},
              {'interface': 'et-4/0/29.0', 'state': 'up'},
              {'interface': 'et-5/0/0', 'state': 'up'},
              {'interface': 'et-5/0/0.0', 'state': 'up'},
              {'interface': 'pfe-5/0/0', 'state': 'up'},
              {'interface': 'pfe-5/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-5/0/0', 'state': 'up'},
              {'interface': 'pfh-5/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-5/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-5/0/0', 'state': 'up'},
              {'interface': 'et-5/0/1', 'state': 'up'},
              {'interface': 'et-5/0/1.0', 'state': 'up'},
              {'interface': 'sxe-5/0/1', 'state': 'up'},
              {'interface': 'et-5/0/2', 'state': 'up'},
              {'interface': 'et-5/0/2.0', 'state': 'up'},
              {'interface': 'sxe-5/0/2', 'state': 'up'},
              {'interface': 'et-5/0/3', 'state': 'up'},
              {'interface': 'et-5/0/3.0', 'state': 'up'},
              {'interface': 'sxe-5/0/3', 'state': 'up'},
              {'interface': 'et-5/0/4', 'state': 'up'},
              {'interface': 'et-5/0/4.0', 'state': 'up'},
              {'interface': 'sxe-5/0/4', 'state': 'up'},
              {'interface': 'et-5/0/5', 'state': 'up'},
              {'interface': 'et-5/0/5.0', 'state': 'up'},
              {'interface': 'sxe-5/0/5', 'state': 'up'},
              {'interface': 'et-5/0/6', 'state': 'up'},
              {'interface': 'et-5/0/6.0', 'state': 'up'},
              {'interface': 'et-5/0/7', 'state': 'up'},
              {'interface': 'et-5/0/7.0', 'state': 'up'},
              {'interface': 'et-5/0/8', 'state': 'up'},
              {'interface': 'et-5/0/8.0', 'state': 'up'},
              {'interface': 'et-5/0/9', 'state': 'up'},
              {'interface': 'et-5/0/9.0', 'state': 'up'},
              {'interface': 'et-5/0/10', 'state': 'up'},
              {'interface': 'et-5/0/10.0', 'state': 'up'},
              {'interface': 'et-5/0/11', 'state': 'up'},
              {'interface': 'et-5/0/11.0', 'state': 'up'},
              {'interface': 'et-5/0/12', 'state': 'down'},
              {'interface': 'et-5/0/12.0', 'state': 'down'},
              {'interface': 'et-5/0/13', 'state': 'up'},
              {'interface': 'et-5/0/13.3000', 'state': 'up'},
              {'interface': 'et-5/0/13.32767', 'state': 'up'},
              {'interface': 'et-5/0/14', 'state': 'up'},
              {'interface': 'et-5/0/14.3000', 'state': 'up'},
              {'interface': 'et-5/0/14.32767', 'state': 'up'},
              {'interface': 'et-5/0/15', 'state': 'up'},
              {'interface': 'et-5/0/15.3000', 'state': 'up'},
              {'interface': 'et-5/0/15.32767', 'state': 'up'},
              {'interface': 'et-5/0/16', 'state': 'down'},
              {'interface': 'et-5/0/16.0', 'state': 'down'},
              {'interface': 'et-5/0/17', 'state': 'down'},
              {'interface': 'et-5/0/17.0', 'state': 'down'},
              {'interface': 'et-5/0/18', 'state': 'up'},
              {'interface': 'et-5/0/18.0', 'state': 'up'},
              {'interface': 'et-5/0/19', 'state': 'up'},
              {'interface': 'et-5/0/19.0', 'state': 'up'},
              {'interface': 'et-5/0/20', 'state': 'up'},
              {'interface': 'et-5/0/20.0', 'state': 'up'},
              {'interface': 'et-5/0/21', 'state': 'up'},
              {'interface': 'et-5/0/21.0', 'state': 'up'},
              {'interface': 'et-5/0/22', 'state': 'up'},
              {'interface': 'et-5/0/22.0', 'state': 'up'},
              {'interface': 'et-5/0/23', 'state': 'up'},
              {'interface': 'et-5/0/23.0', 'state': 'up'},
              {'interface': 'et-5/0/24', 'state': 'up'},
              {'interface': 'et-5/0/24.0', 'state': 'up'},
              {'interface': 'et-5/0/25', 'state': 'up'},
              {'interface': 'et-5/0/25.0', 'state': 'up'},
              {'interface': 'et-5/0/26', 'state': 'up'},
              {'interface': 'et-5/0/26.0', 'state': 'up'},
              {'interface': 'et-5/0/27', 'state': 'up'},
              {'interface': 'et-5/0/27.0', 'state': 'up'},
              {'interface': 'et-5/0/28', 'state': 'up'},
              {'interface': 'et-5/0/28.0', 'state': 'up'},
              {'interface': 'et-5/0/29', 'state': 'up'},
              {'interface': 'et-5/0/29.0', 'state': 'up'},
              {'interface': 'et-6/0/0', 'state': 'up'},
              {'interface': 'et-6/0/0.0', 'state': 'up'},
              {'interface': 'pfe-6/0/0', 'state': 'up'},
              {'interface': 'pfe-6/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-6/0/0', 'state': 'up'},
              {'interface': 'pfh-6/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-6/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-6/0/0', 'state': 'up'},
              {'interface': 'et-6/0/1', 'state': 'up'},
              {'interface': 'et-6/0/1.0', 'state': 'up'},
              {'interface': 'sxe-6/0/1', 'state': 'up'},
              {'interface': 'et-6/0/2', 'state': 'up'},
              {'interface': 'et-6/0/2.0', 'state': 'up'},
              {'interface': 'sxe-6/0/2', 'state': 'up'},
              {'interface': 'et-6/0/3', 'state': 'up'},
              {'interface': 'et-6/0/3.0', 'state': 'up'},
              {'interface': 'sxe-6/0/3', 'state': 'up'},
              {'interface': 'et-6/0/4', 'state': 'up'},
              {'interface': 'et-6/0/4.0', 'state': 'up'},
              {'interface': 'sxe-6/0/4', 'state': 'up'},
              {'interface': 'et-6/0/5', 'state': 'up'},
              {'interface': 'et-6/0/5.0', 'state': 'up'},
              {'interface': 'sxe-6/0/5', 'state': 'up'},
              {'interface': 'et-6/0/6', 'state': 'up'},
              {'interface': 'et-6/0/6.0', 'state': 'up'},
              {'interface': 'et-6/0/7', 'state': 'up'},
              {'interface': 'et-6/0/7.0', 'state': 'up'},
              {'interface': 'et-6/0/8', 'state': 'up'},
              {'interface': 'et-6/0/8.0', 'state': 'up'},
              {'interface': 'et-6/0/9', 'state': 'up'},
              {'interface': 'et-6/0/9.0', 'state': 'up'},
              {'interface': 'et-6/0/10', 'state': 'up'},
              {'interface': 'et-6/0/10.0', 'state': 'up'},
              {'interface': 'et-6/0/11', 'state': 'up'},
              {'interface': 'et-6/0/11.0', 'state': 'up'},
              {'interface': 'et-6/0/12', 'state': 'up'},
              {'interface': 'et-6/0/12.3000', 'state': 'up'},
              {'interface': 'et-6/0/12.32767', 'state': 'up'},
              {'interface': 'et-6/0/13', 'state': 'up'},
              {'interface': 'et-6/0/13.3000', 'state': 'up'},
              {'interface': 'et-6/0/13.32767', 'state': 'up'},
              {'interface': 'et-6/0/14', 'state': 'up'},
              {'interface': 'et-6/0/14.3000', 'state': 'up'},
              {'interface': 'et-6/0/14.32767', 'state': 'up'},
              {'interface': 'et-6/0/15', 'state': 'down'},
              {'interface': 'et-6/0/15.0', 'state': 'down'},
              {'interface': 'et-6/0/16', 'state': 'up'},
              {'interface': 'et-6/0/16.3000', 'state': 'up'},
              {'interface': 'et-6/0/16.32767', 'state': 'up'},
              {'interface': 'et-6/0/17', 'state': 'up'},
              {'interface': 'et-6/0/17.3000', 'state': 'up'},
              {'interface': 'et-6/0/17.32767', 'state': 'up'},
              {'interface': 'et-6/0/18', 'state': 'up'},
              {'interface': 'et-6/0/18.0', 'state': 'up'},
              {'interface': 'et-6/0/19', 'state': 'down'},
              {'interface': 'et-6/0/19.0', 'state': 'down'},
              {'interface': 'et-6/0/20', 'state': 'up'},
              {'interface': 'et-6/0/20.0', 'state': 'up'},
              {'interface': 'et-6/0/21', 'state': 'up'},
              {'interface': 'et-6/0/21.0', 'state': 'up'},
              {'interface': 'et-6/0/22', 'state': 'up'},
              {'interface': 'et-6/0/22.0', 'state': 'up'},
              {'interface': 'et-6/0/23', 'state': 'up'},
              {'interface': 'et-6/0/23.0', 'state': 'up'},
              {'interface': 'et-6/0/24', 'state': 'up'},
              {'interface': 'et-6/0/24.0', 'state': 'up'},
              {'interface': 'et-6/0/25', 'state': 'up'},
              {'interface': 'et-6/0/25.0', 'state': 'up'},
              {'interface': 'et-6/0/26', 'state': 'up'},
              {'interface': 'et-6/0/26.0', 'state': 'up'},
              {'interface': 'et-6/0/27', 'state': 'up'},
              {'interface': 'et-6/0/27.0', 'state': 'up'},
              {'interface': 'et-6/0/28', 'state': 'up'},
              {'interface': 'et-6/0/28.0', 'state': 'up'},
              {'interface': 'et-6/0/29', 'state': 'up'},
              {'interface': 'et-6/0/29.0', 'state': 'up'},
              {'interface': 'et-7/0/0', 'state': 'up'},
              {'interface': 'et-7/0/0.0', 'state': 'up'},
              {'interface': 'pfe-7/0/0', 'state': 'up'},
              {'interface': 'pfe-7/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-7/0/0', 'state': 'up'},
              {'interface': 'pfh-7/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-7/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-7/0/0', 'state': 'up'},
              {'interface': 'et-7/0/1', 'state': 'up'},
              {'interface': 'et-7/0/1.0', 'state': 'up'},
              {'interface': 'sxe-7/0/1', 'state': 'up'},
              {'interface': 'et-7/0/2', 'state': 'up'},
              {'interface': 'et-7/0/2.0', 'state': 'up'},
              {'interface': 'sxe-7/0/2', 'state': 'up'},
              {'interface': 'et-7/0/3', 'state': 'up'},
              {'interface': 'et-7/0/3.0', 'state': 'up'},
              {'interface': 'sxe-7/0/3', 'state': 'up'},
              {'interface': 'et-7/0/4', 'state': 'up'},
              {'interface': 'et-7/0/4.0', 'state': 'up'},
              {'interface': 'sxe-7/0/4', 'state': 'up'},
              {'interface': 'et-7/0/5', 'state': 'up'},
              {'interface': 'et-7/0/5.0', 'state': 'up'},
              {'interface': 'sxe-7/0/5', 'state': 'up'},
              {'interface': 'et-7/0/6', 'state': 'up'},
              {'interface': 'et-7/0/6.0', 'state': 'up'},
              {'interface': 'et-7/0/7', 'state': 'up'},
              {'interface': 'et-7/0/7.0', 'state': 'up'},
              {'interface': 'et-7/0/8', 'state': 'up'},
              {'interface': 'et-7/0/8.0', 'state': 'up'},
              {'interface': 'et-7/0/9', 'state': 'up'},
              {'interface': 'et-7/0/9.0', 'state': 'up'},
              {'interface': 'et-7/0/10', 'state': 'up'},
              {'interface': 'et-7/0/10.0', 'state': 'up'},
              {'interface': 'et-7/0/11', 'state': 'up'},
              {'interface': 'et-7/0/11.0', 'state': 'up'},
              {'interface': 'et-7/0/12', 'state': 'up'},
              {'interface': 'et-7/0/12.3000', 'state': 'up'},
              {'interface': 'et-7/0/12.32767', 'state': 'up'},
              {'interface': 'et-7/0/13', 'state': 'up'},
              {'interface': 'et-7/0/13.3000', 'state': 'up'},
              {'interface': 'et-7/0/13.32767', 'state': 'up'},
              {'interface': 'et-7/0/14', 'state': 'up'},
              {'interface': 'et-7/0/14.3000', 'state': 'up'},
              {'interface': 'et-7/0/14.32767', 'state': 'up'},
              {'interface': 'et-7/0/15', 'state': 'up'},
              {'interface': 'et-7/0/15.3000', 'state': 'up'},
              {'interface': 'et-7/0/15.32767', 'state': 'up'},
              {'interface': 'et-7/0/16', 'state': 'up'},
              {'interface': 'et-7/0/16.3000', 'state': 'up'},
              {'interface': 'et-7/0/16.32767', 'state': 'up'},
              {'interface': 'et-7/0/17', 'state': 'up'},
              {'interface': 'et-7/0/17.3000', 'state': 'up'},
              {'interface': 'et-7/0/17.32767', 'state': 'up'},
              {'interface': 'et-7/0/19', 'state': 'up'},
              {'interface': 'et-7/0/19.3000', 'state': 'up'},
              {'interface': 'et-7/0/19.3666', 'state': 'up'},
              {'interface': 'et-7/0/19.32767', 'state': 'up'},
              {'interface': 'et-7/0/20', 'state': 'down'},
              {'interface': 'et-7/0/21', 'state': 'up'},
              {'interface': 'et-7/0/22', 'state': 'up'},
              {'interface': 'et-7/0/22.3000', 'state': 'up'},
              {'interface': 'et-7/0/22.3666', 'state': 'up'},
              {'interface': 'et-7/0/22.32767', 'state': 'up'},
              {'interface': 'et-8/0/0', 'state': 'up'},
              {'interface': 'et-8/0/0.3000', 'state': 'up'},
              {'interface': 'et-8/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-8/0/0', 'state': 'up'},
              {'interface': 'pfe-8/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-8/0/0', 'state': 'up'},
              {'interface': 'pfh-8/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-8/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-8/0/0', 'state': 'up'},
              {'interface': 'et-8/0/1', 'state': 'up'},
              {'interface': 'et-8/0/1.3000', 'state': 'up'},
              {'interface': 'et-8/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/1', 'state': 'up'},
              {'interface': 'et-8/0/2', 'state': 'up'},
              {'interface': 'et-8/0/2.3000', 'state': 'up'},
              {'interface': 'et-8/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/2', 'state': 'up'},
              {'interface': 'et-8/0/3', 'state': 'up'},
              {'interface': 'et-8/0/3.3000', 'state': 'up'},
              {'interface': 'et-8/0/3.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/3', 'state': 'up'},
              {'interface': 'et-8/0/4', 'state': 'up'},
              {'interface': 'et-8/0/4.3000', 'state': 'up'},
              {'interface': 'et-8/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/4', 'state': 'up'},
              {'interface': 'et-8/0/5', 'state': 'up'},
              {'interface': 'et-8/0/5.3000', 'state': 'up'},
              {'interface': 'et-8/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-8/0/5', 'state': 'up'},
              {'interface': 'et-8/0/6', 'state': 'up'},
              {'interface': 'et-8/0/6.3000', 'state': 'up'},
              {'interface': 'et-8/0/6.32767', 'state': 'up'},
              {'interface': 'et-8/0/7', 'state': 'up'},
              {'interface': 'et-8/0/7.3000', 'state': 'up'},
              {'interface': 'et-8/0/7.32767', 'state': 'up'},
              {'interface': 'et-8/0/8', 'state': 'up'},
              {'interface': 'et-8/0/8.3000', 'state': 'up'},
              {'interface': 'et-8/0/8.32767', 'state': 'up'},
              {'interface': 'et-8/0/9', 'state': 'up'},
              {'interface': 'et-8/0/9.3000', 'state': 'up'},
              {'interface': 'et-8/0/9.32767', 'state': 'up'},
              {'interface': 'et-8/0/10', 'state': 'up'},
              {'interface': 'et-8/0/10.3000', 'state': 'up'},
              {'interface': 'et-8/0/10.32767', 'state': 'up'},
              {'interface': 'et-8/0/11', 'state': 'up'},
              {'interface': 'et-8/0/11.3000', 'state': 'up'},
              {'interface': 'et-8/0/11.32767', 'state': 'up'},
              {'interface': 'et-8/0/12', 'state': 'up'},
              {'interface': 'et-8/0/12.3000', 'state': 'up'},
              {'interface': 'et-8/0/12.32767', 'state': 'up'},
              {'interface': 'et-8/0/13', 'state': 'down'},
              {'interface': 'et-8/0/13.0', 'state': 'down'},
              {'interface': 'et-8/0/14', 'state': 'up'},
              {'interface': 'et-8/0/14.3000', 'state': 'up'},
              {'interface': 'et-8/0/14.32767', 'state': 'up'},
              {'interface': 'et-8/0/15', 'state': 'down'},
              {'interface': 'et-8/0/15.0', 'state': 'down'},
              {'interface': 'et-8/0/16', 'state': 'up'},
              {'interface': 'et-8/0/16.3000', 'state': 'up'},
              {'interface': 'et-8/0/16.32767', 'state': 'up'},
              {'interface': 'et-8/0/17', 'state': 'down'},
              {'interface': 'et-8/0/17.0', 'state': 'down'},
              {'interface': 'et-8/0/18', 'state': 'down'},
              {'interface': 'et-8/0/18.0', 'state': 'down'},
              {'interface': 'et-8/0/19', 'state': 'up'},
              {'interface': 'et-8/0/19.3000', 'state': 'up'},
              {'interface': 'et-8/0/19.32767', 'state': 'up'},
              {'interface': 'et-8/0/20', 'state': 'up'},
              {'interface': 'et-8/0/20.3000', 'state': 'up'},
              {'interface': 'et-8/0/20.32767', 'state': 'up'},
              {'interface': 'et-8/0/21', 'state': 'up'},
              {'interface': 'et-8/0/21.3000', 'state': 'up'},
              {'interface': 'et-8/0/21.32767', 'state': 'up'},
              {'interface': 'et-8/0/22', 'state': 'down'},
              {'interface': 'et-8/0/22.0', 'state': 'down'},
              {'interface': 'et-8/0/23', 'state': 'up'},
              {'interface': 'et-8/0/23.3000', 'state': 'up'},
              {'interface': 'et-8/0/23.32767', 'state': 'up'},
              {'interface': 'et-8/0/24', 'state': 'down'},
              {'interface': 'et-8/0/24.0', 'state': 'down'},
              {'interface': 'et-8/0/25', 'state': 'down'},
              {'interface': 'et-8/0/25.0', 'state': 'down'},
              {'interface': 'et-8/0/26', 'state': 'down'},
              {'interface': 'et-8/0/26.0', 'state': 'down'},
              {'interface': 'et-8/0/27', 'state': 'up'},
              {'interface': 'et-8/0/27.3000', 'state': 'up'},
              {'interface': 'et-8/0/27.32767', 'state': 'up'},
              {'interface': 'et-8/0/28', 'state': 'up'},
              {'interface': 'et-8/0/28.3000', 'state': 'up'},
              {'interface': 'et-8/0/28.32767', 'state': 'up'},
              {'interface': 'et-8/0/29', 'state': 'up'},
              {'interface': 'et-8/0/29.3000', 'state': 'up'},
              {'interface': 'et-8/0/29.32767', 'state': 'up'},
              {'interface': 'et-9/0/0', 'state': 'up'},
              {'interface': 'et-9/0/0.3000', 'state': 'up'},
              {'interface': 'et-9/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-9/0/0', 'state': 'up'},
              {'interface': 'pfe-9/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-9/0/0', 'state': 'up'},
              {'interface': 'pfh-9/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-9/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-9/0/0', 'state': 'up'},
              {'interface': 'et-9/0/1', 'state': 'up'},
              {'interface': 'et-9/0/1.3000', 'state': 'up'},
              {'interface': 'et-9/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/1', 'state': 'up'},
              {'interface': 'et-9/0/2', 'state': 'up'},
              {'interface': 'et-9/0/2.3000', 'state': 'up'},
              {'interface': 'et-9/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/2', 'state': 'up'},
              {'interface': 'et-9/0/3', 'state': 'down'},
              {'interface': 'et-9/0/3.0', 'state': 'down'},
              {'interface': 'sxe-9/0/3', 'state': 'up'},
              {'interface': 'et-9/0/4', 'state': 'up'},
              {'interface': 'et-9/0/4.3000', 'state': 'up'},
              {'interface': 'et-9/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/4', 'state': 'up'},
              {'interface': 'et-9/0/5', 'state': 'up'},
              {'interface': 'et-9/0/5.3000', 'state': 'up'},
              {'interface': 'et-9/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-9/0/5', 'state': 'up'},
              {'interface': 'et-9/0/6', 'state': 'up'},
              {'interface': 'et-9/0/6.3000', 'state': 'up'},
              {'interface': 'et-9/0/6.32767', 'state': 'up'},
              {'interface': 'et-9/0/7', 'state': 'down'},
              {'interface': 'et-9/0/7.0', 'state': 'down'},
              {'interface': 'et-9/0/8', 'state': 'up'},
              {'interface': 'et-9/0/8.3000', 'state': 'up'},
              {'interface': 'et-9/0/8.32767', 'state': 'up'},
              {'interface': 'et-9/0/9', 'state': 'up'},
              {'interface': 'et-9/0/9.3000', 'state': 'up'},
              {'interface': 'et-9/0/9.32767', 'state': 'up'},
              {'interface': 'et-9/0/10', 'state': 'up'},
              {'interface': 'et-9/0/10.3000', 'state': 'up'},
              {'interface': 'et-9/0/10.32767', 'state': 'up'},
              {'interface': 'et-9/0/11', 'state': 'up'},
              {'interface': 'et-9/0/11.3000', 'state': 'up'},
              {'interface': 'et-9/0/11.32767', 'state': 'up'},
              {'interface': 'et-9/0/12', 'state': 'up'},
              {'interface': 'et-9/0/12.3000', 'state': 'up'},
              {'interface': 'et-9/0/12.32767', 'state': 'up'},
              {'interface': 'et-9/0/13', 'state': 'up'},
              {'interface': 'et-9/0/13.3000', 'state': 'up'},
              {'interface': 'et-9/0/13.32767', 'state': 'up'},
              {'interface': 'et-9/0/14', 'state': 'down'},
              {'interface': 'et-9/0/14.0', 'state': 'down'},
              {'interface': 'et-9/0/15', 'state': 'down'},
              {'interface': 'et-9/0/15.0', 'state': 'down'},
              {'interface': 'et-9/0/16', 'state': 'up'},
              {'interface': 'et-9/0/16.3000', 'state': 'up'},
              {'interface': 'et-9/0/16.32767', 'state': 'up'},
              {'interface': 'et-9/0/17', 'state': 'up'},
              {'interface': 'et-9/0/17.3000', 'state': 'up'},
              {'interface': 'et-9/0/17.32767', 'state': 'up'},
              {'interface': 'et-9/0/18', 'state': 'up'},
              {'interface': 'et-9/0/18.3000', 'state': 'up'},
              {'interface': 'et-9/0/18.32767', 'state': 'up'},
              {'interface': 'et-9/0/19', 'state': 'up'},
              {'interface': 'et-9/0/19.3000', 'state': 'up'},
              {'interface': 'et-9/0/19.32767', 'state': 'up'},
              {'interface': 'et-9/0/20', 'state': 'up'},
              {'interface': 'et-9/0/20.3000', 'state': 'up'},
              {'interface': 'et-9/0/20.32767', 'state': 'up'},
              {'interface': 'et-9/0/21', 'state': 'down'},
              {'interface': 'et-9/0/21.0', 'state': 'down'},
              {'interface': 'et-9/0/22', 'state': 'up'},
              {'interface': 'et-9/0/22.3000', 'state': 'up'},
              {'interface': 'et-9/0/22.32767', 'state': 'up'},
              {'interface': 'et-9/0/23', 'state': 'up'},
              {'interface': 'et-9/0/23.3000', 'state': 'up'},
              {'interface': 'et-9/0/23.32767', 'state': 'up'},
              {'interface': 'et-9/0/24', 'state': 'up'},
              {'interface': 'et-9/0/24.3000', 'state': 'up'},
              {'interface': 'et-9/0/24.32767', 'state': 'up'},
              {'interface': 'et-9/0/25', 'state': 'down'},
              {'interface': 'et-9/0/25.0', 'state': 'down'},
              {'interface': 'et-9/0/26', 'state': 'up'},
              {'interface': 'et-9/0/26.3000', 'state': 'up'},
              {'interface': 'et-9/0/26.32767', 'state': 'up'},
              {'interface': 'et-9/0/27', 'state': 'up'},
              {'interface': 'et-9/0/27.3000', 'state': 'up'},
              {'interface': 'et-9/0/27.32767', 'state': 'up'},
              {'interface': 'et-9/0/28', 'state': 'up'},
              {'interface': 'et-9/0/28.3000', 'state': 'up'},
              {'interface': 'et-9/0/28.32767', 'state': 'up'},
              {'interface': 'et-9/0/29', 'state': 'down'},
              {'interface': 'et-9/0/29.0', 'state': 'down'},
              {'interface': 'et-10/0/0', 'state': 'up'},
              {'interface': 'et-10/0/0.3000', 'state': 'up'},
              {'interface': 'et-10/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-10/0/0', 'state': 'up'},
              {'interface': 'pfe-10/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-10/0/0', 'state': 'up'},
              {'interface': 'pfh-10/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-10/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-10/0/0', 'state': 'up'},
              {'interface': 'et-10/0/1', 'state': 'up'},
              {'interface': 'et-10/0/1.3000', 'state': 'up'},
              {'interface': 'et-10/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/1', 'state': 'up'},
              {'interface': 'et-10/0/2', 'state': 'up'},
              {'interface': 'et-10/0/2.3000', 'state': 'up'},
              {'interface': 'et-10/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/2', 'state': 'up'},
              {'interface': 'et-10/0/3', 'state': 'up'},
              {'interface': 'et-10/0/3.3000', 'state': 'up'},
              {'interface': 'et-10/0/3.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/3', 'state': 'up'},
              {'interface': 'et-10/0/4', 'state': 'up'},
              {'interface': 'et-10/0/4.3000', 'state': 'up'},
              {'interface': 'et-10/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/4', 'state': 'up'},
              {'interface': 'et-10/0/5', 'state': 'up'},
              {'interface': 'et-10/0/5.3000', 'state': 'up'},
              {'interface': 'et-10/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-10/0/5', 'state': 'up'},
              {'interface': 'et-10/0/6', 'state': 'up'},
              {'interface': 'et-10/0/6.3000', 'state': 'up'},
              {'interface': 'et-10/0/6.32767', 'state': 'up'},
              {'interface': 'et-10/0/7', 'state': 'up'},
              {'interface': 'et-10/0/7.3000', 'state': 'up'},
              {'interface': 'et-10/0/7.32767', 'state': 'up'},
              {'interface': 'et-10/0/8', 'state': 'up'},
              {'interface': 'et-10/0/8.3000', 'state': 'up'},
              {'interface': 'et-10/0/8.32767', 'state': 'up'},
              {'interface': 'et-10/0/9', 'state': 'up'},
              {'interface': 'et-10/0/9.3000', 'state': 'up'},
              {'interface': 'et-10/0/9.32767', 'state': 'up'},
              {'interface': 'et-10/0/10', 'state': 'up'},
              {'interface': 'et-10/0/10.3000', 'state': 'up'},
              {'interface': 'et-10/0/10.32767', 'state': 'up'},
              {'interface': 'et-10/0/11', 'state': 'up'},
              {'interface': 'et-10/0/11.3000', 'state': 'up'},
              {'interface': 'et-10/0/11.32767', 'state': 'up'},
              {'interface': 'et-10/0/12', 'state': 'down'},
              {'interface': 'et-10/0/12.0', 'state': 'down'},
              {'interface': 'et-10/0/13', 'state': 'down'},
              {'interface': 'et-10/0/13.0', 'state': 'down'},
              {'interface': 'et-10/0/18', 'state': 'up'},
              {'interface': 'et-10/0/18.3000', 'state': 'up'},
              {'interface': 'et-10/0/18.32767', 'state': 'up'},
              {'interface': 'et-10/0/19', 'state': 'down'},
              {'interface': 'et-10/0/19.0', 'state': 'down'},
              {'interface': 'et-10/0/20', 'state': 'up'},
              {'interface': 'et-10/0/20.3000', 'state': 'up'},
              {'interface': 'et-10/0/20.32767', 'state': 'up'},
              {'interface': 'et-10/0/21', 'state': 'up'},
              {'interface': 'et-10/0/21.3000', 'state': 'up'},
              {'interface': 'et-10/0/21.32767', 'state': 'up'},
              {'interface': 'et-10/0/22', 'state': 'up'},
              {'interface': 'et-10/0/22.3000', 'state': 'up'},
              {'interface': 'et-10/0/22.32767', 'state': 'up'},
              {'interface': 'et-10/0/23', 'state': 'down'},
              {'interface': 'et-10/0/23.0', 'state': 'down'},
              {'interface': 'et-10/0/24', 'state': 'down'},
              {'interface': 'et-10/0/24.0', 'state': 'down'},
              {'interface': 'et-10/0/25', 'state': 'up'},
              {'interface': 'et-10/0/25.3000', 'state': 'up'},
              {'interface': 'et-10/0/25.32767', 'state': 'up'},
              {'interface': 'et-10/0/26', 'state': 'up'},
              {'interface': 'et-10/0/26.3000', 'state': 'up'},
              {'interface': 'et-10/0/26.32767', 'state': 'up'},
              {'interface': 'et-10/0/27', 'state': 'up'},
              {'interface': 'et-10/0/27.3000', 'state': 'up'},
              {'interface': 'et-10/0/27.32767', 'state': 'up'},
              {'interface': 'et-10/0/28', 'state': 'up'},
              {'interface': 'et-10/0/28.3000', 'state': 'up'},
              {'interface': 'et-10/0/28.32767', 'state': 'up'},
              {'interface': 'et-10/0/29', 'state': 'up'},
              {'interface': 'et-10/0/29.3000', 'state': 'up'},
              {'interface': 'et-10/0/29.32767', 'state': 'up'},
              {'interface': 'et-11/0/0', 'state': 'up'},
              {'interface': 'et-11/0/0.3000', 'state': 'up'},
              {'interface': 'et-11/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-11/0/0', 'state': 'up'},
              {'interface': 'pfe-11/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-11/0/0', 'state': 'up'},
              {'interface': 'pfh-11/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-11/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-11/0/0', 'state': 'up'},
              {'interface': 'et-11/0/1', 'state': 'down'},
              {'interface': 'et-11/0/1.0', 'state': 'down'},
              {'interface': 'sxe-11/0/1', 'state': 'up'},
              {'interface': 'et-11/0/2', 'state': 'up'},
              {'interface': 'et-11/0/2.3000', 'state': 'up'},
              {'interface': 'et-11/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-11/0/2', 'state': 'up'},
              {'interface': 'et-11/0/3', 'state': 'down'},
              {'interface': 'et-11/0/3.0', 'state': 'down'},
              {'interface': 'sxe-11/0/3', 'state': 'up'},
              {'interface': 'et-11/0/4', 'state': 'up'},
              {'interface': 'et-11/0/4.3000', 'state': 'up'},
              {'interface': 'et-11/0/4.32767', 'state': 'up'},
              {'interface': 'sxe-11/0/4', 'state': 'up'},
              {'interface': 'et-11/0/5', 'state': 'up'},
              {'interface': 'et-11/0/5.3000', 'state': 'up'},
              {'interface': 'et-11/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-11/0/5', 'state': 'up'},
              {'interface': 'et-11/0/6', 'state': 'up'},
              {'interface': 'et-11/0/6.3000', 'state': 'up'},
              {'interface': 'et-11/0/6.32767', 'state': 'up'},
              {'interface': 'et-11/0/7', 'state': 'up'},
              {'interface': 'et-11/0/7.3000', 'state': 'up'},
              {'interface': 'et-11/0/7.32767', 'state': 'up'},
              {'interface': 'et-11/0/8', 'state': 'up'},
              {'interface': 'et-11/0/8.3000', 'state': 'up'},
              {'interface': 'et-11/0/8.32767', 'state': 'up'},
              {'interface': 'et-11/0/9', 'state': 'up'},
              {'interface': 'et-11/0/9.3000', 'state': 'up'},
              {'interface': 'et-11/0/9.32767', 'state': 'up'},
              {'interface': 'et-11/0/10', 'state': 'up'},
              {'interface': 'et-11/0/10.3000', 'state': 'up'},
              {'interface': 'et-11/0/10.32767', 'state': 'up'},
              {'interface': 'et-11/0/11', 'state': 'up'},
              {'interface': 'et-11/0/11.3000', 'state': 'up'},
              {'interface': 'et-11/0/11.32767', 'state': 'up'},
              {'interface': 'et-11/0/12', 'state': 'down'},
              {'interface': 'et-11/0/12.0', 'state': 'down'},
              {'interface': 'et-11/0/13', 'state': 'down'},
              {'interface': 'et-11/0/13.0', 'state': 'down'},
              {'interface': 'et-11/0/14', 'state': 'up'},
              {'interface': 'et-11/0/14.3000', 'state': 'up'},
              {'interface': 'et-11/0/14.32767', 'state': 'up'},
              {'interface': 'et-11/0/15', 'state': 'up'},
              {'interface': 'et-11/0/15.3000', 'state': 'up'},
              {'interface': 'et-11/0/15.32767', 'state': 'up'},
              {'interface': 'et-11/0/16', 'state': 'up'},
              {'interface': 'et-11/0/16.3000', 'state': 'up'},
              {'interface': 'et-11/0/16.32767', 'state': 'up'},
              {'interface': 'et-11/0/17', 'state': 'down'},
              {'interface': 'et-11/0/17.0', 'state': 'down'},
              {'interface': 'et-11/0/18', 'state': 'up'},
              {'interface': 'et-11/0/18.3000', 'state': 'up'},
              {'interface': 'et-11/0/18.32767', 'state': 'up'},
              {'interface': 'et-11/0/19', 'state': 'up'},
              {'interface': 'et-11/0/19.3000', 'state': 'up'},
              {'interface': 'et-11/0/19.32767', 'state': 'up'},
              {'interface': 'et-11/0/20', 'state': 'up'},
              {'interface': 'et-11/0/20.3000', 'state': 'up'},
              {'interface': 'et-11/0/20.32767', 'state': 'up'},
              {'interface': 'et-11/0/21', 'state': 'up'},
              {'interface': 'et-11/0/21.3000', 'state': 'up'},
              {'interface': 'et-11/0/21.32767', 'state': 'up'},
              {'interface': 'et-11/0/22', 'state': 'up'},
              {'interface': 'et-11/0/22.3000', 'state': 'up'},
              {'interface': 'et-11/0/22.32767', 'state': 'up'},
              {'interface': 'et-11/0/23', 'state': 'up'},
              {'interface': 'et-11/0/23.3000', 'state': 'up'},
              {'interface': 'et-11/0/23.32767', 'state': 'up'},
              {'interface': 'et-11/0/24', 'state': 'up'},
              {'interface': 'et-11/0/24.3000', 'state': 'up'},
              {'interface': 'et-11/0/24.32767', 'state': 'up'},
              {'interface': 'et-11/0/25', 'state': 'down'},
              {'interface': 'et-11/0/25.0', 'state': 'down'},
              {'interface': 'et-11/0/26', 'state': 'up'},
              {'interface': 'et-11/0/26.3000', 'state': 'up'},
              {'interface': 'et-11/0/26.32767', 'state': 'up'},
              {'interface': 'et-11/0/27', 'state': 'up'},
              {'interface': 'et-11/0/27.3000', 'state': 'up'},
              {'interface': 'et-11/0/27.32767', 'state': 'up'},
              {'interface': 'et-11/0/28', 'state': 'up'},
              {'interface': 'et-11/0/28.3000', 'state': 'up'},
              {'interface': 'et-11/0/28.32767', 'state': 'up'},
              {'interface': 'et-11/0/29', 'state': 'down'},
              {'interface': 'et-11/0/29.3000', 'state': 'down'},
              {'interface': 'et-11/0/29.32767', 'state': 'down'},
              {'interface': 'et-12/0/0', 'state': 'up'},
              {'interface': 'et-12/0/0.3000', 'state': 'up'},
              {'interface': 'et-12/0/0.32767', 'state': 'up'},
              {'interface': 'pfe-12/0/0', 'state': 'up'},
              {'interface': 'pfe-12/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-12/0/0', 'state': 'up'},
              {'interface': 'pfh-12/0/0.16383', 'state': 'up'},
              {'interface': 'pfh-12/0/0.16384', 'state': 'up'},
              {'interface': 'sxe-12/0/0', 'state': 'up'},
              {'interface': 'et-12/0/1', 'state': 'up'},
              {'interface': 'et-12/0/1.3000', 'state': 'up'},
              {'interface': 'et-12/0/1.32767', 'state': 'up'},
              {'interface': 'sxe-12/0/1', 'state': 'up'},
              {'interface': 'et-12/0/2', 'state': 'up'},
              {'interface': 'et-12/0/2.3000', 'state': 'up'},
              {'interface': 'et-12/0/2.32767', 'state': 'up'},
              {'interface': 'sxe-12/0/2', 'state': 'up'},
              {'interface': 'et-12/0/3', 'state': 'down'},
              {'interface': 'et-12/0/3.0', 'state': 'down'},
              {'interface': 'sxe-12/0/3', 'state': 'up'},
              {'interface': 'et-12/0/4', 'state': 'down'},
              {'interface': 'et-12/0/4.0', 'state': 'down'},
              {'interface': 'sxe-12/0/4', 'state': 'up'},
              {'interface': 'et-12/0/5', 'state': 'up'},
              {'interface': 'et-12/0/5.3000', 'state': 'up'},
              {'interface': 'et-12/0/5.32767', 'state': 'up'},
              {'interface': 'sxe-12/0/5', 'state': 'up'},
              {'interface': 'et-12/0/6', 'state': 'down'},
              {'interface': 'et-12/0/6.0', 'state': 'down'},
              {'interface': 'et-12/0/7', 'state': 'down'},
              {'interface': 'et-12/0/7.0', 'state': 'down'},
              {'interface': 'et-12/0/8', 'state': 'up'},
              {'interface': 'et-12/0/8.3000', 'state': 'up'},
              {'interface': 'et-12/0/8.32767', 'state': 'up'},
              {'interface': 'et-12/0/9', 'state': 'up'},
              {'interface': 'et-12/0/9.3000', 'state': 'up'},
              {'interface': 'et-12/0/9.32767', 'state': 'up'},
              {'interface': 'et-12/0/10', 'state': 'up'},
              {'interface': 'et-12/0/10.3000', 'state': 'up'},
              {'interface': 'et-12/0/10.32767', 'state': 'up'},
              {'interface': 'et-12/0/11', 'state': 'up'},
              {'interface': 'et-12/0/11.3000', 'state': 'up'},
              {'interface': 'et-12/0/11.32767', 'state': 'up'},
              {'interface': 'et-12/0/13', 'state': 'up'},
              {'interface': 'et-12/0/13.3000', 'state': 'up'},
              {'interface': 'et-12/0/13.3666', 'state': 'up'},
              {'interface': 'et-12/0/13.32767', 'state': 'up'},
              {'interface': 'et-12/0/15', 'state': 'up'},
              {'interface': 'et-12/0/15.3000', 'state': 'up'},
              {'interface': 'et-12/0/15.3666', 'state': 'up'},
              {'interface': 'et-12/0/15.32767', 'state': 'up'},
              {'interface': 'et-12/0/18', 'state': 'up'},
              {'interface': 'et-12/0/18.3000', 'state': 'up'},
              {'interface': 'et-12/0/18.32767', 'state': 'up'},
              {'interface': 'et-12/0/19', 'state': 'up'},
              {'interface': 'et-12/0/19.3000', 'state': 'up'},
              {'interface': 'et-12/0/19.32767', 'state': 'up'},
              {'interface': 'et-12/0/20', 'state': 'up'},
              {'interface': 'et-12/0/20.3000', 'state': 'up'},
              {'interface': 'et-12/0/20.32767', 'state': 'up'},
              {'interface': 'et-12/0/21', 'state': 'up'},
              {'interface': 'et-12/0/21.3000', 'state': 'up'},
              {'interface': 'et-12/0/21.32767', 'state': 'up'},
              {'interface': 'et-12/0/22', 'state': 'up'},
              {'interface': 'et-12/0/22.3000', 'state': 'up'},
              {'interface': 'et-12/0/22.32767', 'state': 'up'},
              {'interface': 'et-12/0/23', 'state': 'up'},
              {'interface': 'et-12/0/23.3000', 'state': 'up'},
              {'interface': 'et-12/0/23.32767', 'state': 'up'},
              {'interface': 'et-12/0/24', 'state': 'up'},
              {'interface': 'et-12/0/24.3000', 'state': 'up'},
              {'interface': 'et-12/0/24.32767', 'state': 'up'},
              {'interface': 'et-12/0/25', 'state': 'up'},
              {'interface': 'et-12/0/25.3000', 'state': 'up'},
              {'interface': 'et-12/0/25.32767', 'state': 'up'},
              {'interface': 'et-12/0/26', 'state': 'up'},
              {'interface': 'et-12/0/26.3000', 'state': 'up'},
              {'interface': 'et-12/0/26.32767', 'state': 'up'},
              {'interface': 'et-12/0/27', 'state': 'up'},
              {'interface': 'et-12/0/27.3000', 'state': 'up'},
              {'interface': 'et-12/0/27.32767', 'state': 'up'},
              {'interface': 'et-12/0/28', 'state': 'up'},
              {'interface': 'et-12/0/28.3000', 'state': 'up'},
              {'interface': 'et-12/0/28.32767', 'state': 'up'},
              {'interface': 'et-12/0/29', 'state': 'up'},
              {'interface': 'et-12/0/29.3000', 'state': 'up'},
              {'interface': 'et-12/0/29.32767', 'state': 'up'},
              {'interface': 'ae1', 'state': 'up'},
              {'interface': 'ae1.0', 'state': 'up'},
              {'interface': 'ae3', 'state': 'up'},
              {'interface': 'ae3.0', 'state': 'up'},
              {'interface': 'ae5', 'state': 'up'},
              {'interface': 'ae5.0', 'state': 'up'},
              {'interface': 'ae7', 'state': 'up'},
              {'interface': 'ae7.0', 'state': 'up'},
              {'interface': 'ae101', 'state': 'up'},
              {'interface': 'ae101.3000', 'state': 'up'},
              {'interface': 'ae101.3666', 'state': 'up'},
              {'interface': 'ae101.32767', 'state': 'up'},
              {'interface': 'ae102', 'state': 'up'},
              {'interface': 'ae102.3000', 'state': 'up'},
              {'interface': 'ae102.3666', 'state': 'up'},
              {'interface': 'ae102.32767', 'state': 'up'},
              {'interface': 'bme0', 'state': 'up'},
              {'interface': 'bme0.0', 'state': 'up'},
              {'interface': 'bme1', 'state': 'up'},
              {'interface': 'bme1.0', 'state': 'up'},
              {'interface': 'bme2', 'state': 'up'},
              {'interface': 'bme2.0', 'state': 'up'},
              {'interface': 'cbp0', 'state': 'up'},
              {'interface': 'dsc', 'state': 'up'},
              {'interface': 'em0', 'state': 'up'},
              {'interface': 'em0.0', 'state': 'up'},
              {'interface': 'em1', 'state': 'down'},
              {'interface': 'em2', 'state': 'up'},
              {'interface': 'em2.32768', 'state': 'up'},
              {'interface': 'esi', 'state': 'up'},
              {'interface': 'gre', 'state': 'up'},
              {'interface': 'ipip', 'state': 'up'},
              {'interface': 'irb', 'state': 'up'},
              {'interface': 'jsrv', 'state': 'up'},
              {'interface': 'jsrv.1', 'state': 'up'},
              {'interface': 'lo0', 'state': 'up'},
              {'interface': 'lo0.0', 'state': 'up'},
              {'interface': 'lo0.16385', 'state': 'up'},
              {'interface': 'lsi', 'state': 'up'},
              {'interface': 'lsi.0', 'state': 'up'},
              {'interface': 'mtun', 'state': 'up'},
              {'interface': 'pimd', 'state': 'up'},
              {'interface': 'pime', 'state': 'up'},
              {'interface': 'pip0', 'state': 'up'},
              {'interface': 'tap', 'state': 'up'},
              {'interface': 'vtep', 'state': 'up'}]
