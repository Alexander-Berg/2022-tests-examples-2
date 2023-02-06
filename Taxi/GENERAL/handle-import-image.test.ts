import {seed, uuid} from 'casual';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';
import {createMasterCategoryWithInfoModel} from 'tests/unit/util';

import {ATTRIBUTES_CODES} from '@/src/constants';
import {IDENTIFIER_HEADER, IMAGE_HEADER} from '@/src/constants/import';
import {ImportSpreadsheet} from '@/src/entities/import-spreadsheet/entity';
import type {Product} from '@/src/entities/product/entity';
import {handleImportImage} from 'server/routes/api/v1/import/products/handle-import-image';
import {ensureConnection} from 'service/db';
import {AttributeType} from 'types/attribute';

seed(3);

const HEADER_ROW: string[] = [IDENTIFIER_HEADER, IMAGE_HEADER];

describe('handle import image', () => {
    let product: Product;
    let regionId: number;

    beforeEach(async () => {
        const {user, infoModel, region: createdRegion, masterCategory} = await createMasterCategoryWithInfoModel();
        regionId = createdRegion.id;
        product = await TestFactory.createProduct({
            userId: user.id,
            masterCategoryId: masterCategory.id,
            regionId
        });

        const barcodeAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.STRING, code: ATTRIBUTES_CODES.BARCODE},
            userId: user.id
        });

        const imageAttr = await TestFactory.createAttribute({
            attribute: {type: AttributeType.IMAGE, code: ATTRIBUTES_CODES.IMAGE, isArray: true},
            userId: user.id
        });

        await TestFactory.linkAttributesToInfoModel({
            userId: user.id,
            infoModelId: infoModel.id,
            attributes: [{id: imageAttr.id}, {id: barcodeAttr.id}]
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: ['/image1', '/image2', '/image3', '/image4'],
            productId: product.id,
            attributeId: imageAttr.id
        });

        await TestFactory.createProductAttributeValue({
            userId: user.id,
            value: '123',
            productId: product.id,
            attributeId: barcodeAttr.id
        });
    });

    it('should handle images by barcode', async () => {
        const importKey = uuid;
        const image1 = await TestFactory.createImportImage({
            importKey,
            relPath: '123.png',
            imageUrl: 'avatars',
            regionId
        });
        const image2 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_2.png',
            imageUrl: 'avatars_2',
            regionId
        });
        const image3 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_3.png',
            imageUrl: 'avatars_2',
            regionId
        });
        const image4 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_4.png',
            imageUrl: 'avatars_2',
            regionId
        });

        expect(await handleImportImage([image4, image1, image2, image3], importKey, regionId)).toBeUndefined();

        const manager = await ensureConnection();
        const importSpreadsheet = await manager.getRepository(ImportSpreadsheet).findOne({importKey});
        expect(importSpreadsheet?.content).toEqual([
            HEADER_ROW,
            [product.identifier.toString(), '123.png; 123_2.png; 123_3.png; 123_4.png']
        ]);
    });

    it('should replace images by position', async () => {
        const importKey = uuid;
        const image1 = await TestFactory.createImportImage({
            importKey,
            relPath: '123.png',
            imageUrl: 'avatars',
            regionId
        });
        const image2 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_3.png',
            imageUrl: 'avatars_4',
            regionId
        });
        const image3 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_9.png',
            imageUrl: 'avatars_9',
            regionId
        });

        expect(await handleImportImage([image1, image2, image3], importKey, regionId)).toBeUndefined();

        const manager = await ensureConnection();
        const importSpreadsheet = await manager.getRepository(ImportSpreadsheet).findOne({importKey});
        expect(importSpreadsheet?.content).toEqual([
            HEADER_ROW,
            [product.identifier.toString(), '123.png; /image2; 123_3.png; /image4; 123_9.png']
        ]);
    });

    it('should ignore images with wrong barcodes', async () => {
        const importKey = uuid;
        const image1 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_copy.png',
            imageUrl: 'avatars_copy',
            regionId
        });
        const image2 = await TestFactory.createImportImage({
            importKey,
            relPath: '123_2.png',
            imageUrl: 'avatars_2',
            regionId
        });
        const image3 = await TestFactory.createImportImage({
            importKey,
            relPath: 'wrong_barcode.png',
            imageUrl: 'avatars_wrong',
            regionId
        });

        expect(await handleImportImage([image1, image2, image3], importKey, regionId)).toBeUndefined();

        const manager = await ensureConnection();
        const importSpreadsheet = await manager.getRepository(ImportSpreadsheet).findOne({importKey});
        expect(importSpreadsheet?.content).toEqual([
            HEADER_ROW,
            [product.identifier.toString(), '/image1; 123_2.png; /image3; /image4']
        ]);
    });

    it('should not create spreadsheet when all images have wrong barcodes', async () => {
        const importKey = uuid;
        const image1 = await TestFactory.createImportImage({
            importKey,
            relPath: '321.png',
            imageUrl: 'avatars',
            regionId
        });
        const image2 = await TestFactory.createImportImage({
            importKey,
            relPath: '321_2.png',
            imageUrl: 'avatars_2',
            regionId
        });

        expect(await handleImportImage([image1, image2], importKey, regionId)).toBeUndefined();

        const manager = await ensureConnection();
        const importSpreadsheet = await manager.getRepository(ImportSpreadsheet).findOne({importKey});
        expect(importSpreadsheet).toBeUndefined();
    });

    it('should ignore images from other regions', async () => {
        const region = await TestFactory.createRegion();
        const importKey = uuid;
        const image1 = await TestFactory.createImportImage({
            importKey,
            relPath: '123.png',
            imageUrl: 'avatars',
            regionId: region.id
        });

        expect(await handleImportImage([image1], importKey, region.id)).toBeUndefined();

        const manager = await ensureConnection();
        const importSpreadsheet = await manager.getRepository(ImportSpreadsheet).findOne({importKey});
        expect(importSpreadsheet?.content).toBeUndefined();
    });

    it('should handle images in folders', async () => {
        const importKey = uuid;
        const image1 = await TestFactory.createImportImage({
            importKey,
            relPath: 'folder/123.png',
            imageUrl: 'avatars',
            regionId
        });
        const image2 = await TestFactory.createImportImage({
            importKey,
            relPath: 'folder/123_2.png',
            imageUrl: 'avatars_2',
            regionId
        });
        const image3 = await TestFactory.createImportImage({
            importKey,
            relPath: 'folder/123_3.png',
            imageUrl: 'avatars_2',
            regionId
        });
        const image4 = await TestFactory.createImportImage({
            importKey,
            relPath: 'folder/123_4.png',
            imageUrl: 'avatars_2',
            regionId
        });

        expect(await handleImportImage([image4, image1, image2, image3], importKey, regionId)).toBeUndefined();

        const manager = await ensureConnection();
        const importSpreadsheet = await manager.getRepository(ImportSpreadsheet).findOne({importKey});
        expect(importSpreadsheet?.content).toEqual([
            HEADER_ROW,
            [product.identifier.toString(), 'folder/123.png; folder/123_2.png; folder/123_3.png; folder/123_4.png']
        ]);
    });
});
