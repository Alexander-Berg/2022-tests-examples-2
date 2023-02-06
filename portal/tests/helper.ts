import { Alert } from '../alerts/alert-handles';
import { Block } from '../index';
import { TestItem } from './data';

type ItemsType = Block | Alert;

export const getCases = (items: ItemsType[], countPerGroup = 20) => {
    let res: TestItem[] = [];
    let order = 0;

    for (let [, item] of Object.entries(items)) {
        const { id, testConfig = {} } = item;
        const { cases, height, skip, only, skipDarkMode } = testConfig;

        if (skip) {
            continue;
        }

        if (Array.isArray(cases)) {
            // eslint-disable-next-line no-loop-func
            const cardTests = cases.map(item => {
                order += 1;
                return {
                    id,
                    group: Math.floor((order - 1) / countPerGroup) + 1,
                    skipDarkMode: item.skipDarkMode !== undefined ? item.skipDarkMode : skipDarkMode,
                    name: `${id}#${item.name}`,
                    height: item.height,
                    width: item.width
                };
            });

            if (only) {
                res = cardTests;
                break;
            }

            res = res.concat(cardTests);
        } else if (only) {
            res = [{ id, group: 1, height, name: id, skipDarkMode }];
            break;
        } else {
            order++;
            res.push({ id, group: Math.floor((order - 1) / countPerGroup) + 1, height, name: id, skipDarkMode });
        }
    }

    return res;
};

export const grouping = (arr: TestItem[]) => {
    const groups: {
        [key: number]: TestItem[];
    } = {};
    arr.forEach(item=>{
        if (groups[item.group]) {
            groups[item.group].push(item);
        } else {
            groups[item.group] = [item];
        }
    });

    return Object.entries(groups).map(group=>{
        return {
            id: group[0],
            items: group[1]
        };
    });
};
