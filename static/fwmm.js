const WIDTH = 9;
const HEIGHT = 34;

const preview = document.getElementById("preview");
const previewContext = preview.getContext("2d");

const availableWidgetList = document.getElementById("available-widget-list");
const widgetTree = document.getElementById("widget-tree");

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
        if (value["name"] != widgets[index]) {
            isChanged = true;
            return;
        }
    });
    return isChanged;
}
function handleFullUpdate(update) {
    console.log("Recieved an update!");
    console.log(update);
    if (checkWidgetDiff(update,["widgets"])) {
        widgetTree.innerHTML = "";
        update["widgets"].forEach((value, index, array) => {
            constructOneWidget(value);
        });
    }
    if (availableWidgetList.children.length != update["available"].length)
        constructAvailableWidgetList(update["available"]);

}

// Widget Tree
async function sendConfigUpdate(widgetIndex, name, newValue) {
    await getJSONFromPath("/updatewidgetconfig/" + widgetIndex + "/" + name + "/" + newValue)
}
async function createWidget(widget) {
    return await getJSONFromPath("/createwidget/" + widget)
}

widgetTree.ondragover = (event) => {event.preventDefault();}
widgetTree.ondrop = async (event) => {
    event.preventDefault();
    
    handleFullUpdate(await createWidget(event.dataTransfer.getData("widgetName")));
}

function constructOneWidget(widgetMetadata) {
    console.log("Rendering widget with metadata:")
    console.log(widgetMetadata)
    const widgetElement = document.createElement("div");

    const widgetDropdownIndicator = document.createElement("div");
    widgetDropdownIndicator.className = "widget-tree-dropdown-indicator";
    widgetElement.appendChild(widgetDropdownIndicator);

    const widgetNameIndicator = document.createElement("div");
    widgetNameIndicator.className = "widget-tree-name-indicator";
    widgetNameIndicator.innerText = widgetMetadata["name"];
    widgetElement.appendChild(widgetNameIndicator); 

    const widgetConfig = document.createElement("div");
    widgetConfig.className = "widget-tree-config";
    Object.keys(widgetMetadata["config"]).forEach((value, index, array) => {
        widgetConfig.appendChild(constructConfigItem(widgetMetadata["index"], value, widgetMetadata["config"][value]));
    })
    widgetElement.appendChild(widgetConfig);

    widgetTree.appendChild(widgetElement);

    
}

function constructConfigItem(widgetIndex, name, meta) {
    console.log(name, meta);
    const container = document.createElement("div");
    container.className = "widget-tree-config-item";

    const label = document.createElement("div");
    label.className = "widget-tree-config-item-label";
    label.innerText = name;
    container.appendChild(label);

    var input;
    switch (meta["item_type"]) {
        case 1: // Number (TODO: Make this show a range slider as well)
            input = document.createElement("input");
            input.type = "number";
            input.value = meta["value"];
            input.min = meta["minimum"];
            input.max = meta["maximum"];
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
        sendConfigUpdate(widgetIndex, name, event.target.value);
    }
    container.appendChild(input);
    return container;
}

// Layout Menu
function loadLayout() {
    const filePicker = document.createElement("input");
    filePicker.type = "file";
    filePicker.accept = ".mmw";
    filePicker.onchange = e => {
        console.log(e.target.files[0]);
    };
    filePicker.click();
}

// Preview
function drawPixel(x, y, color) {
    previewContext.fillStyle = color;
    previewContext.fillRect(x,y,1,1);
}

// Setup
fetchInitial();