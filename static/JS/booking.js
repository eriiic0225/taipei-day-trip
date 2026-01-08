document.addEventListener("DOMContentLoaded", async()=>{
    const user = await checkUserStates()
    if (!user){
        window.location.assign("/")
    }

    document.querySelector(".booking__user-name").textContent = user.name

    const currentBooking = await authApiCallGet("/api/booking", "GET")
    if (!currentBooking.data) return
    renderBookingPageDetail(currentBooking.data)
});

function renderBookingPageDetail(bookingDetail){
    console.log(bookingDetail)
    const hasBookingElements = document.querySelectorAll(".no-booking")
    hasBookingElements.forEach(el=>{
        el.classList.remove("no-booking")
    })
    const noBookingElement = document.querySelector(".booking__no-booking-message")
    noBookingElement.classList.add("no-booking")

    document.querySelector(".booking__attraction__pic img").src = bookingDetail.attraction.image
    document.querySelector(".booking__attraction__pic img").alt = bookingDetail.attraction.name
    document.querySelector(".booking__attraction__title").textContent = `台北一日遊：${bookingDetail.attraction.name}`
    document.querySelector(".booking__date").textContent = bookingDetail.date
    document.querySelector(".booking__time").textContent = 
        bookingDetail.time === "morning"? "早上 9 點到下午 4 點" : "下午 2 點到晚上 9 點"
    document.querySelector(".booking__price").textContent = `新台幣 ${bookingDetail.price} 元`
    document.querySelector(".booking__total__price > span").textContent = bookingDetail.price
    document.querySelector(".booking__address").textContent = bookingDetail.attraction.address
}

async function cancelCurrentBooking() {
    const result = await authApiCallGet("/api/booking", "DELETE")
    if (result.ok){
        location.reload()
    }else{
        alert(`操作失敗：${result.message}`)
    }
}