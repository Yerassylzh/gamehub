
function get_error_p(content) {
    let message = document.createElement("p")
    message.setAttribute("class", "error-message")
    message.textContent = content
    setTimeout(() => {
      message.style.opacity = 0
      setTimeout(() => {
        message.remove()
      }, 200);
    }, 2000);
    return message
  }

  function get_success_p(content) {
    let message = document.createElement("p")
    message.setAttribute("class", "success-message")
    message.textContent = content
    setTimeout(() => {
      message.style.opacity = 0
      setTimeout(() => {
        message.remove()
      }, 200);
    }, 2000);
    return message
  }

  function removeAll(attrName) {
    document.querySelectorAll(attrName).forEach(item => {
      item.remove()
    })
  }

  document.addEventListener("click", e => {
    if (!e.target.matches("#booking-btn") && e.target.closest("#booking-btn") == null) return

    let bookingButton = document.getElementById("booking-btn")
    bookingButton.remove()
    
    let bookingSection = document.getElementById("booking-section")
    
    let dateInputWrapper = document.createElement("div")
    dateInputWrapper.setAttribute("class", "col-10 col-md-6 col-xl-5")
    dateInputWrapper.setAttribute("id", "date-input-wrapper")

    let dateInput = document.createElement("input")
    dateInput.setAttribute("type", "date")
    dateInput.setAttribute("id", "date-picker-input")
    dateInput.setAttribute("class", "date-picker-input")

    dateInputWrapper.appendChild(dateInput)
    bookingSection.appendChild(dateInputWrapper)
  })

  document.addEventListener("change", e => {
    if (!e.target.matches("#date-picker-input") && e.target.closest("#date-picker-input") == null) return

    let bookingSection = document.getElementById("booking-section")
    if (document.getElementById("date-picker-input").value === "") {
      bookingSection.appendChild(
        get_error_p("Введите валидную дату"),
      )
    }
    
    let [year, month, day] = document.getElementById("date-picker-input").value.split("-")

    $.ajax({
      method: "POST",
      url: CLUB_DETAILS_URL,
      data: {
        "csrfmiddlewaretoken": CSRF_TOKEN,
        "action": "save-date",
        "year": year,
        "month": month,
        "day": day,
      },
      dateType: "json",
      success: data => {
        current_booking_date = [year, month, day]

        if (data["time_intervals"].length == 0) {
          let bookingSection = document.getElementById("booking-section")
          bookingSection.appendChild(
            get_error_p("Очень забитый график, попробуйте позже"),
          )
        }

        let rowDiv = document.createElement("div")
        rowDiv.setAttribute("class", "row")
        rowDiv.setAttribute("id", "time-intervals-row")

        for (let i = 0; i < data["time_intervals"].length; i++) {
          let timeIntervalBtnWrapper = document.createElement("div")
          timeIntervalBtnWrapper.setAttribute("class", "col-4 col-md-3 col-xl-3")

          let timeIntervalBtn = document.createElement("button")
          timeIntervalBtn.setAttribute("id", "time-interval-btn-" + data["time_intervals"][i][0].toString())
          timeIntervalBtn.setAttribute("class", "time-interval")
          timeIntervalBtn.textContent = data["time_intervals"][i][0].toString() + ":00 - " + data["time_intervals"][i][1].toString() + ":00"

          timeIntervalBtnWrapper.appendChild(timeIntervalBtn)
          rowDiv.appendChild(timeIntervalBtnWrapper)
        }
      
        let bookingSection = document.getElementById("booking-section")
        bookingSection.appendChild(rowDiv)
      },
      error: (xhr, errmsg, err) => {
        let bookingSection = document.getElementById("booking-section")
      
        bookingSection.appendChild(
          get_error_p("Произошла ошибка"),
        )
      }
    })
  })
  
  document.addEventListener("click", e => {
    if (!e.target.matches(".time-interval") && e.target.closest(".time-interval") == null) return

    let button = document.getElementById(e.target.id)
    let startHour = parseInt(e.target.id.split("-")[e.target.id.split("-").length - 1])
    if (button.classList.contains("active-time-interval")) {
      button.classList.remove("active-time-interval")
      current_time_intervals = current_time_intervals.filter(item => item[0] !== startHour)
    }
    else {
      button.classList.toggle("active-time-interval")
      current_time_intervals.push([startHour, (startHour + 1) % 24])
    }
  
    if (current_time_intervals.length == 0) {
      removeAll(".free-computers-text")
      removeAll("#free-computers-row")
      removeAll("#commit-booking")

      document.getElementById("booking-section").appendChild(get_error_p("Не найдено свобоных компьютеров"))
      return
    }

    $.ajax({
      method: "POST",
      url: CLUB_DETAILS_URL,
      data: {
        "csrfmiddlewaretoken": CSRF_TOKEN,
        "action": "get-free-computers",
        "time_intervals": current_time_intervals.flat(),
        "booking_year": current_booking_date[0],
        "booking_month": current_booking_date[1],
        "booking_day": current_booking_date[2],
      },
      dateType: "json",
      success: data => {
        removeAll(".free-computers-text")
        removeAll("#free-computers-row")
        removeAll("#commit-booking")

        if (data["computer_orders"].length == 0) {
          document.getElementById("booking-section").appendChild(get_error_p("Не найдено свобоных компьютеров"))
          return
        }

        let bookingSection = document.getElementById("booking-section")

        let freeComputersText = document.createElement("p")
        freeComputersText.setAttribute("class", "free-computers-text")
        freeComputersText.setAttribute("id", "free-computers-text")
        freeComputersText.textContent = "Свободные компьютеры"
        bookingSection.appendChild(freeComputersText)

        let rowDiv = document.createElement("div")
        rowDiv.setAttribute("class", "row")
        rowDiv.setAttribute("id", "free-computers-row")

        for (let i = 0; i < data["computer_orders"].length; i++) {
          let computerBtnWrapper = document.createElement("div")
          computerBtnWrapper.setAttribute("class", "col-4 col-md-3 col-xl-3")

          let computerBtn = document.createElement("button")
          computerBtn.setAttribute("id", "computer-btn-" + data["computer_orders"][i].toString())
          computerBtn.setAttribute("class", "computer-btn")
          computerBtn.textContent = data["computer_orders"][i].toString()

          computerBtnWrapper.appendChild(computerBtn)
          rowDiv.appendChild(computerBtnWrapper)
        }

        document.getElementById("booking-section").appendChild(rowDiv)

        let commitBooking = document.createElement("button")
        commitBooking.setAttribute("class", "commit-booking")
        commitBooking.setAttribute("id", "commit-booking")
        commitBooking.textContent = "Подтвердить"
        document.getElementById("booking-section").appendChild(commitBooking)
      },
      error: (xhr, errmsg, err) => {
        document.getElementById("booking-section").appendChild(get_error_p("Не найдено свобоных компьютеров"))
      }
    })
  })

  document.addEventListener("click", e => {
    if (!e.target.matches(".computer-btn") && e.target.closest(".computer-btn") == null) return

    let computerOrder = e.target.id.split("-")[e.target.id.split("-").length - 1]
    let computerBtn = document.getElementById(e.target.id)
    if (computerBtn.classList.contains("active-computer-btn")) {
      computerBtn.classList.remove("active-computer-btn")
      current_computer_orders = current_computer_orders.filter(item => item !== computerOrder)
    }
    else {
      computerBtn.classList.toggle("active-computer-btn")
      current_computer_orders.push(computerOrder)
    }
  })
  
  document.addEventListener("click", e => {
    if (!e.target.matches("#commit-booking") && e.target.closest("#commit-booking") == null) return

    if (current_computer_orders.length === 0) {
      document.getElementById("booking-section").insertBefore(get_error_p("Выберите номера компьютеров"), document.getElementById("commit-booking"))
      return
    }

    $.ajax({
      method: "POST",
      url: CLUB_DETAILS_URL,
      data: {
        "csrfmiddlewaretoken": CSRF_TOKEN,
        "action": "commit-booking",
        "time_intervals": current_time_intervals.flat(),
        "booking_year": current_booking_date[0],
        "booking_month": current_booking_date[1],
        "booking_day": current_booking_date[2],
        "computer_orders": current_computer_orders,
      },
      dataType: "json",
      success: data => {
        let bookingSection = document.getElementById("booking-section")
        if (data["has_errors"]) {
          bookingSection.insertBefore(get_error_p(data["error_message"]), document.getElementById("commit-booking"))
          return
        }

        removeAll("#date-input-wrapper")
        removeAll("#time-intervals-row")
        removeAll("#free-computers-text")
        removeAll("#free-computers-row")
        removeAll("#commit-booking")

        bookingSection.appendChild(get_success_p("Запись была успешно добавлена"))
        
        let createBookingBtn = document.createElement("button")
        createBookingBtn.setAttribute("id", "booking-btn")
        createBookingBtn.setAttribute("class", "booking-btn")
        createBookingBtn.textContent = "Забронировать"

        bookingSection.appendChild(createBookingBtn)

        current_booking_date = [-1, -1, -1]
        current_time_intervals = []
        current_computer_orders = []
      },
      error: (xhr, errmsg, err) => {
        document.getElementById("booking-section").insertBefore(get_error_p("Произошла ошибка"), document.getElementById("#commit-booking"))
        current_booking_date = [-1, -1, -1]
        current_time_intervals = []
        current_computer_orders = []
      }
    })
  })