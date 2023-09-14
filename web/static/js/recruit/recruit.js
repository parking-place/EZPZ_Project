function add_nbsp(el){
    const nbsp = document.createTextNode("\u00a0"); 
    const br = document.createElement("br");
    height = el.clientHeight;
    
    // 120보다 작은 경우에만
    if (142 - height > 0){
        line = (142 - height) / 24; // 추가해야할 p태그 개수

        // 줄바꿈 추가(5줄 포맷)
        for(i=0; i < line; i++){
            el.appendChild(br);
            el.appendChild(nbsp);
        }
    }
}

// 이벤트 삽입 외엔 document ready 사용하지 않습니다.
document.addEventListener("DOMContentLoaded", function(){
    const infos = document.querySelectorAll('.recruit_info');
    const texts = document.querySelectorAll('.recruit_info > div');

    infos.forEach((info) => {
        info.addEventListener('click', function(){
            window.open("https://www.wanted.co.kr/wd/" + this.getAttribute('id'));
        });
    })
    texts.forEach((text) => {
        add_nbsp(text);
    });
});
