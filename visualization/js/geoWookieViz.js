//Use data binding to construct a common html table

//Use data binding to construct a bar chart for each data point. Layout the single bar charts in a simple grid. There is no need for axes or text information.
function billy() {
  console.log("importing")
  var filename = 'csv/result_stat.csv';
//   d3.csv(filename, function(error, data) {
//     data.forEach(function(d) {
//         d.date = parseDate(d.Hour);
//         d.T = +d.T;
//     });
// });

   if (window.File && window.FileReader && window.FileList && window.Blob) {
    // Great success! All the File APIs are supported.
  } else {
    alert('The File APIs are not fully supported in this browser.');
  } 
}
  function handleFileSelect(evt) {
    var files = evt.target.files; // FileList object

    // files is a FileList of File objects. List some properties.
    var output = [];
    for (var i = 0, f; f = files[i]; i++) {
      output.push('<li><strong>', escape(f.name), '</strong> (', f.type || 'n/a', ') - ',
                  f.size, ' bytes, last modified: ',
                  f.lastModifiedDate ? f.lastModifiedDate.toLocaleDateString() : 'n/a',
                  '</li>');
    }
    document.getElementById('list').innerHTML = '<ul>' + output.join('') + '</ul>';
  }
function findSize(file) {
    var fileInput = file; 
    try{
        alert(fileInput.files[0].size); // Size returned in bytes.
    }catch(e){
        var objFSO = new ActiveXObject("Scripting.FileSystemObject");
        var e = objFSO.getFile( fileInput.value);
        var fileSize = e.size;
        alert(fileSize);    
    }
}

function processResultStat(data) {
}
function buildCharts() {
      var piedata = [
        {key: "One", y: 5},
        {key: "Two", y: 2},
        {key: "Three", y: 9},
        {key: "Four", y: 7},
        {key: "Five", y: 4},
        {key: "Six", y: 3},
        {key: "Seven", y: 0.5}
    ];
        var barchartdata =[
  {
    key: "Cumulative Return",
    values: [
      { 
        "label" : "A" ,
        "value" : -29.765957771107
      } , 
      { 
        "label" : "B" , 
        "value" : 0
      } , 
      { 
        "label" : "C" , 
        "value" : 32.807804682612
      } , 
      { 
        "label" : "D" , 
        "value" : 196.45946739256
      } , 
      { 
        "label" : "E" ,
        "value" : 0.19434030906893
      } , 
      { 
        "label" : "F" , 
        "value" : -98.079782601442
      } , 
      { 
        "label" : "G" , 
        "value" : -13.925743130903
      } , 
      { 
        "label" : "H" , 
        "value" : -5.1387322875705
      }
    ]
  }
]
 

            var height = 350;
    var width = 450;
    var chart1;
    nv.addGraph(function() {
        var chart1 = nv.models.pieChart()
            .x(function(d) { return d.key })
            .y(function(d) { return d.y })
            .donut(true)
            .width(width)
            .height(height)
            .padAngle(.08)
            .cornerRadius(10)
            .id('donut1'); // allow custom CSS for this one svg
        chart1.title("Results");
        chart1.pie.donutLabelsOutside(true).donut(true);
        d3.select("#piechart")
            .datum(piedata)
            .transition().duration(1200)
            .call(chart1);
        return chart1;
    });
nv.addGraph(function() {
  var chart = nv.models.discreteBarChart()
    .x(function(d) { return d.label })
    .y(function(d) { return d.value })
    .staggerLabels(true)
//    .tooltips(false)
    .showValues(true)

  d3.select('#barchart')
    .datum(barchartdata)
    .transition().duration(500)
    .call(chart)
    ;

  nv.utils.windowResize(chart.update);

  return chart;
});


}
// function buildPieChart(dataPoints) {
//         'use strict';

//         var dataset = [
//           { label: 'Abulia', count: 10 }, 
//           { label: 'Betelgeuse', count: 20 },
//           { label: 'Cantaloupe', count: 30 },
//           { label: 'Dijkstra', count: 40 }
//         ];

//         var width = 360;
//         var height = 360;
//         var radius = Math.min(width, height) / 2;

//         var color = d3.scale.category20b();

//         var svg = d3.select('#chart')
//           .append('svg')
//           .attr('width', width)
//           .attr('height', height)
//           .append('g')
//           .attr('transform', 'translate(' + (width / 2) + 
//             ',' + (height / 2) + ')');

//         var arc = d3.svg.arc()
//           .outerRadius(radius);

//         var pie = d3.layout.pie()
//         //   .value(function(d) { return d.count; })
//         //   .sort(null);

//         // var path = svg.selectAll('path')
//         //   .data(pie(dataset))
//         //   .enter()
//         //   .append('path')
//         //   .attr('d', arc)
//         //   .attr('fill', function(d, i) { 
//         //     return color(d.data.label);
//         // });
// }

function start()
{                
    buildCharts();
    billy();
    console.log("==========");
}

