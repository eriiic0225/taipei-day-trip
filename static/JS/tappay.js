TPDirect.setupSDK(166471, 'app_754GkYarsLk09eOWINBA6JoIGC4k06qPAR1EA7zk2a7dhJ0EbmPjBeU9R8Br', 'sandbox')

const fields = {
        number: {
            // css selector
            element: '#card-number',
            placeholder: '**** **** **** ****'
        },
        expirationDate: {
            // DOM object
            element: document.getElementById('card-expiration-date'),
            placeholder: 'MM / YY'
        },
        ccv: {
            element: '#card-ccv',
            placeholder: 'CCV'
        }
    }

TPDirect.card.setup({
    // Display ccv field
    fields: fields,
    styles: {
        // Style all elements
        'input': {
            'color': 'gray'
        },
        // Styling ccv field
        'input.ccv': {
            // 'font-size': '16px'
        },
        // Styling expiration-date field
        'input.expiration-date': {
            // 'font-size': '16px'
        },
        // Styling card-number field
        'input.card-number': {
            // 'font-size': '16px'
        },
        // style focus state
        ':focus': {
            // 'color': 'black'
        },
        // style valid state
        '.valid': {
            'color': 'green'
        },
        // style invalid state
        '.invalid': {
            'color': 'red'
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        '@media screen and (max-width: 400px)': {
            'input': {
                'color': 'orange'
            }
        }
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11
    }
})

const submitButton = document.querySelector(".booking__total__confirm-btn")
TPDirect.card.onUpdate((update) => {
    // update.canGetPrime === true
    // --> you can call TPDirect.card.getPrime()
    if (update.canGetPrime) {
        // Enable submit Button to get prime.
        submitButton.removeAttribute('disabled')
    } else {
        // Disable submit Button to get prime.
        submitButton.setAttribute('disabled', true)
    }
})


function onSubmit(event) {
    event.preventDefault()
    submitButton.setAttribute('disabled', true)

    // 取得 TapPay Fields 的 status
    const tappayStatus = TPDirect.card.getTappayFieldsStatus()

    // 確認是否可以 getPrime
    if (tappayStatus.canGetPrime === false) {
        alert('can not get prime')
        return
    }

    // Get prime
    TPDirect.card.getPrime(async (result) => {
        if (result.status !== 0) {
            console.log('get prime error ' + result.msg)
            return
        }
        console.log('get prime 成功，prime: ' + result.card.prime)

        // contact 欄位檢查

        // send prime to your server, to pay with Pay by Prime API .
        // Pay By Prime Docs: https://docs.tappaysdk.com/tutorial/zh/back.html#pay-by-prime-api
        const bookingInfo = JSON.parse(sessionStorage.getItem("booking-info"))
        // console.log(bookingInfo)
        const payload = {
            "prime": result.card.prime,
            "order": {
                "price": bookingInfo.price,
                "trip": {
                    "attraction": {
                        "id": bookingInfo.attraction.id,
                        "name": bookingInfo.attraction.name,
                        "address": bookingInfo.attraction.address,
                        "image": bookingInfo.attraction.image
                    },
                    "date": bookingInfo.date,
                    "time": bookingInfo.time
                },
                "contact": {
                    "name": document.querySelector(".contact__field input[name='name']").value,
                    "email": document.querySelector(".contact__field input[name='email']").value,
                    "phone": document.querySelector(".contact__field input[name='phone']").value
                }
            }
        }
        try{
            // 打 orders API (POST)
            const result = await authApiCall("/api/orders", "POST", payload)
            console.log(result)
            if (result.error){
                alert(`操作失敗`, result.message)
                submitButton.removeAttribute('disabled')
                return
            }
            location.assign(`/thankyou?number=${result.data.number}`)
        }catch(error){
            console.error("呼叫 API 發生錯誤:", error)
            alert("系統繁忙，請稍後再試")
            submitButton.removeAttribute('disabled')
        }
    })
}

const orderFrom = document.querySelector("#orderForm")
orderFrom.addEventListener("submit",onSubmit)
