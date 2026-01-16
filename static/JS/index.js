//! ============ 全域變數 ============ 
let nextPage = null  // 保存下一頁遊標
let isLoading = false // 防止無限滾動連續觸發
let currentCategory = "" // 空字串 = 全部分類
let currentKeyword = ""

//! ============ DOM 元素 ============ 
const attractionsContainer = document.querySelector('.attractions') // card容器
const footer = document.querySelector('.footer__copy-right') // 哨兵元素
const catDrawer = document.querySelector(".category-dropdown__container") // cat容器(外)
const categoryMenu = document.querySelector(".category-dropdown__menu") // cat容器(內)
const filterDisplay = document.getElementById("category-dropdown__filter") // 目前選取的cat
const listSwitch = document.querySelector(".category-dropdown__trigger") // 展開cat按鈕
const searchInput = document.querySelector('.search-box__input') // keyword輸入框
const mrtList = document.querySelector('.carousel') // mrt容器


// ============ List bar 滾動 ============ 
const scrollContainer = document.querySelector(".carousel")
const backBtn = document.querySelector(".carousel__back-btn")
const nextBtn = document.querySelector(".carousel__next-btn")
const listBar = document.querySelector(".list-bar") 

listBar.addEventListener("wheel", (e)=>{
    e.preventDefault()
    scrollContainer.scrollLeft += e.deltaY
})

nextBtn.addEventListener("click",()=>{
    scrollContainer.scrollLeft += 200
})

backBtn.addEventListener("click",()=>{
    scrollContainer.scrollLeft -= 200
})

// ============ 類別清單展開 ＆ 條件更新 ============ 
// 點擊按鈕展開/收合
listSwitch.addEventListener("click", (e)=>{
    catDrawer.classList.toggle("category-dropdown__container--open")
})

// 點擊分類項目 --->> 更新條件/收回清單
categoryMenu.addEventListener("click", (e)=>{
    const item = e.target.closest(".category-dropdown__item")
    if (item){
        const selectedCategory = item.textContent
        filterDisplay.textContent = selectedCategory // 更新DOM顯示的類別

        // 更新全域變數
        currentCategory = item.dataset.category;  // 「全部分類」的 data-category=""

        catDrawer.classList.remove("category-dropdown__container--open")

        console.log("分類已更新，目前選取類別: ", currentCategory)
    }
})


// ============ 輸入框搜尋 ============ 
const searchBtn = document.querySelector('.search-box__btn')
searchBtn.addEventListener('click', (e) => {
    e.preventDefault();
    currentKeyword = searchInput.value.trim();
    newSearch();  // 搜尋分類 & 關鍵字
});


// ============ mrt 關鍵字查詢 ============
mrtList.addEventListener('click',(e)=>{
    const mrt = e.target.closest(".carousel__mrt")
    if (mrt){
        selectedMrt = mrt.textContent
        searchInput.value = selectedMrt

        currentKeyword = selectedMrt
        // trigger 搜尋
        newSearch()
    }
})

// ============ 景點渲染函式 ============ 
function renderCards(attractions){
    //week 5 加入圖片預加載機制
    const preloadPromises = attractions.map((item,idx)=>{
        const url = item.images[0]
        return ImgPreload(url)
            // .then(()=>console.log(`✅ 第${idx+1}張圖片加載成功`, url))
            .catch(()=>console.error(`❌ 第${idx+1}張圖片加載失敗`, url))
    })
    Promise.all(preloadPromises)
        .then(() => console.log('✅ 全部完成'))

    // 渲染
    attractions.forEach( item => {

        // 創造容器＆子元素
        const attraction_card = document.createElement('a')
        attraction_card.className = 'attraction__card'
        attraction_card.dataset.attractionId = item.id
        attraction_card.href = `/attraction/${item.id}`

        const attraction_card__content = document.createElement('div')
        attraction_card__content.className = 'attraction__card__content'

        const attraction_card__pic = document.createElement('img')
        attraction_card__pic.className = 'attraction__card__pic'
        attraction_card__pic.src = item.images[0]
        attraction_card__pic.alt = item.name

        const attraction_card__name = document.createElement('div')
        attraction_card__name.className = 'attraction__card__name'
        attraction_card__name.textContent = item.name

        const attraction_card__detail = document.createElement('div')
        attraction_card__detail.className = 'attraction__card__detail'

        const attraction_card__mrt = document.createElement('div')
        attraction_card__mrt.className = 'attraction__card__mrt'
        attraction_card__mrt.textContent = item.mrt

        const attraction_card__cat = document.createElement('div')
        attraction_card__cat.className = 'attraction__card__cat'
        attraction_card__cat.textContent = item.category

        // 組合元素
        attraction_card__content.appendChild(attraction_card__pic)
        attraction_card__content.appendChild(attraction_card__name)
        attraction_card__detail.appendChild(attraction_card__mrt)
        attraction_card__detail.appendChild(attraction_card__cat)
        attraction_card.appendChild(attraction_card__content)
        attraction_card.appendChild(attraction_card__detail)

        // 放進外框容器
        attractionsContainer.appendChild(attraction_card)
    });
}

// ============ Category渲染函式 ============ 
function renderCategories(categories){
    const container = document.querySelector('.category-dropdown__menu')
    // 清空除了「全部分類」外的項目
    const items = container.querySelectorAll('.category-dropdown__item');
    items.forEach((item, index) => {
        if (index > 0) item.remove();  // 保留第一個"全部分類"
    });

    categories.forEach(category =>{
        const categoryItem = document.createElement('li')
        
        categoryItem.className = 'category-dropdown__item'
        categoryItem.textContent = category
        categoryItem.dataset.category = category

        container.appendChild(categoryItem)
    })
}

// ============ Mrt List渲染函式 ============
function renderMrts(mrts){
    const container = document.querySelector('.carousel')
    mrts.forEach(mrt => {
        const mrtItem = document.createElement('li')
        mrtItem.className = 'carousel__mrt'
        mrtItem.textContent = mrt
        container.appendChild(mrtItem)
    })
}

// ============ 初始化(首次渲染) ============
async function init() {
    // 改為並行發送三個請求
    const [attractionsResult, catResult, mrtResult] = await Promise.all([
        fetchData('/api/attractions'),
        fetchData('/api/categories'),
        fetchData('/api/mrts')
    ])

    if (attractionsResult) {
        renderCards(attractionsResult.data);      // 渲染第一頁
        nextPage = attractionsResult.nextPage;    // 保存下一頁遊標
    }

    if (catResult) renderCategories(catResult.data);
    if (mrtResult) renderMrts(mrtResult.data);

}
init() // 記得立馬執行初始化



// ============ 加載下一頁(給infinite scroll用) ============ 
async function loadMore() {
    if (isLoading || !nextPage) return
    isLoading = true

    // 構建 URL：category 為空字串(全部分類)時不傳
    let url = `/api/attractions?page=${nextPage}`;
    if (currentCategory) {
        url += `&category=${currentCategory}`
    }
    if (currentKeyword) {
        url += `&keyword=${currentKeyword}`
    }

    const result = await fetchData(url)
    if (result){
        renderCards(result.data)
        nextPage = result.nextPage
        console.log(`成功載入更多頁面，下一頁：`,nextPage)
    }
    isLoading = false
}

// ============ 新搜尋（重置頁數和卡片） ============ 
async function newSearch(){
    // 1. 清空舊卡片
    attractionsContainer.innerHTML = ''

    const noResult = document.querySelector('.attraction__no-result')

    // 2. 重置 nextPage
    nextPage = null;

    // 3. 構建 URL（page=0 開始新搜尋）
    let url = '/api/attractions?page=0'
    if (currentCategory) url += `&category=${currentCategory}`
    if (currentKeyword) url += `&keyword=${currentKeyword}`

    const result = await fetchData(url)
    if (result?.data?.length > 0) {
        renderCards(result.data) // 渲染搜尋到的結果
        nextPage = result.nextPage // 在全域紀錄是否有下一頁
        console.log("新搜尋完成，下一頁:", nextPage)
        noResult.classList.remove('show'); 
    }else{
        noResult.classList.add('show');
    }
}

// ============ 監聽 Intersection Observer（無限滾動） ============
const observer = new IntersectionObserver((entries)=>{
    const entry = entries[0] // 只監聽footer一個元素所以取node list的第一個即可
    if (entry.isIntersecting && nextPage){ // 利用isIntersecting(判斷元素是否在rootmargin內)，
        loadMore()                           // 防止footer被向下推出視窗時二次觸發IntersectionObserver
    }
},{
    threshold: 0.3 // 當被監聽元素露出/消失 30% 時觸發
})
observer.observe(footer)