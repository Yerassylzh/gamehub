document.addEventListener("click", e => {
    if (!e.target.matches("#auth-submit") && e.target.closest("#auth-submit") == null) return
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
            "auth_type": document.getElementById("auth-type-wrapper").getAttribute("auth_type"),
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
    if (!e.target.matches("#auth-type-wrapper") && e.target.closest("#auth-type-wrapper") == null) return
    
    auth_btns_wrapper = document.getElementById("auth-type-wrapper")
    if (e.target.matches("#auth-login")) {
        $("#auth-login").removeClass().addClass("auth-option-button-selected");
        $("#auth-signup").removeClass().addClass("auth-option-button");
        auth_btns_wrapper.setAttribute("auth_type", "0")
    } else {
        $("#auth-login").removeClass().addClass("auth-option-button");
        $("#auth-signup").removeClass().addClass("auth-option-button-selected");
        auth_btns_wrapper.setAttribute("auth_type", "1")
    }
})
