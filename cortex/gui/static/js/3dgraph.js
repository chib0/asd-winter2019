
// This was taken from an example on highgraphs
function getChartForData(data) {// Give the points a 3D feel by adding a radial gradient
  let listData = data.map((dict) => [dict.x, dict.y, dict.z]);
  let maxes = {x: Number.NEGATIVE_INFINITY, y: Number.NEGATIVE_INFINITY, z: Number.NEGATIVE_INFINITY};
  let mins = {x: Number.POSITIVE_INFINITY, y: Number.POSITIVE_INFINITY, z: Number.POSITIVE_INFINITY};

  ['x', 'y', 'z'].forEach((axis) => data.forEach((dict) => {
    maxes[axis] = Math.max(maxes[axis], dict[axis]);
    mins[axis] = Math.min(mins[axis], dict[axis]);
  }));
  console.log(mins);
  console.log(maxes);
  Highcharts.setOptions({
    colors: Highcharts.getOptions().colors.map(function (color) {
      return {
        radialGradient: {},
        stops: [
          [0, color],
          [1, Highcharts.color(color).get('rgb')]
        ]
      };
    })
  });

// Set up the chart
  var chart = new Highcharts.Chart({
    chart: {
      renderTo: 'container',
      margin: 100,
      type: 'scatter3d',
      animation: false,
      options3d: {
        enabled: true,
        alpha: 10,
        beta: 30,
        depth: 250,
        viewDistance: 5,
        fitToPlot: false,
        frame: {
          bottom: {size: 1, color: 'rgba(0,0,0,0.02)'},
          back: {size: 1, color: 'rgba(0,0,0,0.04)'},
          side: {size: 1, color: 'rgba(0,0,0,0.06)'}
        }
      }
    },
    title: {
      text: 'Location box'
    },
    subtitle: {
      text: 'Click and drag the plot area to rotate in space'
    },
    plotOptions: {
      scatter: {
        width: 10,
        height: 10,
        depth: 10
      }
    },
    yAxis: {
      min: mins.y,
      max: maxes.y,
      title: null
    },
    xAxis: {
      min: mins.x,
      max: maxes.x,
      gridLineWidth: 1
    },
    zAxis: {
      min: mins.z,
      max: maxes.z,
      showFirstLabel: false
    },
    legend: {
      enabled: false
    },
    series: [{
      name: 'Data',
      colorByPoint: true,
      accessibility: {
        exposeAsGroupOnly: true
      },
      data: listData
    }]
  });


// Add mouse and touch events for rotation
  (function (H) {
    function dragStart(eStart) {
      eStart = chart.pointer.normalize(eStart);

      var posX = eStart.chartX,
          posY = eStart.chartY,
          alpha = chart.options.chart.options3d.alpha,
          beta = chart.options.chart.options3d.beta,
          sensitivity = 5,  // lower is more sensitive
          handlers = [];

      function drag(e) {
        // Get e.chartX and e.chartY
        e = chart.pointer.normalize(e);

        chart.update({
          chart: {
            options3d: {
              alpha: alpha + (e.chartY - posY) / sensitivity,
              beta: beta + (posX - e.chartX) / sensitivity
            }
          }
        }, undefined, undefined, false);
      }

      function unbindAll() {
        handlers.forEach(function (unbind) {
          if (unbind) {
            unbind();
          }
        });
        handlers.length = 0;
      }

      handlers.push(H.addEvent(document, 'mousemove', drag));
      handlers.push(H.addEvent(document, 'touchmove', drag));


      handlers.push(H.addEvent(document, 'mouseup', unbindAll));
      handlers.push(H.addEvent(document, 'touchend', unbindAll));
    }

    H.addEvent(chart.container, 'mousedown', dragStart);
    H.addEvent(chart.container, 'touchstart', dragStart);
  }(Highcharts));

}