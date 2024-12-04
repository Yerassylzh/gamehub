
document.addEventListener("click", e => {
    if (!e.target.matches("[data-left-img]") && e.target.closest("[data-left-img]") == null) return

    $.ajax({
      method: "POST",
      url: CLUB_DETAILS,
      data: {
          "action": "get-left-image",
          "current_image_url": document.getElementById("image").getAttribute("src"),
          "csrfmiddlewaretoken": CSRF_TOKEN,
      },
      dataType: "json",
      success: function(data) {
        document.getElementById("image").setAttribute("src", data["current_image_url"])
      },
      error: function(xhr, errmsg, err) {
          console.log(xhr.status + ":" + xhr.responseText)
      }
    })
  })

  document.addEventListener("click", e => {
    if (!e.target.matches("[data-right-img]") && e.target.closest("[data-right-img]") == null) return

    $.ajax({
      method: "POST",
      url: CLUB_DETAILS,
      data: {
          "action": "get-right-image",
          "current_image_url": document.getElementById("image").getAttribute("src"),
          "csrfmiddlewaretoken": CSRF_TOKEN,
      },
      dataType: "json",
      success: function(data) {
        document.getElementById("image").setAttribute("src", data["current_image_url"])
      },
      error: function(xhr, errmsg, err) {
          console.log(xhr.status + ":" + xhr.responseText)
      }
    })
  })