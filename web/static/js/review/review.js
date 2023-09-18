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
            
            if(chart.width <= 446){
                ctx.fillText(value, (chart.width / 10), (chart.height * 0.95));
            }else{
                ctx.fillText(value, (chart.width / 20), (chart.height * 0.9));
            }
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

/*  ========================================
    Wordcloud 관련
    ======================================== */
function draw_word_cloud(data){
    var chart = anychart.tagCloud(data);
    chart.angles([0]);
    chart.container("review_word_cloud");
    chart.draw();
}
