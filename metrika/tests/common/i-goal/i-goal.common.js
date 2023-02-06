describe('i-goal', function () {
    var iGoal = BN('i-goal'),
        goals = BN('d-goals').goals(),
        goal1 = BN('d-goals').goal1(),
        goal2 = BN('d-goals').goal2();

    describe('static method getGoalById', function () {
        it('returns false if goal id is null', function () {
            expect(iGoal.getGoalById(null, goals))
                .to.be.equal(false);
        });

        it('returns false if goals list is empty', function () {
            expect(iGoal.getGoalById(goal1.id, []))
                .to.be.equal(false);
        });

        it('returns false if goals list is null', function () {
            expect(iGoal.getGoalById(goal1.id, null))
                .to.be.equal(false);
        });

        it('found correct goal', function () {
            expect(iGoal.getGoalById(goal1.id, goals))
                .to.eql(goal1);
        });

        it('found correct step-goal', function () {
            expect(iGoal.getGoalById(goal2.id, goals))
                .to.eql(goal2);
        });
    });
});

