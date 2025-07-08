const WIDTH = 9;
const HEIGHT = 34;


const availableWidgetList = document.getElementById("available-widget-list");
const widgetLayout = document.getElementById("layout");
const widgetTree = document.getElementById("widget-tree");
const notificationList = document.getElementById("notification-list");

document.body.onresize = (e) => {
    widgets.forEach((value, index, array) => {
        updateLayoutObject(index, value.widgetLayoutObject, value.dimensions.width, value.dimensions.height, value.dimensions.x, value.dimensions.y, value.dimensions.rotation);
    });
}

var widgets = [];

// Helpers
async function getJSONFromPath(path) {
    const request = await fetch(path);
    const json = await request.json();
    return json

}

// Available Widget List
async function fetchInitial() {
    handleFullUpdate(await getJSONFromPath("/initial"));
}
async function constructAvailableWidgetList(available) {
    availableWidgetList.innerHTML = "";
    available.forEach((value, index, array) => {
        const widgetElement = document.createElement("div");
        widgetElement.className = "available-widget";
        widgetElement.innerText = value;
        widgetElement.draggable = true;
        widgetElement.widgetName = value;
        widgetElement.ondragstart = (event) => {event.dataTransfer.setData("widgetName", value);}
        availableWidgetList.appendChild(widgetElement);
    })
}

// Full Update
function checkWidgetDiff(newWidgetList) {
    if (newWidgetList.length != widgets.length) return true;
    var isChanged = false;
    newWidgetList.forEach((value, index, array) => {
        if (value["name"] != widgets[index]["name"]) {
            isChanged = true;
            return;
        }
    });
    return isChanged;
}
function handleFullUpdate(update, forceReloadWidgets = false) {
    console.log("Recieved an update!");
    console.log(update);
    if (forceReloadWidgets || checkWidgetDiff(update["widgets"])) {
        widgetTree.innerHTML = "";
        widgetLayout.innerHTML = "";
        widgets = []
        update["widgets"].forEach((value, index, array) => {
            widgets.push(constructOneWidget(value));
        });
    } else {
        update["widgets"].forEach((value, index, array) => {
            updateLayoutObject(index, widgets[index].widgetLayoutObject, value["size"][0], value["size"][1], value["transform"]["X"], value["transform"]["Y"], value["transform"]["Rotation"]);
        });
    }
    if (availableWidgetList.children.length != update["available"].length)
        constructAvailableWidgetList(update["available"]);

    update["notifications"].forEach((value, index, array) => {
        showNotification(value);
    })

}

function updateLayoutObject(index, layoutObject, width, height, x, y, rotation) {
    if (index != -1) {
        widgets[index].dimensions = {
                width: width,
                height: height,
                x: x,
                y: y, 
                rotation: rotation
            }
    }
    const scale = widgetLayout.offsetWidth/WIDTH;
    
    width *= scale;
    height *= scale;
    x *= scale;
    y *= scale;
    if (((rotation / 90) % 2) != 0) {
        const temp = width;
        width = height;
        height = temp;
    }
    layoutObject.style.top = y + "px";
    layoutObject.style.left = x + "px";
    layoutObject.style.width = width + "px";
    layoutObject.style.height = height + "px";

    
}

function showNotification(text) {
    const notificationElement = document.createElement("div");
    notificationElement.className = "notification";
    notificationElement.innerText = text;
    notificationList.appendChild(notificationElement);

    notificationElement.onclick = (event) => {
        notificationElement.classList.remove("showing");
        setTimeout(() => {notificationElement.remove();}, 500);
    }
    setTimeout(notificationElement.onclick, 5000);
    notificationElement.classList.add("showing");
}

// Widget Tree
async function sendConfigUpdate(widgetIndex, name, newValue) {
    handleFullUpdate(await getJSONFromPath("/updatewidgetconfig/" + widgetIndex + "/" + name + "/" + newValue));
}
async function sendTransformUpdate(widgetIndex, name, newValue) {
    handleFullUpdate(await getJSONFromPath("/updatewidgettransform/" + widgetIndex + "/" + name + "/" + newValue));
}
async function sendColorUpdate(widgetIndex, newValue) {
    await getJSONFromPath("/updatewidgetcolor/" + widgetIndex + "/" + newValue);
}
async function sendDeleteUpdate(widgetIndex) {
    handleFullUpdate(await getJSONFromPath("/deletewidget/" + widgetIndex));
}
async function updateNow() {
    handleFullUpdate(await getJSONFromPath("/updatenow"));
}
async function createWidget(widget) {
    return await getJSONFromPath("/createwidget/" + widget)
}

widgetTree.ondragover = (event) => {event.preventDefault();}
widgetTree.ondrop = async (event) => {
    event.preventDefault();
    
    handleFullUpdate(await createWidget(event.dataTransfer.getData("widgetName")));
}

function componentToHex(c) {
  let hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}
function rgbToHex(r, g, b) {
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function constructOneWidget(widgetMetadata) {
    console.log("Rendering widget with metadata:")
    console.log(widgetMetadata)
    const widgetElement = document.createElement("div");
    widgetElement.className = "widget-tree-widget-container";

    const widgetHeader = document.createElement("div");
    widgetHeader.className = "widget-tree-header";
    widgetElement.appendChild(widgetHeader);

    const widgetNameIndicator = document.createElement("div");
    widgetNameIndicator.className = "widget-tree-name-indicator";
    widgetNameIndicator.innerText = widgetMetadata["name"];
    widgetHeader.appendChild(widgetNameIndicator); 

    const widgetDel = document.createElement("button");
    widgetDel.className = "delete";
    widgetDel.innerText = "Delete";
    widgetDel.onclick = (event) => {

        sendDeleteUpdate(widgetMetadata["index"]);
    }
    widgetHeader.appendChild(widgetDel);

    const color = widgetMetadata["color"];
    const colorHex = rgbToHex(color[0], color[1], color[2])
    const widgetColor = document.createElement("input");
    widgetColor.type = "color";
    widgetColor.value = colorHex;
    widgetHeader.appendChild(widgetColor);

    const widgetTransform = document.createElement("div");
    widgetTransform.className = "widget-tree-transform";

    const widgetTransformHeader = document.createElement("div");
    widgetTransformHeader.className = "widget-header";
    widgetTransformHeader.innerText = "Transform";
    widgetElement.appendChild(widgetTransformHeader);

    widgetTransform.appendChild(constructConfigItem(widgetMetadata["index"], "X", {
        "item_type": 1,
        "value": widgetMetadata["transform"]["X"],
        "minimum": 0,
        "maximum": 10
    },
    true))
    widgetTransform.appendChild(constructConfigItem(widgetMetadata["index"], "Y", {
        "item_type": 1,
        "value": widgetMetadata["transform"]["Y"],
        "minimum": 0,
        "maximum": 35
    },
    true))
    widgetTransform.appendChild(constructConfigItem(widgetMetadata["index"], "Rotation", {
        "item_type": 6,
        "value": widgetMetadata["transform"]["Rotation"],
        "options": [0, 90, 180, 270]
    },
    true))
    widgetElement.appendChild(widgetTransform);

    const widgetConfig = document.createElement("div");
    widgetConfig.className = "widget-tree-config";

    const widgetConfigHeader = document.createElement("div");
    widgetConfigHeader.className = "widget-header";
    widgetConfigHeader.innerText = "Configuration";
    widgetElement.appendChild(widgetConfigHeader);

    Object.keys(widgetMetadata["config"]).forEach((value, index, array) => {
        widgetConfig.appendChild(constructConfigItem(widgetMetadata["index"], value, widgetMetadata["config"][value], false));
    })
    widgetElement.appendChild(widgetConfig);

    widgetTree.appendChild(widgetElement);

    const widgetLayoutObject = document.createElement("div");
    widgetLayoutObject.className = "widget-layout-object";
    updateLayoutObject(-1, widgetLayoutObject, widgetMetadata["size"][0], widgetMetadata["size"][1], widgetMetadata["transform"]["X"], widgetMetadata["transform"]["Y"], widgetMetadata["transform"]["Rotation"]);
    widgetLayoutObject.style.backgroundColor = colorHex;

    widgetColor.onchange = (event) => {
        const newColor = widgetColor.value;
        widgetLayoutObject.style.backgroundColor = newColor;
        sendColorUpdate(widgetMetadata["index"], newColor.replace("#", ""));
    }
    
    widgetLayout.appendChild(widgetLayoutObject);

    return {
        name: widgetMetadata["name"],
        widgetLayoutObject: widgetLayoutObject,
        widgetElement: widgetElement,
        dimensions: {
            width: widgetMetadata["size"][0],
            height: widgetMetadata["size"][1],
            x: widgetMetadata["transform"]["X"],
            y: widgetMetadata["transform"]["Y"], 
            rotation: widgetMetadata["transform"]["Rotation"]
        }
    }
}

function constructConfigItem(widgetIndex, name, meta, isTransform) {
    console.log(name, meta);
    const container = document.createElement("div");
    container.className = "widget-tree-config-item";

    const label = document.createElement("div");
    label.className = "widget-tree-config-item-label";
    label.innerText = name;
    container.appendChild(label);

    var input;
    var innerInput = undefined;
    switch (meta["item_type"]) {
        case 1: // Number (TODO: Make this show a range slider as well)
            input = document.createElement("input");
            input.type = "number";
            input.value = meta["value"];
            input.min = meta["minimum"];
            input.max = meta["maximum"];

            innerInput = document.createElement("input");
            innerInput.className = "number-input-slider";
            innerInput.type = "range";
            innerInput.min = meta["minimum"];
            innerInput.max = meta["maximum"];
            innerInput.value = meta["value"];
            console.log(name, meta["value"]);
            innerInput.onchange = (event) => {
                input.value = innerInput.value;
                input.onchange(undefined);
            };

            const incDecContainer = document.createElement("div");
            incDecContainer.className = "number-inc-dec-container";

            incButton = document.createElement("button");
            incButton.className = "number-inc-button";
            incButton.onclick = (event) => {input.value = Number(input.value) + 1; input.onchange(undefined);}
            incButton.innerText = "⮝"
            incDecContainer.appendChild(incButton);

            decButton = document.createElement("button");
            decButton.className = "number-dec-button";
            decButton.onclick = (event) => {input.value = Number(input.value) - 1; input.onchange(undefined);}
            decButton.innerText = "⮟"
            incDecContainer.appendChild(decButton);

            container.appendChild(innerInput);
            container.appendChild(incDecContainer);
            break;
        case 5:
            input = document.createElement("input");
            input.type = "checkbox";
            input.value = meta["value"];
            break;
        case 6: // Dropdown
            input = document.createElement("select");
            meta["options"].forEach((value, index, array) => {
                const option = document.createElement("option");
                option.value = value;
                option.innerText = value;
                if (value == meta["value"]) option.selected = true;
                input.appendChild(option);
            })
            break;
        default:
            input = document.createElement("div");
            input.innerText = "Unsupported item type!";
            break;
    }
    input.className = "widget-tree-config-item-input";
    input.onchange = (event) => {
        if (meta["item_type"] == 1) {
            console.log(meta, Number(input.value))
            if (Number(input.value) > meta["maximum"]) {
                input.value = meta["maximum"];
                return;
            }
            else if (Number(input.value) < meta["minimum"]) {
                input.value = meta["minimum"];
                return;
            }
        }
        if (innerInput) {innerInput.value = input.value}
        if (!isTransform) sendConfigUpdate(widgetIndex, name, input.value);
        else sendTransformUpdate(widgetIndex, name, input.value);
    }
    container.appendChild(input);
    return container;
}

// Layout Menu
async function loadLayout() {
    handleFullUpdate(await getJSONFromPath("/loadlayout"), true);
}
function saveLayout() {
    fetch("/savelayout");
}
function setDefaultLayout() {
    fetch("/setdefaultlayout");
}
async function addToStartup() {
    result = (await getJSONFromPath("/addtostartup"))["result"];
    showNotification(result);
}
async function removeFromStartup() {
    result = (await getJSONFromPath("/removefromstartup"))["result"];
    showNotification(result);
}
function stopServer() {
    document.body.innerHTML = "<div class='centered'><h1>FWMM is shutting down.</h1><h4>You may close this tab.</h4></div>"
    fetch("/stop");
}

// Setup
fetchInitial();