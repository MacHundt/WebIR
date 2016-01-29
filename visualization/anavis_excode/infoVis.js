function start()
{                
    console.log("Creating random data...")
    //Exercise 1 - 2:
    //attr1: nr of data points, attr2: nr. of dimensions, attr3: value range
    //buildTable(randomData(40,4,30));    
    
    //Exercise 3:
    buildSmallBarCharts(randomData(40,5,10));
    console.log("==========");
}


//Use data binding to construct a common html table
function buildTable(dataPoints)
{
    console.log("constructing data table...");
    var vis = d3.select("#container");
    var table = vis.append("table");
    var tr = table.selectAll("tr").data(dataPoints)
                        .enter()                        
                        .append("tr")
    
                        
    var td = tr.selectAll("td").data(function(d){return d;})
                        .enter()
                        .append("td")                        
                        .text(function(d){return d;});
    
}

//Use data binding to construct a bar chart for each data point. Layout the single bar charts in a simple grid. There is no need for axes or text information.
function buildSmallBarCharts(dataPoints)
{
    console.log("constructing bar charts...",dataPoints.length, dataPoints[0].length);
    
//initialize some variables *********************
    //size of the screen
    screenWidth = window.innerWidth;
    screenHeight = window.innerHeight;
    //size of the single barCharts 
    barContainerWidth = 100;
    barContainerHeight = 100;
    margin = 30;
    //number of dimensions
    var nrDim = dataPoints[0].length;
    //size of the single bars
    var barSize = Math.floor(barContainerWidth/nrDim);

    var barHeightLimit = Math.floor(barSize/2);
//initialize some variables *********************
    
    
    //scale for the data values according to the size of the container
    // found the part that sets the bar's heights;
    // in the aufgabe, the charts seem to have moved the 0 point to the middle of 
    // the y-axis. also, the bars seem to be much smaller than what they appear 
    // on our screen. and more in line with a 50% reduction in scale. i'll do this by 
    // dividing the barContainerHieght by 2. 
    // and later move the bars to the middle of the y-axis to simular the new 0-point. 
    // after that, i'll have to find a way to substract the chosen box's elements 
    // from the other bars.
    // 
    // progress addendum: i can now click the boxes.
    // the idea is as follows: the onclick event will call the draw function again 
    // after applying a function to dataPoints that substracts the selected elements.
    // next step: actually get the selected points.
    // after that: figure out how to update the graphs.
    // i need to number the boxes. ?
    
    // coders log; it's 03:00, progress report; i've managed to get the on click element and subtract it from the graphs
    // encountering a problem with negative heights. solution; case distinction; case A = positive heights start at out new 0 and go up
    // while negative heights start at an offset from zero as their base line and go their absolute value in height to reach the 
    // 0 axis  - probably give them a different color if i get to it.
    // going to bed
    // done! a persistent problem was that our chosenbox would reset to 0, and after the transformation all following boxes would have [0,0,0,0,0]
    // subtracted from them.
    // the solution was to use array.splice(0) to create a new permanent array that doesn't reset.
    // woooo! 
    var yScale = d3.scale.linear().domain([ 0, maxArray[0]]).range([0,Math.ceil(barContainerHeight/2)]);
//    var yScale = d3.scale.linear().domain([ 0, maxArray[0]]).range([0,Math.ceil(barContainerHeight)]);
    
    numberOfElementsX = Math.floor(screenWidth/(barContainerWidth+margin));
    yPositionCounter = 0;
    
    var vis = d3.select("#container").append("svg").attr("width", screenWidth).attr("height", screenHeight);
    
    //data binding first step. For each data point create a group element
    var barContainer = vis.selectAll("g").data(dataPoints)
                            .enter()
                            .append("g")
                            //LAYOUT****************
                            .attr("transform",function(d,i){
                                
                                if(i > numberOfElementsX)
                                {
                                    yPositionCounter+= 1;
                                    
                                }                                
                                var xPositionIndex = (i%numberOfElementsX);
                                var yPositionIndex = Math.floor(i/numberOfElementsX);                                
                                
                                var position = "translate(" +(margin+xPositionIndex*(barContainerWidth+margin))
                                                            +","+(margin+yPositionIndex*(barContainerWidth+margin))+")";
                                //console.log(position)
                                return position;
                            //LAYOUT****************
                            });
    
                            function sub1from2(array1, array2) {
                                console.log("subbing", array1, array2)
                                for (var i = 0; i < array1.length; i++) {
                                var newVal = array1[i]- array2[i];
                                  if (newVal >= barHeightLimit) {
                                       newVal = barHeightLimit;
                                  } 
                                 array1[i] = newVal;
                              }
                              return array1;
                          }
    var subway = (function (someArray, selements) {
        var newSelements = selements.slice(0);
        // console.log("subtracting")
        // console.log(someArray.length, someArray[0].length, selements.length)
        // console.log(someArray[0].length);
        // console.log(someArray.length);
        // console.log(Math.ceil(someArray.length/someArray[0].length));
        rowsNr = someArray.length;
        //console.log(rowsNr);
        dimsNr = someArray[0].length;
        // console.log(rowsNr);
        // console.log(dimsNr);
//     for (var dim = 0; dim < dimsNr; dim++)  {
        for (var row = 0; row < rowsNr; row++) {
//                  console.log(someArray[row][dim]);
//                  well, its doing something but it's going terrible wrong.
//                  negative heights all over the place. 
//                  console.log(counter);
//                  someArray[row][dim] = (someArray[row][dim] - selements[dim]) % (barSize/2);
//                  this works! 
   
//                       barHeightLimit = Math.floor(barSize/2);
//                       console.log(barHeightLimit)
//                       var newVal = (someArray[row][dim]  - selements[dim]) % barHeightLimit;  
//                       if (newVal >= barHeightLimit) {
//                           newVal = barHeightLimit;
//                        } 
//                        console.log(newVal)

                        console.log(someArray[row])
                        someArray[row] = sub1from2(someArray[row], newSelements);
// //                 counter++;
                
 //                 console.log(someArray[row][dim]);
            }
//       console.log(someArray.toString());
       return someArray;
    });

    //BackgroundContainer

    barContainer.append("rect").attr("width",barContainerWidth)
                            .attr("height",barContainerHeight)
                            .attr("fill","white")
                            .attr("stroke-width",1)
                            .attr("stroke","red")
                            // http://stackoverflow.com/questions/10988213/d3-javascript-click-function-call
                            .on("click",
                               function () {
                                  //        alert("woo");
                                  //selected elements found! 
                                 var selements =  d3.select(this)[0][0].__data__;
                                 //clear d3's svg grid
                                 d3.selectAll("svg").remove();
                                 console.log(dataPoints.toString()) 
                                 var newPoints =  subway(dataPoints, selements);
                                 buildSmallBarCharts(dataPoints);
                                 console.log(dataPoints.toString()) 
                                 console.log("++++++++")                                                
                               }) ;
    //Container for the single bars
    var barChart = barContainer.append("g");

    //Plot the single bars (data binding second step). For each dimension create a rectangle
    barChart.selectAll("rect").data(function(d){return d;})
                            .enter()
                            .append("rect")
                            .attr("x", function(d,i)
                            {
                                return barSize * i;
                            })
                            //found the y-axes base line for the individual boxcharts
                            .attr("y", function(d)
                            {
                                // console.log(d);
                                // console.log(barContainerHeight);
                                // console.log(yScale(d));
                                var newZero = 0;
                                //console.log(newZero);
                                if (d >= 0)  {
                                    newZero = barContainerHeight/2- yScale(d);
                                }
                                 else {
                                     //console.log("kid's iron deficient")
                                     newZero = (barContainerHeight/2)  ;
                                 }
                                 
                                return newZero;
//                                return barContainerHeight - yScale(d);
                            })
                            .attr("width", barSize)
                            .attr("height", function(d)
                            {
                                if (d < 0)  {
                                    d = Math.abs(d);
                                }
                                return yScale(d);
                            })
                            .attr("stroke-width",1)
                            .attr("stroke","#ffffff")
                            .attr("fill", function(d) {
                             if (d < 0)  {
                                return "orange";
                            }
                            else {
                                return "blue";
                            }
                        })
                            ;
                        }
