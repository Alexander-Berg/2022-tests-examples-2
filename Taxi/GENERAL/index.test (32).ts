/* eslint-disable @typescript-eslint/no-explicit-any */
import {StructError} from 'superstruct';
import {describe, expect, it} from 'tests/jest.globals';

import {
    DisallowedAttributeValueLineBreaks,
    ForbidReservedCharacter,
    InvalidArrayAttributeValue,
    InvalidLocalizableAttributeValue,
    InvalidMultipleAttributeValueMaxSize,
    InvalidNumberIsIntegerAttributeValue,
    InvalidNumberIsNonNegativeAttributeValue,
    InvalidNumberMaxAttributeValue,
    InvalidNumberMinAttributeValue,
    InvalidRequiredAttributeValue,
    InvalidSelectOptionAttributeValue,
    InvalidStringMaxAttributeValue,
    InvalidStringMinAttributeValue
} from '@/src/errors';
import {AttributeValue} from 'service/attribute-value/index';
import {
    AttributeType,
    BooleanAttribute,
    ImageAttribute,
    MultiselectAttribute,
    NumberAttribute,
    SelectAttribute,
    StringAttribute,
    TextAttribute
} from 'types/attribute';

describe('attribute value: value struct', () => {
    it('should check "BOOLEAN" struct', async () => {
        const attribute: BooleanAttribute = {
            type: AttributeType.BOOLEAN,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo' as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: true
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should check "NUMBER" struct', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo' as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 20
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should check "IMAGE" struct', async () => {
        const attribute: ImageAttribute = {
            type: AttributeType.IMAGE,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ''
                })
        ).toThrow(StructError);

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 92 as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should check "STRING" struct', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 28 as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should check "TEXT" struct', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 11 as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should check "SELECT" struct', async () => {
        const attribute: SelectAttribute = {
            type: AttributeType.SELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [{code: 'foo', translations: {}}]
            }
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 32 as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should check "MULTISELECT" struct', async () => {
        const attribute: MultiselectAttribute = {
            type: AttributeType.MULTISELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [{code: 'foo', translations: {}}]
            }
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo' as never
                })
        ).toThrow(StructError);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['foo']
            })
        ).toBeInstanceOf(AttributeValue);
    });
});

describe('attribute value: "isArray" property', () => {
    it('should throw error on invalid "BOOLEAN::isArray"', async () => {
        const attribute: BooleanAttribute = {
            type: AttributeType.BOOLEAN,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [true, false]
                })
        ).toThrow(InvalidArrayAttributeValue);
    });

    it('should throw error on invalid "NUMBER::isArray"', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [1, 2]
                })
        ).toThrow(InvalidArrayAttributeValue);
    });

    it('should throw error on invalid "IMAGE::isArray"', async () => {
        const attribute: ImageAttribute = {
            type: AttributeType.IMAGE,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['/url-a', '/url-b']
                })
        ).toThrow(InvalidArrayAttributeValue);
    });

    it('should throw error on invalid "STRING::isArray"', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['foo', 'bar']
                })
        ).toThrow(InvalidArrayAttributeValue);
    });

    it('should throw error on invalid "TEXT::isArray"', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['foo', 'bar']
                })
        ).toThrow(InvalidArrayAttributeValue);
    });

    describe('should throw error on forbidden character cases', () => {
        it('StringAttribute', async () => {
            const attribute: StringAttribute = {
                type: AttributeType.STRING,
                isValueLocalizable: false,
                isArray: true,
                properties: {}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo;baz', 'bar']
                    })
            ).toThrow(ForbidReservedCharacter);
        });

        it('TextAttribute', async () => {
            const attribute: TextAttribute = {
                type: AttributeType.TEXT,
                isValueLocalizable: false,
                isArray: true,
                properties: {}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo;baz', 'bar']
                    })
            ).toThrow(ForbidReservedCharacter);
        });
    });
});

describe('attribute value: "isValueLocalizable" property', () => {
    it('should throw error on invalid "STRING::isValueLocalizable"', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['bar']}
                })
        ).toThrow(InvalidLocalizableAttributeValue);

        attribute.isValueLocalizable = true;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['bar']
                })
        ).toThrow(InvalidLocalizableAttributeValue);
    });

    it('should throw error on invalid "TEXT::isValueLocalizable"', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['bar']}
                })
        ).toThrow(InvalidLocalizableAttributeValue);

        attribute.isValueLocalizable = true;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['bar']
                })
        ).toThrow(InvalidLocalizableAttributeValue);
    });
});

describe('attribute value: "isValueRequired" property', () => {
    it('should throw error on invalid "BOOLEAN::isValueRequired"', async () => {
        const attribute: BooleanAttribute = {
            type: AttributeType.BOOLEAN,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: null
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });

    it('should throw error on invalid "NUMBER::isValueRequired"', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: null
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });

    it('should throw error on invalid "IMAGE::isValueRequired"', async () => {
        const attribute: ImageAttribute = {
            type: AttributeType.IMAGE,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: null
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });

    it('should throw error on invalid "STRING::isValueRequired"', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: null
                })
        ).toThrow(InvalidRequiredAttributeValue);

        attribute.isValueLocalizable = true;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {
                        ru: null,
                        en: 'bar'
                    }
                })
        ).toThrow(InvalidRequiredAttributeValue);

        attribute.isArray = true;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {
                        ru: [],
                        en: ['bar']
                    }
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });

    it('should throw error on invalid "TEXT::isValueRequired"', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: null
                })
        ).toThrow(InvalidRequiredAttributeValue);

        attribute.isValueLocalizable = true;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {
                        ru: null,
                        en: 'bar'
                    }
                })
        ).toThrow(InvalidRequiredAttributeValue);

        attribute.isArray = true;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {
                        ru: [],
                        en: ['bar']
                    }
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });

    it('should throw error on invalid "SELECT::isValueRequired"', async () => {
        const attribute: SelectAttribute = {
            type: AttributeType.SELECT,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {options: [{code: 'foo', translations: {}}]}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: null
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });

    it('should throw error on invalid "MULTISELECT::isValueRequired"', async () => {
        const attribute: MultiselectAttribute = {
            type: AttributeType.MULTISELECT,
            isValueLocalizable: false,
            isValueRequired: true,
            isArray: false,
            properties: {options: [{code: 'foo', translations: {}}]}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: []
                })
        ).toThrow(InvalidRequiredAttributeValue);
    });
});

describe('attribute value: string-like line breaks', () => {
    it('should throw error on invalid "IMAGE" line breaks', async () => {
        const attribute: ImageAttribute = {
            type: AttributeType.IMAGE,
            isValueLocalizable: false,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo\n'
                })
        ).toThrow(DisallowedAttributeValueLineBreaks);
    });

    it('should throw error on invalid "STRING" line breaks', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: false,
            properties: {}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'foo\n'}
                })
        ).toThrow(DisallowedAttributeValueLineBreaks);

        attribute.isValueLocalizable = false;
        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo\n'
                })
        ).toThrow(DisallowedAttributeValueLineBreaks);
    });

    it('should throw error on invalid "SELECT" line breaks', async () => {
        const attribute: SelectAttribute = {
            type: AttributeType.SELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [{code: 'foo\n', translations: {}}]
            }
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo\n'
                })
        ).toThrow(DisallowedAttributeValueLineBreaks);
    });

    it('should throw error on invalid "MULTISELECT" line breaks', async () => {
        const attribute: MultiselectAttribute = {
            type: AttributeType.MULTISELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [{code: 'foo\r', translations: {}}]
            }
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['foo\r']
                })
        ).toThrow(DisallowedAttributeValueLineBreaks);
    });
});

describe('attribute value: select options', () => {
    it('should throw error on invalid "SELECT" options', async () => {
        const attribute: SelectAttribute = {
            type: AttributeType.SELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [{code: 'foo', translations: {}}]
            }
        };

        let error = null;
        try {
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'bar'
            });
        } catch (err) {
            error = err;
        }

        expect(error).toMatchObject(new InvalidSelectOptionAttributeValue({value: 'bar'}).toFlatArray()[0]);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should throw error on invalid "MULTISELECT" options', async () => {
        const attribute: MultiselectAttribute = {
            type: AttributeType.MULTISELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [{code: 'foo', translations: {}}]
            }
        };

        let error = null;
        try {
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['bar']
            });
        } catch (err) {
            error = err;
        }

        expect(error).toMatchObject(new InvalidSelectOptionAttributeValue({value: 'bar'}).toFlatArray()[0]);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['foo']
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should throw error on non-unique "MULTISELECT" values', async () => {
        const attribute: MultiselectAttribute = {
            type: AttributeType.MULTISELECT,
            isValueLocalizable: false,
            isArray: false,
            properties: {
                options: [
                    {code: 'foo', translations: {}},
                    {code: 'baz', translations: {}},
                    {code: 'bar', translations: {}}
                ]
            }
        };

        let error = null;
        try {
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['foo', 'foo']
            });
        } catch (err) {
            error = err;
        }

        expect(error).toMatchObject(new InvalidSelectOptionAttributeValue({value: 'foo,foo'}).toFlatArray()[0]);
    });

    it('should return null db value if it is empty array', async () => {
        const attributes = [
            {
                type: AttributeType.MULTISELECT,
                isValueLocalizable: false,
                isArray: false,
                properties: {
                    options: [{code: 'foo', translations: {}}]
                }
            },
            {
                type: AttributeType.TEXT,
                isValueLocalizable: false,
                isArray: true,
                properties: {}
            },
            {
                type: AttributeType.STRING,
                isValueLocalizable: false,
                isArray: true,
                properties: {}
            },
            {
                type: AttributeType.BOOLEAN,
                isValueLocalizable: false,
                isArray: true,
                properties: {}
            },
            {
                type: AttributeType.NUMBER,
                isValueLocalizable: false,
                isArray: true,
                properties: {}
            }
        ];

        for (const attribute of attributes) {
            const attributeValue = new AttributeValue<typeof attribute.type>({
                attribute: attribute as any,
                value: []
            });

            expect(attributeValue.getDbAttributeValue()).toBeNull();
        }
    });

    it('should return null db value if it is empty array in each lang', async () => {
        const attributes = [
            {
                type: AttributeType.TEXT,
                isValueLocalizable: true,
                isArray: true,
                properties: {}
            },
            {
                type: AttributeType.STRING,
                isValueLocalizable: true,
                isArray: true,
                properties: {}
            }
        ];

        for (const attribute of attributes) {
            const attributeValue = new AttributeValue<typeof attribute.type>({
                attribute: attribute as any,
                value: {
                    ru: []
                }
            });

            expect(attributeValue.getDbAttributeValue()).toBeNull();
        }
    });

    it('should ignore empty array in db value', async () => {
        const attributes = [
            {
                type: AttributeType.TEXT,
                isValueLocalizable: true,
                isArray: true,
                properties: {}
            },
            {
                type: AttributeType.STRING,
                isValueLocalizable: true,
                isArray: true,
                properties: {}
            }
        ];

        for (const attribute of attributes) {
            const attributeValue = new AttributeValue<typeof attribute.type>({
                attribute: attribute as any,
                value: {
                    ru: [],
                    en: ['foo']
                }
            });

            expect(attributeValue.getDbAttributeValue()).toEqual([{langIsoCode: 'en', value: ['foo']}]);
        }
    });
});

describe('attribute value: "NUMBER" properties', () => {
    it('should handle "min" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: false,
            properties: {min: 0}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: -1
                })
        ).toThrow(InvalidNumberMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 20
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "min" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: true,
            properties: {min: 0}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [10, -1]
                })
        ).toThrow(InvalidNumberMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: [10, 0]
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle "max" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: false,
            properties: {max: 10}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 11
                })
        ).toThrow(InvalidNumberMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 10
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "max" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: true,
            properties: {max: 10}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [10, 11]
                })
        ).toThrow(InvalidNumberMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: [5, 10]
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle "isInteger" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: false,
            properties: {isInteger: true}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 0.25
                })
        ).toThrow(InvalidNumberIsIntegerAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 25
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "isInteger" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: true,
            properties: {isInteger: true}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [5, 0.25]
                })
        ).toThrow(InvalidNumberIsIntegerAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: [5, 25]
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle "isNonNegative" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: false,
            properties: {isNonNegative: true}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: -1
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 1
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "isNonNegative" property', async () => {
        const attribute: NumberAttribute = {
            type: AttributeType.NUMBER,
            isValueLocalizable: false,
            isArray: true,
            properties: {isNonNegative: true}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [5, -0.25]
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: [5, 25]
            })
        ).toBeInstanceOf(AttributeValue);
    });
});

describe('attribute value: "STRING" properties', () => {
    it('should handle "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'fo'
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: true,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['bar', 'fo']
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['bar', 'foo']
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle localizable "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: false,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'bar', en: 'fo'}
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: 'bar', en: 'foo'}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple localizable "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: true,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['bar', 'fo']}
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: ['bar', 'foo']}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo'
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'fo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: true,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['ba', 'foo']
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['ba', 'fo']
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle localizable "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: false,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'ba', en: 'foo'}
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: 'ba', en: 'fo'}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple localizable "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: true,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['ba', 'foo']}
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: ['ba', 'fo']}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle negative "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {min: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'fo'
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle multiple negative "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: true,
            properties: {min: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['bar', 'fo']
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle localizable negative "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: false,
            properties: {min: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'bar', en: 'fo'}
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle multiple localizable negative "min" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: true,
            properties: {min: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['bar', 'fo']}
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle negative "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: false,
            properties: {max: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo'
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle multiple negative "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: false,
            isArray: true,
            properties: {max: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['ba', 'foo']
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle localizable negative "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: false,
            properties: {max: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'ba', en: 'foo'}
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });

    it('should handle multiple localizable negative "max" property', async () => {
        const attribute: StringAttribute = {
            type: AttributeType.STRING,
            isValueLocalizable: true,
            isArray: true,
            properties: {max: -1}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['ba', 'foo']}
                })
        ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
    });
});

describe('attribute value: "TEXT" properties', () => {
    it('should handle "min" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: false,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'fo'
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'foo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "min" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: true,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['bar', 'fo']
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['bar', 'foo']
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle localizable "min" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: true,
            isArray: false,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'bar', en: 'fo'}
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: 'bar', en: 'foo'}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple localizable "min" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: true,
            isArray: true,
            properties: {min: 3}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['bar', 'fo']}
                })
        ).toThrow(InvalidStringMinAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: ['bar', 'foo']}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle "max" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: false,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: 'foo'
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: 'fo'
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple "max" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: false,
            isArray: true,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['ba', 'foo']
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: ['ba', 'fo']
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle localizable "max" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: true,
            isArray: false,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: 'ba', en: 'foo'}
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: 'ba', en: 'fo'}
            })
        ).toBeInstanceOf(AttributeValue);
    });

    it('should handle multiple localizable "max" property', async () => {
        const attribute: TextAttribute = {
            type: AttributeType.TEXT,
            isValueLocalizable: true,
            isArray: true,
            properties: {max: 2}
        };

        expect(
            () =>
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: {ru: ['ba', 'foo']}
                })
        ).toThrow(InvalidStringMaxAttributeValue);

        expect(
            new AttributeValue<typeof attribute.type>({
                attribute,
                value: {ru: ['ba', 'fo']}
            })
        ).toBeInstanceOf(AttributeValue);
    });
});

describe('attribute value: "maxArraySize" property', () => {
    describe('unlimited cases', () => {
        it('should handle "NUMBER" "maxArraySize" property', async () => {
            const attribute: NumberAttribute = {
                type: AttributeType.NUMBER,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 0}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: [1, 2, 3]
                    })
            ).not.toThrow();
        });

        it('should handle "BOOLEAN" "maxArraySize" property', async () => {
            const attribute: BooleanAttribute = {
                type: AttributeType.BOOLEAN,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 0}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: [true, false, true]
                    })
            ).not.toThrow();

            expect(
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [true]
                })
            ).toBeInstanceOf(AttributeValue);
        });

        it('should handle "IMAGE" "maxArraySize" property', async () => {
            const attribute: ImageAttribute = {
                type: AttributeType.IMAGE,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 0}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['/url1', '/url2']
                    })
            ).not.toThrow();
        });

        it('should handle "STRING" "maxArraySize" property', async () => {
            const attribute: StringAttribute = {
                type: AttributeType.STRING,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 0}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo', 'bar']
                    })
            ).not.toThrow();
        });

        it('should handle "TEXT" "maxArraySize" property', async () => {
            const attribute: TextAttribute = {
                type: AttributeType.TEXT,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 0}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo', 'bar']
                    })
            ).not.toThrow();
        });
    });

    describe('limited cases', () => {
        it('should handle "NUMBER" "maxArraySize" property', async () => {
            const attribute: NumberAttribute = {
                type: AttributeType.NUMBER,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: [1, 2]
                    })
            ).toThrow(InvalidMultipleAttributeValueMaxSize);

            expect(
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [1]
                })
            ).toBeInstanceOf(AttributeValue);
        });

        it('should handle "BOOLEAN" "maxArraySize" property', async () => {
            const attribute: BooleanAttribute = {
                type: AttributeType.BOOLEAN,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: [true, false]
                    })
            ).toThrow(InvalidMultipleAttributeValueMaxSize);

            expect(
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: [true]
                })
            ).toBeInstanceOf(AttributeValue);
        });

        it('should handle "IMAGE" "maxArraySize" property', async () => {
            const attribute: ImageAttribute = {
                type: AttributeType.IMAGE,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['/url1', '/url2']
                    })
            ).toThrow(InvalidMultipleAttributeValueMaxSize);

            expect(
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['/url1']
                })
            ).toBeInstanceOf(AttributeValue);
        });

        it('should handle "STRING" "maxArraySize" property', async () => {
            const attribute: StringAttribute = {
                type: AttributeType.STRING,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo', 'bar']
                    })
            ).toThrow(InvalidMultipleAttributeValueMaxSize);

            expect(
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['foo']
                })
            ).toBeInstanceOf(AttributeValue);
        });

        it('should handle "TEXT" "maxArraySize" property', async () => {
            const attribute: TextAttribute = {
                type: AttributeType.TEXT,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: 1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo', 'bar']
                    })
            ).toThrow(InvalidMultipleAttributeValueMaxSize);

            expect(
                new AttributeValue<typeof attribute.type>({
                    attribute,
                    value: ['foo']
                })
            ).toBeInstanceOf(AttributeValue);
        });
    });

    describe('negative cases', () => {
        it('should handle "NUMBER" "maxArraySize" property', async () => {
            const attribute: NumberAttribute = {
                type: AttributeType.NUMBER,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: -1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: [1]
                    })
            ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
        });

        it('should handle "BOOLEAN" "maxArraySize" property', async () => {
            const attribute: BooleanAttribute = {
                type: AttributeType.BOOLEAN,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: -1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: [true]
                    })
            ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
        });

        it('should handle "IMAGE" "maxArraySize" property', async () => {
            const attribute: ImageAttribute = {
                type: AttributeType.IMAGE,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: -1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['/url1']
                    })
            ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
        });

        it('should handle "STRING" "maxArraySize" property', async () => {
            const attribute: StringAttribute = {
                type: AttributeType.STRING,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: -1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo']
                    })
            ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
        });

        it('should handle "TEXT" "maxArraySize" property', async () => {
            const attribute: TextAttribute = {
                type: AttributeType.TEXT,
                isValueLocalizable: false,
                isArray: true,
                properties: {maxArraySize: -1}
            };

            expect(
                () =>
                    new AttributeValue<typeof attribute.type>({
                        attribute,
                        value: ['foo']
                    })
            ).toThrow(InvalidNumberIsNonNegativeAttributeValue);
        });
    });
});
