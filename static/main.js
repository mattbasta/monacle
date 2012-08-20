templates = {};
reqdata = {};
globid = null;

queries = [];

function save_data() {window.localStorage["reqdata"] = JSON.stringify(reqdata);}

function add_data(key, value) {
    reqdata[key] = value;
    save_data();
}

function ajax_wrap(url, success_callback, failure_callback) {
    $.ajax({
        url: url,
        data: $.extend(true, {uid: globid}, reqdata),
        success: success_callback,
        error: failure_callback
    });
}
function json_wrap(url, success_callback, data) {
    if(!data)
        data = {};
    $.ajax({
        url: url,
        cache: false,
        dataType: "json",
        data: $.extend(true, {uid: globid}, data, reqdata),
        success: function(data) {
            if("luggage" in data) {
                reqdata = $.extend(reqdata, data.luggage);
                window.localStorage["reqdata"] = JSON.stringify(reqdata);
            }
            success_callback.apply(this, [data]);
        }
    });
}

function handleQuestion(data) {
    if(data.type == "multi") {
        for(var i in data.responses)
            handleQuestion(data.responses[i]);
        return;
    }

    $("#initial_info").hide();
    var wrapper = $("<div>");
    wrapper.addClass("resp");
    wrapper.addClass(data.type);
    if(!("lat" in data && "lon" in data) && "coords" in data) {
        data.lat = data.coords.lat;
        data.lon = data.coords.lon;
    }
    wrapper.html(templates[data.type](data));

    function submit() {
        var ser_array = wrapper.find("input").serializeArray();
        // Save each of the text input values to the list of queries.
        _.each(ser_array, function(v) {queries.push(v.value);});

        json_wrap(
            "/questions/" + data.endpoint,
            handleQuestion,
            _.reduce(
                ser_array,
                function(memo, val) {memo[val.name] = val.value; return memo;},
                {}
            )
        );
        wrapper.addClass("disabled");
        wrapper.find("input, button").attr("disabled", "disabled");
    }


    var index = -1,
        partial_val = "";
    wrapper.find("input[type=text]").keyup(function(e) {
        function post_setval() {
            var toIndex = this.value.length;
            if(this.createTextRange) {
                var range = this.createTextRange();
                range.move("character", toIndex);
                range.select();
            } else if(this.selectionStart != null) {
                this.focus();
                this.setSelectionRange(toIndex, toIndex);
            }
        }
        function setval() {
            this.value = queries[queries.length - index - 1];
            post_setval.apply(this);
        }
        switch(e.which) {
            case 13:
                e.preventDefault();
                return submit();
            case 38:
                if(index == -1)
                    partial_val = this.value;
                index++;
                if(index >= queries.length)
                    return index--;
                return setval.apply(this);
            case 40:
                if(index == -1)
                    return;
                index--;
                if(index == -1) {
                    this.value = partial_val;
                    return post_setval.apply(this);
                }
                return setval.apply(this);
        }
    }).focus();
    wrapper.find("button").click(submit);

    if("endpoint" in data) {
        wrapper.addClass("prompt");
        wrapper.data("endpoint", data.endpoint);
    }

    $("header").after(wrapper);
}

$(function() {

    templates.static = _.template('<p><%= text %></p>');
    templates.textquestion = _.template(
        '<h1><%= text %></h1>' +
        '<input type="text" name="response" x-webkit-speech /> <button>&raquo;</button>'
    );
    templates.place = _.template(
        '<h1><%= name %></h1>' +
        '<% if(address) { %><p><b><%= address %></b>, <%= place.locality %>, <%= place.region %></p><% } %>' +
        '<img src="http://maps.googleapis.com/maps/api/staticmap?' +
        'center=<%= lat %>,<%= lon %>&zoom=<%= zoom %>&size=300x300&' +
        'markers=color:red|<%= lat %>,<%= lon %>&' +
        'sensor=false">'
    );
    // templates.choices = _.template(
    //     '<h1><%= text %></h1>' +
    //     '<% for(var c in choices) { %>' +
    //         '' +
    //     '<% } %>' +
    //     '<button>&raquo;</button>'
    // );

    if("reqdata" in window.localStorage)
        reqdata = JSON.parse(window.localStorage["reqdata"]);
    else
        reqdata = {};

    var boot = grom(function() {
        console.log("ready " + boot.delay_count);
        json_wrap("/questions", handleQuestion);
    });

    if("gid" in window.localStorage)
        globid = window.localStorage["gid"];
    else {
        $.get("/uniqid", boot.delay(function(data) {
            window.localStorage["gid"] = globid = data;
        }));
    }

    navigator.geolocation.getCurrentPosition(boot.delay(function(location) {
        reqdata["latitude"] = location.coords.latitude;
        reqdata["longitude"] = location.coords.longitude;
    }));

    boot.go();
});
