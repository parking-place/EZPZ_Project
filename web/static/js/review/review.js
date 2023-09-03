// ========================================
// Sub_detail_menu 관련
// ========================================
/*
function openMenu(evt, menuName) {
    var i, tabcontent, tablinks;

    // 1. 모든 탭 컨텐츠 숨기기.
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    
    // 2. 모든 버튼에서 active 클래스 제거.
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace("active", "");
    }

    // 3. 선택된 메뉴와 관련된 탭 컨텐츠를 보여주고 버튼에 active 클래스 추가.
    // 3-1. 현재 클릭한 클래스 이름에 active 클래스 없으면 참이라 {...}안에있는 조건문 실행. " "공백을 넣어야지 내가 원하는대로 나옴. 
    document.getElementById(menuName).style.display = "block";
    if (!evt.currentTarget.classList.contains('active')) {
        evt.currentTarget.className += " active";
    }
}

// 4. 첫 번째 탭을 기본적으로 열어줍니다.
document.addEventListener('DOMContentLoaded', function() {
    document.getElementsByClassName('tablinks')[0].click();
});
*/
function go_page(type, comp_uid){
    if(type && type=='half'){
        document.location = '/reivew/half?comp_uid=' + comp_uid;
    } else if(type && type=='quart'){
        document.location = '/review/quarter?comp_uid=' + comp_uid;
    }
}
// ========================================
// Graph 관련
// ========================================


// ========================================
// Wordcloud 관련
// ========================================
