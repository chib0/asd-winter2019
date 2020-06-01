function str2ab(str) {
  var buf = new ArrayBuffer(str.length*2); // 2 bytes for each char
  var bufView = new Uint16Array(buf);
  for (var i=0, strLen=str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}
    _snapshotPartHandlers = {
        timestamp: handleTimestamp,
        pose: handlePose,
        color_image: handleColorImage,
        depth_image: handleDepthImage,
        feelings: handleFeelings,
    };
function handleTimestamp(userid, snap, res) {
    document.title += ": " + (new Date(res)).toDateString()
}

function makeObjectRow(headerText, obj) {
    let hrow = document.createElement("tr");
    let vrow = document.createElement("tr");
    let header = document.createElement("th");
    header.rowSpan = 2;
    header.innerText=headerText;
    hrow.appendChild(header);
    if (!obj) {
        obj = {"No Data" : "No Data"}
    }
    Object.keys(obj).forEach((key) => {
        let td=document.createElement("td"); td.innerText=key; hrow.appendChild(td);
        td = document.createElement('td'); td.innerText=obj[key].toString(); vrow.appendChild(td); }
        );

    return [hrow,vrow]
}

function handlePose(userid, snap, res) {
    let coordinateRows = makeObjectRow('Coordinates', res.translation);
    let rotationRows = makeObjectRow('Rotation', res.rotation);
    let poseTable = document.createElement("table");
    poseTable.append(...coordinateRows, ...rotationRows);
    let poseContainer =$(".pose-container")[0];
    if (!poseContainer) {
        alert("somethint went horribly worng!");
        return
    }
    poseContainer.innerHTML += "<h5>Pose information:</h5>>";
    poseContainer.appendChild(poseTable)
}

function handleColorImage(userid, snap, res){
    let imageContainer = $(".snapshot-image-container")[0];
    if (!imageContainer) { alert("something is awfully wrong"); return;}
    if (!res) {
        imageContainer.innerHTML += "<h5>No Snpahost Image</h5>"
    }
    let im = document.createElement('img');
    im.tooltip = "Snapshot image"
    im.src = res;
    im.onerror = () => {
        imageContainer.innerHTML += "<br>Error Getting Snpahost Image<br>";
    };
    if (imageContainer) {
        imageContainer.appendChild(im)
    }
}
function handleDepthImage(userid, snap, res){
    //TODO: bson is not working as expected, not allowing me to extract the image.
    // console.log(res);
    // $.get(res).done((bson) => {
    //     console.log(BSON.deserialize(buffer.Buffer(bson)))
    // });
    // // let container = $(".snapshot-heatmap-container")[0];
    // if (container == null || container == undefined) {
    //     alert("error - could'nt find container for heatmap");
    //     return
    // }
    // renderHeatmap(res, container, 30, 30)
}
function handleFeelings(userid, snap, res){console.log(arguments)}
function startPopulateSnapshot() {
    let args = hashArgs();
    if (args.id ===undefined || args.snap === undefined) {
        alert(`user or snapshot undefined`);
        window.location = '/';
        return;
    }
    cortex.getSnapshotWithHandlers(args.id, args.snap, _snapshotPartHandlers)
}