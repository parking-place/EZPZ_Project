// 이벤트 삽입 외엔 document ready 사용하지 않습니다.
function add_p_tag(el){
    const nbsp = document.createTextNode("\u00a0"); 
    height = $(el).css('height');
    height = height.substring(0, (height.length - 2));
    
    // 120보다 작은 경우에만
    if (120 - height){
        line = (120 - height) / 24; // 추가해야할 p태그 개수

        // 줄바꿈 추가(5줄 포맷)
        for(i=0; i < line; i++){
            $(el).append('<br>');
            $(el).append(nbsp);
        }
    }
}

// 이벤트 삽입 외엔 document ready 사용하지 않습니다.
$(document).ready(function(){
    $(".recruit_info").click(function () {
        window.open("https://www.wanted.co.kr/wd/" + $(this).attr("id"));
    });
    $.each($('.recruit_cont_box > div'), function(){
        add_p_tag(this);
    });
});
