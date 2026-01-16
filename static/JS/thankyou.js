// 從網址取得訂單編號
function getOrderNumberFromURL(){
    const url = new URL(window.location.href);
    const params = url.searchParams;
    return params.get('number')
}

document.addEventListener("DOMContentLoaded", async()=>{
    const user = await checkUserStates()
    if (!user){
        window.location.assign("/")
    }

    document.querySelector(".order__user-name").textContent = user.name

    const orderNumber = getOrderNumberFromURL()
    const orderInfo = await authApiCallGet(`/api/order/${orderNumber}`, "GET")
    console.log(orderInfo)
    if (orderInfo.data.status === 1) {
        renderOrderDetail(orderInfo.data)
    }else{
        location.assign("/booking")
    }
});

function renderOrderDetail(data){
    document.querySelector(".order-number").textContent = data.number
    
    document.querySelector(".booking__attraction__pic img").src = data.trip.attraction.image
    document.querySelector(".booking__attraction__pic img").alt = data.trip.attraction.name
    document.querySelector(".order__attraction__title span").textContent = data.trip.attraction.name
    document.querySelector(".booking__date").textContent = data.trip.date
    document.querySelector(".booking__time").textContent = 
        data.trip.time === "morning"? "早上 9 點到下午 4 點" : "下午 2 點到晚上 9 點"
    document.querySelector(".booking__price").textContent = `新台幣 ${data.price} 元`
    document.querySelector(".booking__address").textContent = data.trip.attraction.address
}