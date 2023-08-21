const dnct1 = document.getElementById('pieChart');

const data = {
  labels: [' 긍정', ' 부정', ' 중립'],
  datasets: [{
    label: 'Sentiments Ratio',
    data: [1234, 456, 789],
    backgroundColor: ['skyblue', 'pink', 'lightgrey'],
    borderColor: '#fff',
    borderWidth: 3,
    hoverOffset: 5,
    cutout: 0
  }]
};

const options = {
  responsive: false,
  layout: {
    padding: {
      bottom: 25
    }
  },
  plugins: {
    tooltip: {
      enabled: true,
      callbacks: {
        footer: (ttItem) => {
          let sum = 0;
          let dataArr = ttItem[0].dataset.data;
          dataArr.map(data => {
            sum += Number(data);
          });
          let percentage = (ttItem[0].parsed * 100 / sum).toFixed(2) + ' %';
          return `비율: ${percentage}`;
        }
      }
    },
    datalabels: {
      formatter: (value, dnct) => {
        let sum = 0;
        let dataArr = dnct.chart.data.datasets[0].data;
        dataArr.map(data => {
          sum += Number(data);
        });
        let percentage = (value * 100 / sum).toFixed(2) + ' %';
        return percentage;
      },
      color: 'darkslategray',
    }
  }
};

const pieChart = new Chart(dnct1, {
  type: 'pie',
  data: data,
  options: options,
  plugins: [ChartDataLabels]
});