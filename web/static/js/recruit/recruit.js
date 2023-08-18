// 이벤트 삽입 외엔 document ready 사용하지 않습니다.
$(document).ready(function(){
    $(".recruit_info").click(function () {
        window.open("https://www.wanted.co.kr/wd/" + $(this).attr("id"));
    });
});
