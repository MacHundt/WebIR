//geoWookie visualization

// load file using file reader as blob
// preprocess blob
// turn blob into proper data format
// feed to charts 

var pieChartBlob;
var barChartBlob;
var processedPieData = [];
var processedBarData = [];
var accuracy = "Not Set";

function processPieBlob(text) {
  //process accuracy first
  var totLine = text[text.length-2].split(",");
  accuracy = (totLine[2] / totLine[1])*100 ;
  accuracy = accuracy.toString().substring(0,5).concat("%");

  // continue to the rest
  var startAt = 1;
  var endAt = 7;
  for (var i = startAt; i < endAt; i += 1) {
    var line = text[i].split(",");
    var countryName = line[0];
    var truePositives = line[1];
    console.log(line, countryName, truePositives);
    processedPieData.push({
      key: countryName,
      y: parseInt(truePositives)
    });
  }
}  

function processChartBlob(text) {
  var midRes = [];
  var startAt = 1;
  var endAt = text.length -1 ;
  var counter = 0;
  for (var i = startAt; i < endAt; i += 1) {
    var line = text[i].split(",");
    var countryName = line[0];
    var bytes = line[1];
    midRes.push({
      label: countryName,
      // label: counter,
      // megabytes
      value: parseInt(bytes)/1000000
    });
    counter++;
  }
  processedBarData.push({
    key: "Cumulative Return",
    values:  midRes
  });
}

function readBlob(opt_startByte, opt_stopByte) {

  var files = document.getElementById('files').files;
  if (!files.length) {
    alert('Please select a file!');
    return;
  }

  var file1 = files[0];
  var file2 = files[1];
  var start1 = parseInt(opt_startByte) || 0;
  var stop1 = parseInt(opt_stopByte) || file1.size - 1;
  var start2 = parseInt(opt_startByte) || 0;
  var stop2 = parseInt(opt_stopByte) || file2.size - 1;
  var reader1 = new FileReader();
  var reader2 = new FileReader();
  console.log(file1, file2, start1, stop1, start2, stop2)

    // If we use onloadend, we need to check the readyState.

    reader1.onloadend = function(evt) {
      if (evt.target.readyState == FileReader.DONE) { // DONE == 2
        pieChartBlob = evt.target.result.split("\n");
        processPieBlob(pieChartBlob);
        document.getElementById('byte_content').textContent = evt.target.result;
        document.getElementById('byte_range').textContent = 
        ['Read bytes: ', start1 + 1, ' - ', stop1 + 1,
        ' of ', file1.size, ' byte file'].join('');
      }
    };
    reader2.onloadend = function(evt) {
      if (evt.target.readyState == FileReader.DONE) { // DONE == 2
        barChartBlob = evt.target.result.split("\n");
        processChartBlob(barChartBlob);
        document.getElementById('byte_content').textContent = evt.target.result;
        document.getElementById('byte_range').textContent = 
        ['Read bytes: ', start2 + 1, ' - ', stop2 + 1,
        ' of ', file2.size, ' byte file'].join('');
      }
    };
    blob2 = file2.slice(start2, stop2 + 1);
    blob1 = file1.slice(start1, stop1 + 1);
    var pieChartData = reader2.readAsText(blob2);
    var barChartData = reader1.readAsText(blob1);
  }


  function buildCharts(pieChartData, barChartData) {
    var piedata = processedPieData;
    var barchartdata = processedBarData;


    var height = 350;
    var width = 450;
    var chart1;

    //pie chart 
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
            chart1.title(accuracy);
            chart1.pie.donutLabelsOutside(true).donut(true);
            d3.select("#piechart")
            .datum(piedata)
            .transition().duration(1200)
            .call(chart1);
            return chart1;
          });

//bar chart
nv.addGraph(function() {
  var chart = nv.models.discreteBarChart()
  .x(function(d) { return d.label })
  .y(function(d) { return d.value })
  .width(width)
  .height(height)
//      .staggerLabels(true)
//    .tooltips(false)
.showValues(false)

d3.select('#barchart')
.datum(barchartdata)
.transition().duration(500)
.call(chart)
;

nv.utils.windowResize(chart.update);

return chart;
});
}

function makeTitleTextVisible() {
  var className = "titleText";
  document.getElementsByClassName("hide-text")[0].className = "titleText";
  document.getElementsByClassName("hide-text")[0].className = "titleText";
}
//toggle results title text on and off 
function start()
{                
  buildCharts();
  makeTitleTextVisible();
  
  console.log("==========");
}

