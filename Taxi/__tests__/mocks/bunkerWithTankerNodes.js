// Ноды с переводами из бункера
module.exports = {
    tanker1: {
        'keysets': {
            'testkeyset1': {
                'keys': {
                    'driving': {
                        'info': {
                            'context': '',
                            'is_plural': true,
                            'references': ''
                        },
                        'translations': {
                            'ru': {
                                'status': 'approved',
                                'form1': 'Водитель приедет через %time%&nbsp;минуту',
                                'form2': 'Водитель приедет через %time%&nbsp;минуты',
                                'form3': 'Водитель приедет через %time%&nbsp;минут'
                            },
                            'en': {
                                'status': 'approved',
                                'form1': '',
                                'form2': ''
                            },
                            'tw': {
                                'status': 'approved',
                                'form1': '',
                                'form2': ''
                            }
                        }
                    },
                    'copyright': {
                        'info': {
                            'context': 'copyright',
                            'is_plural': false,
                            'references': ''
                        },
                        'translations': {
                            'ru': {
                                'status': 'approved',
                                'form': 'Убер'
                            },
                            'en': {
                                'status': 'approved',
                                'form': 'Uber'
                            },
                            'tw': {
                                'status': 'approved',
                                'form': ''
                            }
                        }
                    }
                },
                'meta': {
                    'languages': [
                        'ru',
                        'en',
                        'tw'
                    ]
                }
            },
            'meta': {
                'languages': [
                    'ru',
                    'en',
                    'tw'
                ]
            }
        }
    },
    tanker2: {
        'keysets': {
            'testkeyset2': {
                'keys': {
                    'user': {
                        'info': {
                            'context': '',
                            'is_plural': false,
                            'references': ''
                        },
                        'translations': {
                            'ru': {
                                'status': 'approved',
                                'form': 'Водитель приедет через %time%&nbsp;минуту'
                            },
                            'en': {
                                'status': 'approved',
                                'form': ''
                            },
                            'tw': {
                                'status': 'approved',
                                'form': ''
                            }
                        }
                    }
                }
            },
            'meta': {
                'languages': [
                    'ru',
                    'en',
                    'tw'
                ]
            }
        }
    }
};
