//! 重複使用的全域變數
const indicatorBar = document.querySelector('.attraction-page__carousel__indicators')

// 抓景點id
function getAttractionIdFromURL() {
    const pathArray = window.location.pathname.split('/');
    const attractionId = pathArray[pathArray.length - 1];

    // 驗證是否為有效的 ID
    if (!attractionId || isNaN(attractionId)) {
        console.error('無效的景點 ID');
        return null;
    }
    
    return parseInt(attractionId);
}

// 景點資訊動態渲染
function renderAttractionDetail(attractionDetail){
    const gallery = document.querySelector(".attraction-page__slides_gallery")
    // 渲染幻燈片及指示器
    attractionDetail.images.forEach((url, idx)=>{
        const slide = document.createElement('li')
        slide.className = 'attraction-page__slide'
        if (idx === 0) slide.dataset.active = true

        const slidePhoto = new Image()
        slidePhoto.className = 'attraction-page__slide__photo'
        slidePhoto.src = url
        slidePhoto.alt = `${attractionDetail.name}第${idx+1}張照片`

        slide.appendChild(slidePhoto)
        gallery.appendChild(slide)

        const indicator = document.createElement('button')
        indicator.role = "tab"
        indicator.ariaLabel = `第${idx+1}張`
        if (idx === 0) indicator.ariaSelected = true
        indicator.dataset.slide = idx
        indicatorBar.appendChild(indicator)
    })

    // 渲染其他文字細節
    const attractionName = document.querySelector('.attraction-page__name')
    attractionName.textContent = attractionDetail.name
    attractionName.dataset.id = attractionDetail.id

    const attractionCategory = document.querySelector('.attraction-page__category')
    attractionCategory.textContent = attractionDetail.category

    const attractionMrt = document.querySelector('.attraction-page__mrt')
    attractionMrt.textContent = attractionDetail.mrt

    const attractionDesc = document.querySelector('.attraction-page__description > p')
    attractionDesc.textContent = attractionDetail.description

    const attractionAddr = document.querySelector('.attraction-page__detail__address')
    attractionAddr.textContent = attractionDetail.address

    const attractionTrasport = document.querySelector('.attraction-page__detail__transport')
    attractionTrasport.textContent = attractionDetail.transport
}


//費用切換計算
const timeInputs = document.querySelectorAll('input[name="book-time"]')
const feeDisplay = document.querySelector('.attraction-page__booking-fee__total')

timeInputs.forEach(input => {
    input.addEventListener('change', (e) => {
        const price = e.target.dataset.price;
        feeDisplay.textContent = `新台幣 ${price} 元`;
    });
});


// ======== 點擊左右切換幻燈片 ========
function initSlideShow(){
    const buttons = document.querySelectorAll("[data-carousel-button]")
    buttons.forEach(button => {
        button.addEventListener('click', ()=>{
            const offset = button.dataset.carouselButton === "next" ? 1 : -1
            const slides = button
                .closest("[data-carousel]")
                .querySelector("[data-slides]")
    
            const activeSlide = slides.querySelector("[data-active]")
            let newIndex = [...slides.children].indexOf(activeSlide) + offset
            if (newIndex < 0) newIndex = slides.children.length - 1
            if (newIndex >= slides.children.length) newIndex = 0
    
            slides.children[newIndex].dataset.active = true
            delete activeSlide.dataset.active
    
            const indicatorBar = document.querySelector('.attraction-page__carousel__indicators')
            const selectIndicator = indicatorBar.querySelector('[aria-selected="true"]')
            indicatorBar.children[newIndex].ariaSelected = true
            selectIndicator.ariaSelected = false
        })
    })
}


// ======== 點擊指示器直接跳到對應幻燈片 ========
function initIndicatorEventListener(){
    indicatorBar.addEventListener('click', (e)=>{

        if (!e.target.matches('button')) return //如果點到容器而不是按鈕就退出

        const selectedIndex = e.target.dataset.slide
        
        const slides = e.target
            .closest('[data-carousel]')
            .querySelector('[data-slides]')

        const activeSlide = slides.querySelector("[data-active]")

        slides.children[selectedIndex].dataset.active = true
        delete activeSlide.dataset.active

        const selectIndicator = document.querySelector('[aria-selected="true"]')
        e.target.ariaSelected = true
        selectIndicator.ariaSelected = false
    })
}

// 初始化渲染及事件監聽代理綁定
async function attractionPageInit(){
    const rawData = await fetchData(`/api/attraction/${getAttractionIdFromURL()}`)

    if (rawData) {

        imagesPreload(rawData.data.images)
            .then((result)=>console.log(`全部圖片預載成功🎊 ,${result}`))
            .catch((error)=>console.error(`有圖片預載失敗🫠 ,${error}`))
        
        renderAttractionDetail(rawData.data)
        console.log("頁面渲染完成")
    }

    initSlideShow()

    initIndicatorEventListener()
}
attractionPageInit()

//! week5 範圍
const bookingForm = document.querySelector(".attraction-page__booking-form")
bookingForm.addEventListener("submit",async(e)=>{
    e.preventDefault()
    const user = await checkUserStates()
    if (!user){
        dialogs.login.showModal()
        return
    }
    try{
        const bookingSuccess = await sendBookingRequest()
        if (bookingSuccess){
            window.location.assign("/booking")
        }
    }catch(err){
        console.error(err)
        alert(err.message)
    }
})