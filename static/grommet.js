function grom(func, args) {
    this.is_grommet = true;

    // Save the information necessary to call the callback.
    this.func = func;
    this.args = args || [];
    this.ready = false;

    this.callbacks = $.Callbacks("memory unique");
    this.delay_count = 0;

    this.thens = [];

    var t = this;

    this.go = function() {
        this.ready = true;
        this.trigger();
    };
    this.trigger = function() {
        if(!this.ready || this.delay_count)
            return;
        
        while(t.thens.length) {
            var then = t.thens.shift();
            if(typeof then == "function")
                then.apply(t, []);
            else if(typeof then == "object" && then.is_grommet)
                then.trigger();
        }

        t.func.apply(t, t.args);
        t.callbacks.fire();
    };
    this.after = function(g) {
        if(typeof g !== "object" || !g.is_grommet)
            throw new Exception("Cannot chain grommets to functions.");
        this.delay_count++;
        g.callbacks.add(function() {
            this.delay_count--;
            t.trigger();
        });
        return t;
    };
    this.then = function(f) {
        t.thens.push(f);
        return t;
    };
    this.delay = function(f) {
        this.delay_count++;
        return function() {
            if(f)
                var out = f.apply(t, arguments);
            
            t.delay_count--;
            t.trigger();
            return out;
        };
    };

    return this;
}