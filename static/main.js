templates = {};
reqdata = {};
globid = null;

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
    function success(data) {
        if("luggage" in data)
            reqdata = $.extend(reqdata, data.luggage);
        success_callback.apply(this, [data]);
    }
    if(!data)
        data = {};
    $.ajax({
        url: url,
        dataType: "json",
        data: $.extend(true, {uid: globid}, data, reqdata),
        success: success
    });
}

function handleQuestion(data) {
    $("#initial_info").hide();
    var wrapper = $("<div>");
    wrapper.addClass("resp");
    wrapper.html(templates[data.type](data));

    function submit() {
        json_wrap(
            "/questions/" + data.endpoint,
            handleQuestion,
            _.reduce(
                wrapper.find("input").serializeArray(),
                function(memo, val) {memo[val.name] = val.value; return memo;},
                {}
            )
        );
        wrapper.addClass("disabled");
        wrapper.find("input, button").attr("disabled", "disabled");
    }
    wrapper.find("input[type=text]").keypress(function(e) {
        if(e.which == 13) {
            e.preventDefault();
            return submit();
        }
    });
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
        '<input type="text" name="response" /> <button>&raquo;</button>'
    );
    templates.choices = _.template(
        '<h1><%= text %></h1>' +
        '<% for(var c in choices) { %>' +
            '' +
        '<% } %>' +
        '<button>&raquo;</button>'
    );

    if("reqdata" in window.localStorage)
        reqdata = window.localStorage["reqdata"]
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
