import execa from 'execa';

import {serviceResolve} from '@/src/lib/resolve';

export default function runLoadBalancer(instances: number) {
    const pathToCompiledFile = serviceResolve('out/src/tests/e2e/load-balancer/load-balancer.js');

    return execa('node', [pathToCompiledFile], {
        stdout: 'inherit',
        stderr: 'inherit',
        env: {INSTANCES_COUNT: String(instances)}
    });
}
