function add_nbsp(el){
    const nbsp = document.createTextNode("\u00a0");
    const br = document.createElement("br");

    if(el.clientHeight == 24){
        el.appendChild(br);
        el.appendChild(nbsp);
    }
}

function go_external_page(url){
    if(!url || url == 'https://'){
        window.alert('홈페이지 바로가기가 지원되지 않는 기업입니다.');
        return;
    }

    window.open(url);
}

// 이벤트 삽입 외엔 document ready 사용하지 않습니다.
document.addEventListener('DOMContentLoaded', function(){
    const conts = document.querySelectorAll('.news_cont');
    const texts = document.querySelectorAll('.news_cont > p');
    
    conts.forEach((cont) => {
        cont.addEventListener('click', function(){
            go_external_page(cont.getAttribute('data'));
        });
    });
    texts.forEach((text) => {
        add_nbsp(text);
    });
});



/*  ========================================
    PieChart 관련
    ======================================== */
function draw_chart(pos, neg, neu){
    const data = {
        labels: ['긍정적', '부정적', '중립적'],
        datasets: [
            {
                data: [pos, neg, neu]
                , backgroundColor: ['skyblue', 'pink', 'lightgrey']
            }
        ]
    };
    const config = {
        type: 'pie',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: '최근 뉴스 동향'
                }
            }
        }
    };
    const el = document.getElementById('pieChart'); // 차트 들어갈 element
    const pieChart = new Chart(el, config);
}
