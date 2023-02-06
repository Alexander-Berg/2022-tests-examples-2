import { mockReq } from '@lib/views/mockReq';
import { cls } from '../cls';

jest.mock('../../../../build/utils/clsCore', function() {
    return {
        CLSCore: class CLSCore {
            full(_val: string): string {
                return 'full';
            }
            part(_val: string): string {
                return 'part';
            }
        }
    };
});

describe('home.cls', function() {
    let generatedClsReq = mockReq({}, {
        antiadb_desktop: 1,
        clsGen: true
    });

    test('should return non-generated cls on empty req', function() {
        let inst = cls(mockReq());

        expect(inst.generated).toEqual(false);
        expect(inst.full('line some__line row, media__row heap_direction_column')).toEqual('line some__line row, media__row heap_direction_column');
        expect(inst.part('line some__line row, media__row heap_direction_column')).toEqual('line some__line row, media__row heap_direction_column');
    });

    test('should return generated cls on special req', function() {
        let inst = cls(generatedClsReq);

        expect(inst.generated).toEqual(true);
        expect(inst.full('line some__line row, media__row heap_direction_column')).toEqual('full');
        expect(inst.part('line some__line row, media__row heap_direction_column')).toEqual('part');
    });
});
