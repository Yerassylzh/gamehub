document.addEventListener("click", e => {
    if (!e.target.matches("#my-bookings")) return
    window.location.href = MYBOOKINGS_URL
})

document.addEventListener("click", e => {
    if (!e.target.matches("#logout-btn")) return

    $.ajax({
        method: "POST",
        url: HOMEPAGE_URL,
        data: {
            "action": "logout",
            "csrfmiddlewaretoken": CSRF_TOKEN,
        },
        dataType: "json",
        success: function(data) {
            window.location.href = data["redirect_to"]
        },
        error: function(xhr, errmsg, err) {
            console.log(xhr.status + ":" + xhr.responseText)
        }
    })
})

document.addEventListener("click", e => {
    const isDropdownButtonImg = e.target.matches("[data-dropdown-button-img]")

    if (!isDropdownButtonImg && e.target.closest("[data-dropdown]") != null) return

    if (!isDropdownButtonImg) {
        document.querySelectorAll("[data-dropdown].active").forEach(dropdown => {
            dropdown.classList.remove("active")
        })
    }

    else {
        currentDropdown = e.target.closest("[data-dropdown-button]").closest("[data-dropdown]")
        currentDropdown.classList.toggle("active")
    }
})
