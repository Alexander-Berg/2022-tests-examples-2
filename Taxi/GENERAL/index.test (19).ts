import Ajv, {AnySchema} from 'ajv';
import fs from 'fs';
import jsYaml from 'js-yaml';

import {serviceResolve} from '@/src/lib/resolve';

const CLIENT_ATTRIBUTES_PATH = './docs/api/definitions/client-attributes.yaml';

describe('validate schemas', () => {
    it(`should validate schema "${CLIENT_ATTRIBUTES_PATH}"`, async () => {
        let errorMessage: string | undefined;

        const clientAttributesSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/client-attributes.yaml'), 'utf8')
        ) as AnySchema;
        const tankerNameSchema = jsYaml.load(
            fs.readFileSync(serviceResolve('./docs/api/definitions/tanker-name.yaml'), 'utf8')
        ) as AnySchema;

        try {
            const ajv = new Ajv({allErrors: true, strict: true});
            ajv.addKeyword('example');
            ajv.addSchema(tankerNameSchema, 'tanker-name.yaml');
            ajv.compile(clientAttributesSchema);
        } catch (error) {
            errorMessage = error.message;
        }

        expect(errorMessage).toBeUndefined();
    });
});
