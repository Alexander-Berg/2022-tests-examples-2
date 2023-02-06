type BaseGoal = {
    name: string;
    type: string;
    is_retargeting: number;
    depth: number;
};

export type SavedGoal = BaseGoal & {
    id: number;
};

export type GoalToSave = BaseGoal & {
    flag: string;
    conditions: {
        type: string;
        url: string;
    };
};

type BaseCounter = {
    name: string;
    site2: {
        site: string;
    };
};

export type SavedCounter = BaseCounter & {
    id: number;
    goals: SavedGoal[];
};

export type CounterToSave = BaseCounter & {
    goals: GoalToSave[];
};
