/**
* Template Name: Kelly
* Updated: Jul 27 2023 with Bootstrap v5.3.1
* Template URL: https://bootstrapmade.com/kelly-free-bootstrap-cv-resume-html-template/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Scrolls to an element with header offset
   */
  const scrollto = (el) => {
    let header = select('#header')
    let offset = header.offsetHeight

    let elementPos = select(el).offsetTop
    window.scrollTo({
      top: elementPos - offset,
      behavior: 'smooth'
    })
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    select('#navbar').classList.toggle('navbar-mobile')
    this.classList.toggle('bi-list')
    this.classList.toggle('bi-x')
  })

  /**
   * Scrool with ofset on links with a class name .scrollto
   */
  on('click', '.scrollto', function(e) {
    if (select(this.hash)) {
      e.preventDefault()

      let navbar = select('#navbar')
      if (navbar.classList.contains('navbar-mobile')) {
        navbar.classList.remove('navbar-mobile')
        let navbarToggle = select('.mobile-nav-toggle')
        navbarToggle.classList.toggle('bi-list')
        navbarToggle.classList.toggle('bi-x')
      }
      scrollto(this.hash)
    }
  }, true)

  /**
   * Scroll with ofset on page load with hash links in the url
   */
  window.addEventListener('load', () => {
    if (window.location.hash) {
      if (select(window.location.hash)) {
        scrollto(window.location.hash)
      }
    }
  });

  /**
   * Preloader
   */
  let preloader = select('#preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      preloader.remove()
    });
  }

  /**
   * Animation on scroll
   */
  window.addEventListener('load', () => {
    AOS.init({
      duration: 1000,
      easing: "ease-in-out",
      once: true,
      mirror: false
    });
  });

  /**
   * Initiate Pure Counter 
   */
  new PureCounter();

})()

const dnct1 = document.getElementById('myChart');

const data = {
  labels: [' 긍정', ' 부정', ' 중립'],
  datasets: [{
    label: 'Sentiments Ratio',
    data: [510, 887, 720],
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

const myChart = new Chart(dnct1, {
  type: 'pie',
  data: data,
  options: options,
  plugins: [ChartDataLabels]
});