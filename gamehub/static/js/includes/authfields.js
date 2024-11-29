document.addEventListener("click", e => {
    if (!e.target.matches("#auth-submit")) return
    let username = $("#username").val()
    let password = $("#password").val()
    $.ajax({
        method: "POST",
        url: AUTHPAGE_URL,
        data: {
            "username": username,
            "password": password,
            "remember_me": $("#remember-me").val() == "on",
            "action": "auth-user",
            "csrfmiddlewaretoken": CSRF_TOKEN,
        },
        dataType: "json",
        success: function(data) {
            if (data["has_error_message"]) {
                const errorMessage = $("<p class='error-message'>" + data["error_message"] + ".</p>");

                $("#auth-form").children().last().before(errorMessage);

                const displayDuration = 3000;

                errorMessage.hide().fadeIn(300);

                setTimeout(function() {
                        errorMessage.fadeOut(300, function() {
                                $(this).remove();
                        });
                }, displayDuration);
            
            } else if (data["success"]) {
                window.location.href = data["redirect_to"]
            } else {
                alert("Got an unexpected error while loggining")
            }
        },
        error: function(xhr, errmsg, err) {
                console.log(xhr.status + ":" + xhr.responseText)
        }
    })
})

document.addEventListener("click", e => {
    if (!e.target.matches(".auth-option-button")) return
    $.ajax({
        method: "POST",
        url: AUTHPAGE_URL,
        data: {
            "action": "change-auth-type",
            "auth-type": $(".auth-option-button").data("auth-type"),
            "csrfmiddlewaretoken": CSRF_TOKEN,
        },
        dataType: "json",
        success: function(data) {
            if (data["auth_option"] == 0) {
                $("#auth-login").removeClass().addClass("auth-option-button-selected");
                $("#auth-signup").removeClass().addClass("auth-option-button");
            } else {
                $("#auth-login").removeClass().addClass("auth-option-button");
                $("#auth-signup").removeClass().addClass("auth-option-button-selected");
            }
        },
        error: function(xhr, errmsg, err) {
                console.log(xhr.status + ":" + xhr.responseText)
        }
    })
})