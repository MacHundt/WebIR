//attr1: nr of data points, attr2: nr. of dimensions, attr3: value range
function randomData(count, nrOfDim, valueRange)
{     
    //Result should be stored in this array
    var dataPoints = new Array();     
    var dimensions = new Array(nrOfDim);
    
    maxArray = new Array();
    
    //Print your results 
    for(var j = 0; j < count; j++)
    {
        dimensions = [];
        for(var i = 0; i < nrOfDim; i++)
        {
            var randomNr = Math.floor(Math.random()*valueRange);
            dimensions[i] = randomNr;
            maxArray[i] = valueRange;             
        }
        dataPoints[j] = dimensions;        
    }
//    console.log(dataPoints.toString()) ;
    return dataPoints;
}
