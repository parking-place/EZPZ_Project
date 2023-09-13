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
            ctx.fillText(value, 25, 280);
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
            responsive: true
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
    const line_graph = new Chart(el, config); // draw
}

function chart_resize(){
    if(window.innerWidth <= 768){
        width = $('#reivew_cont').css('width');
    }else{
        width = innerWidth / 2.5;
    }
    $('#chart_container').css('width', width);
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
