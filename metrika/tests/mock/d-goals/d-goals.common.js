BEM.decl('d-goals', null, {

    goal1: function () {
        return this.goals()[4];
    },

    goal2: function () {
        return this.goals()[5].steps[1];
    },

    goals: function () {
        return BEM.blocks['d-counter'].get().goals;
    }

});

