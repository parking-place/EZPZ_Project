/*  =============================================
    검색 관련 함수
    =============================================*/
    function search_method() {
        keyword = document.search_form.q.value;
        
        // 아무것도 입력되지 않은 경우
        if(!keyword){
            return;
        }
        document.search_form.action = "/";
        document.search_form.submit();
    }
    
/*  =============================================
    기타 공통 버튼 
    =============================================*/
// 더보기 버튼
function show_details(cont_tag_id){
    $(cont_tag_id).css('height', 'auto');
    $('#details_box').css('display', 'none');
}