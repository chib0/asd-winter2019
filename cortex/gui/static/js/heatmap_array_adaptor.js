// assumes someone loads heatmap.js
function renderHeatmap(data_url, container, xoffset, yoffset) {
    $.get(data_url).done((resp) => {
        resp = JSON.parse(resp);
        let points;
        try {
            points= pointsFromArray(resp, xoffset, yoffset)
        } catch (e) {
            console.error("failed to get points for heatmap: " + e.toString());
            container.innerText= "Error Presenting Image"
            return;
        }
        let width_height = `;width:${resp[0].length * 4}px;height:${resp.length * 4}px;`;
        container.style +=width_height;
        let canvas = $('.heatmap', container)[0];
        if (! canvas) {container.innerText= "Error Presenting Image"}
        canvas.style += width_height;
        makeChart(points, canvas)
    })
}

pointsFromArray = (data, xoffset, yoffset) => {
        let outData = [];
        for(let y=0; y < data.length; ++y) {
            for (let x=0; x < data[y].length; ++x) {
                let dp = {x: x + xoffset, y: y+yoffset, value: -data[y][x]};
                outData.push(dp);
            }
        }
        return outData;
    };
makeChart = (userData, canvas) => {
    console.log(userData);

    let heatmapInstance = h337.create({
        // only container is required, the rest will be defaults
        container: canvas,
         gradient: {
    // enter n keys between 0 and 1 here
    // for gradient color customization
    '-.5': 'blue',
    '-.8': 'red',
    '-.95': 'white'
  },
    });


    // heatmap data format
    let data = {
        min: -20,
        max: 0,
        data: userData
    };
    heatmapInstance.setData(data);
};