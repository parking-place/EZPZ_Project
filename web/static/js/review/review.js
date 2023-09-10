// 리뷰 페이지 내 세부 탭 이동
function go_page(type, comp_uid){
    if(type && type=='half'){
        document.location = '/review/half?comp_uid=' + comp_uid;
    } else if(type && type=='quart'){
        document.location = '/review/quarter?comp_uid=' + comp_uid;
    }
}

// 더보기 버튼 클릭 시
function show_details(){
    $('.review_cont').css('height', 'auto');
    $('#details_box').css('display', 'none');
}

/*  ========================================
    Graph 관련
    ======================================== */
// hoverValue : show keyword animation
const hoverValue = {
    id: 'hoverValue',
    afterDatasetsDraw(chart, args, pluginOptions) {
        const { ctx, data, options } = chart;
        chart.getActiveElements().forEach((active) => {
            value = '키워드 : ' + time_keywords[active.index];
            ctx.fillText(value, window.innerWidth * 0.02, 280);
        })
    }
}

// chart drawing function
function draw_chart(cols, rate){
    const data = {
        labels: cols,
        datasets: [
            {
                label: '평균 별점'
                , data: rate
                , borderColor : 'skyblue'
            }
        ]
    };

    const config = {
        type: 'line'
        , data: data
        , options: {
            responsive: false
            , plugins: {
                legend: { display: false }
                , title: {
                    display: true,
                    text: '리뷰 통계'
                }
            }
            , scales: {
                x: { display: false }
                , y: {
                    suggestedMin: 0
                    , suggestedMax: 5
                    , ticks: { stepSize: 1 }
                }
            }
        }
        , plugins: [hoverValue]
    };
    const el = document.getElementById('review_chart'); // 차트 들어갈 element
    const pieChart = new Chart(el, config);
}

/*  ========================================
    Wordcloud 관련
    ======================================== */
function draw_word_cloud(data){
    var chart = anychart.tagCloud(data);
    chart.angles([0]);
    chart.container("review_word_cloud");
    chart.draw();
}
