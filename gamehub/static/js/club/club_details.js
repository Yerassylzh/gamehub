document.addEventListener("click", e => {
    if (!e.target.matches("#homepage-btn")) return
    window.location.href = HOMEPAGE_URL
})

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



document.addEventListener("click", e => {
    if (!e.target.matches("#create-feedback-btn") && e.target.closest("#create-feedback-btn") == null) return

    let createFeedbackButton = document.getElementById("create-feedback-btn")
    createFeedbackButton.remove()

    let rating = document.createElement("div")
    rating.setAttribute("class", "rating")
    rating.setAttribute("id", "rating")
    for (let i = 1; i <= 5; i++) {
        let star_img = document.createElement("img")
        star_img.setAttribute("class", "star-img")
        star_img.setAttribute("id", "star-empty" + i.toString())
        star_img.setAttribute("src", EMPTY_STAR_IMG_URL)
        rating.appendChild(star_img)
    }
    
    let feedbackInput = document.createElement("textarea")
    feedbackInput.setAttribute("class", "col-8 col-md-5 col-xl-5 feedback-input")
    feedbackInput.setAttribute("id", "feedback-input")
    
    let saveFeedbackButton = document.createElement("button")
    saveFeedbackButton.setAttribute("class", "save-feedback-btn")
    saveFeedbackButton.setAttribute("id", "save-feedback-btn")
    saveFeedbackButton.textContent = "Сохранить"

    let feedbackInputWrapper = document.createElement("div")
    feedbackInputWrapper.setAttribute("class", "feedback-input-wrapper")
    feedbackInputWrapper.setAttribute("id", "feedback-input-wrapper")

    feedbackInputWrapper.appendChild(rating)
    feedbackInputWrapper.appendChild(feedbackInput)
    feedbackInputWrapper.appendChild(saveFeedbackButton)

    let contentSectionWrapper = document.getElementById("content-section")
    contentSectionWrapper.appendChild(feedbackInputWrapper)
  })

  document.addEventListener("click", e => {
    if (!e.target.matches("#save-feedback-btn") && e.target.closest("#save-feedback-btn") == null) return

    $.ajax({
      method: "POST",
      url: CLUB_DETAILS_URL,
      data: {
        "csrfmiddlewaretoken": CSRF_TOKEN,
        "action": "save-feedback",
        "feedback_message": document.getElementById("feedback-input").value,
        "feedback_rating": current_rating,
      },
      dataType: "json",
      success: function (data) {
        current_rating = 0;

        let feedbackInputWrapper = document.getElementById("feedback-input-wrapper")
        feedbackInputWrapper.remove()

        let contentSectionWrapper = document.getElementById("content-section")

        let statusMessage = document.createElement("p")
        statusMessage.setAttribute("class", "success-message")
        statusMessage.textContent = "Ваш отзыв был успешно добавлен"
        contentSectionWrapper.appendChild(statusMessage)

        let createFeedbackButton = document.createElement("button")
        createFeedbackButton.setAttribute("class", "create-feedback-btn")
        createFeedbackButton.setAttribute("id", "create-feedback-btn")
        createFeedbackButton.textContent = "Оставить отзыв"
        contentSectionWrapper.appendChild(createFeedbackButton)

        
        setTimeout(() => {
          statusMessage.style.opacity = 0;
          setTimeout(() => {
            statusMessage.remove();
          }, 200);
        }, 3000);
      },
      error: function(xhr, errmsg, err) {
        current_rating = 0;

        let contentSectionWrapper = document.getElementById("content-section")
        
        let feedbackInputWrapper = document.getElementById("feedback-input-wrapper")
        feedbackInputWrapper.remove()
        
        let statusMessage = document.createElement("p")
        statusMessage.setAttribute("class", "error-message")
        statusMessage.textContent = "Возникла ошибка"
        contentSectionWrapper.appendChild(statusMessage)

        let createFeedbackButton = document.createElement("button")
        createFeedbackButton.setAttribute("class", "create-feedback-btn")
        createFeedbackButton.setAttribute("id", "create-feedback-btn")
        createFeedbackButton.textContent = "Оставить отзыв"
        contentSectionWrapper.appendChild(createFeedbackButton)
        
        setTimeout(() => {
          statusMessage.style.opacity = 0;
          setTimeout(() => {
            statusMessage.remove();
          }, 200);
        }, 3000);
      }
    })
  })

  document.addEventListener("click", e => {
    if (!e.target.matches(".star-img")) return

    let img_id = e.target.id
    current_rating = parseInt(img_id.charAt(img_id.length - 1))
    console.log("curent rating: ", current_rating)

    document.getElementById("rating").remove()

    let rating = document.createElement("div")
    rating.setAttribute("class", "rating")
    rating.setAttribute("id", "rating")
    for (let i = 1; i <= current_rating; i++) {
        let star_img = document.createElement("img")
        star_img.setAttribute("class", "star-img")
        star_img.setAttribute("id", "star-full" + i.toString())
        star_img.setAttribute("src", FULL_STAR_IMG_URL)
        rating.appendChild(star_img)
    }

    for (let i = current_rating + 1; i <= 5; i++) {
      let star_img = document.createElement("img")
      star_img.setAttribute("class", "star-img")
      star_img.setAttribute("id", "star-empty" + i.toString())
      star_img.setAttribute("src", EMPTY_STAR_IMG_URL)
      rating.appendChild(star_img)
    }

    let feedbackInputWrapper = document.getElementById("feedback-input-wrapper")
    feedbackInputWrapper.insertBefore(rating, document.getElementById("feedback-input"))
})
