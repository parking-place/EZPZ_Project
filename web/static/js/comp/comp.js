// ========================================
// Chart 관련
// ========================================

function go_chart(pos, neg, neu){
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
            responsive: false,
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

// 더보기 버튼 클릭시
function show_details(){
    $('.comp_news').css('height', 'auto');
    $('#details_box').css('display', 'none');
}

function add_nbsp(el){
    const nbsp = document.createTextNode("\u00a0");
    if($(el).css('height') == '24px'){
        $(el).append('<br>');
        $(el).append(nbsp);
    }
}

// 이벤트 삽입 외엔 document ready 사용하지 않습니다.
$(document).ready(function(){
    $.each($('.news_cont > p'), function(){
        add_nbsp(this);
    })
});