$(function() {
    var Query = Backbone.model.extend({
        defaults: {
            question: "What can I do for you?"
        },
        urlRoot: "/questions"
    });

    var Person = Backbone.model.extend({
        defaults: {}
    });

    var initial_question = new Query({id: "initial"});
});
